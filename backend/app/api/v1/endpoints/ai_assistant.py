"""
Enterprise Multi-LLM & Grounded RAG API Endpoints
Skills: agency-backend-architect, agency-rag-pipeline-engineer, 
        agency-application-security-engineer, agency-software-architect
"""

import uuid
import os
import re
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.response import success
from app.core.security import decode_token
from app.api.deps import bearer
from app.models import User
from app.models.rag_document import RAGDocument
from app.ai.multi_llm_orchestrator import multi_llm_orchestrator
from app.rag.parsers import parse_document
from app.rag.chunker import RecursiveTextChunker
from app.rag.embeddings import get_embedding_generator
from app.rag.vector_store import vector_store
from app.rag.engine import rag_engine
from app.schemas.ai_assistant import (
    CompareRequest,
    ChatRequest,
    RAGQueryRequest,
    DocumentUploadResponse,
    DocumentListItem,
)

router = APIRouter(prefix="/ai-assistant", tags=["Enterprise Multi-LLM & RAG Assistant"])


def get_optional_user(credentials=Depends(bearer), db: Session = Depends(get_db)) -> Optional[User]:
    """Resolves current user if token is provided; otherwise returns None gracefully."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if not payload or not payload.get("sub"):
            return None
        user_id = uuid.UUID(str(payload["sub"]))
        return db.get(User, user_id)
    except Exception:
        return None


def sanitize_filename(name: str) -> str:
    """Strips directory traversal components and non-safe characters.

    Works cross-platform: replaces both forward and backslash separators
    before extracting the basename, then removes any residual '..' segments.
    """
    # Normalise both slash styles to a common separator, then take basename
    clean = name.replace("\\", "/")
    clean = clean.split("/")[-1]          # equivalent to basename on all platforms
    # Remove any residual '..' left after basename extraction
    clean = re.sub(r"\.{2,}", "", clean)
    # Strip non-safe characters (allow word chars, single dot, hyphen, space)
    clean = re.sub(r"[^\w.\- ]", "_", clean)
    return clean[:200]


# ─── Multi-LLM Comparison & Continuation ─────────────────────────────────────

@router.post("/compare")
async def compare_models(payload: CompareRequest):
    """
    Parallel Multi-LLM Arena: Dispatches the user prompt simultaneously to
    OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), and Google (Gemini).
    Returns responses side-by-side with latency (ms) and error containment.
    """
    responses = await multi_llm_orchestrator.compare_all(
        prompt=payload.prompt,
        system_prompt=payload.system_prompt,
    )
    return success([r.model_dump() for r in responses])


@router.post("/chat")
async def chat_single_model(payload: ChatRequest):
    """
    Continue conversation with a designated single model with conversation memory.
    """
    response = await multi_llm_orchestrator.chat_single(
        provider=payload.provider,
        prompt=payload.prompt,
        system_prompt=payload.system_prompt,
        conversation_history=payload.conversation_history,
    )
    return success(response.model_dump())


@router.get("/models")
async def list_available_models():
    """
    Returns the configured status and active models for OpenAI, Claude, and Gemini.
    """
    statuses = multi_llm_orchestrator.get_providers_status()
    return success(statuses)


# ─── Document Ingestion & Management ──────────────────────────────────────────

@router.post("/documents/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Ingests PDF, DOCX, or TXT document:
    1. Validates file extension and size (<= 25MB).
    2. Sanitizes filename and writes to storage/rag_documents.
    3. Extracts text preserving page/section pointers.
    4. Recursively splits text into overlapping chunks.
    5. Computes vector embeddings in batches.
    6. Persists vectors to NumPy index and registers metadata.
    """
    orig_filename = sanitize_filename(file.filename or "uploaded_document.txt")
    ext = os.path.splitext(orig_filename)[1].lower()

    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed extensions: .pdf, .docx, .txt",
        )

    # Read bytes with size ceiling
    max_bytes = settings.rag_max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {settings.rag_max_file_size_mb} MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    doc_id = str(uuid.uuid4())

    # Save to disk
    upload_dir = Path(settings.rag_storage_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / f"{doc_id}_{orig_filename}"
    with open(saved_path, "wb") as f:
        f.write(content)

    # Parse document
    try:
        parsed_doc = parse_document(content, orig_filename, doc_id)
    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Document parsing failed: {str(exc)}")

    # Chunk document
    chunker = RecursiveTextChunker(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )
    chunks = chunker.chunk_document(parsed_doc)

    if not chunks:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="No readable text chunks could be extracted from document.")

    # Tag user_id in chunk metadata if available
    if user:
        for c in chunks:
            c.metadata["user_id"] = str(user.id)

    # Generate embeddings
    emb_gen = get_embedding_generator()
    try:
        embeddings = await emb_gen.generate_embeddings([c.content for c in chunks])
    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=f"Embedding generation failed: {str(exc)}")

    # Add to Vector Store
    vector_store.add_chunks(chunks, embeddings)

    # Persist in DB
    user_uuid = user.id if user else None
    try:
        db_doc = RAGDocument(
            id=uuid.UUID(doc_id),
            user_id=user_uuid,
            original_filename=orig_filename,
            storage_path=str(saved_path),
            file_type=ext.lstrip("."),
            file_size_bytes=len(content),
            chunk_count=len(chunks),
            status="READY",
        )
        db.add(db_doc)
        db.commit()
    except Exception:
        # DB error shouldn't block RAG retrieval if vector store succeeded
        db.rollback()

    response_payload = DocumentUploadResponse(
        document_id=doc_id,
        original_filename=orig_filename,
        file_type=ext.lstrip("."),
        file_size_bytes=len(content),
        chunk_count=len(chunks),
        status="READY",
        message="Document successfully processed and indexed for RAG queries.",
    )
    return success(response_payload.model_dump())


@router.get("/documents")
async def list_documents(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Lists all uploaded documents available in the system."""
    try:
        query = db.query(RAGDocument)
        if user:
            # If authenticated, show user's documents plus global
            query = query.filter((RAGDocument.user_id == user.id) | (RAGDocument.user_id.is_(None)))
        docs = query.order_by(RAGDocument.created_at.desc()).all()
        doc_list = [
            DocumentListItem(
                id=str(d.id),
                original_filename=d.original_filename,
                file_type=d.file_type,
                file_size_bytes=d.file_size_bytes,
                chunk_count=d.chunk_count,
                status=d.status,
                created_at=d.created_at.isoformat() if d.created_at else "",
            ).model_dump()
            for d in docs
        ]
        return success(doc_list)
    except Exception:
        # Fallback to unique documents in vector store
        seen = {}
        for c in vector_store.chunks:
            if c.document_id not in seen:
                seen[c.document_id] = {
                    "id": c.document_id,
                    "original_filename": c.filename,
                    "file_type": c.metadata.get("file_type", "unknown"),
                    "file_size_bytes": 0,
                    "chunk_count": 0,
                    "status": "READY",
                    "created_at": "",
                }
            seen[c.document_id]["chunk_count"] += 1
        return success(list(seen.values()))


@router.get("/documents/{document_id}")
async def get_document_details(
    document_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Retrieves metadata and all vectorized chunks for a specific document."""
    matching_chunks = [c for c in vector_store.chunks if c.document_id == document_id]

    doc_info = {
        "id": document_id,
        "original_filename": matching_chunks[0].filename if matching_chunks else "Document",
        "file_type": matching_chunks[0].metadata.get("file_type", "unknown") if matching_chunks else "unknown",
        "file_size_bytes": 0,
        "chunk_count": len(matching_chunks),
        "status": "READY",
        "created_at": "",
        "chunks": [c.model_dump() for c in matching_chunks],
    }

    try:
        doc_uuid = uuid.UUID(document_id)
        db_doc = db.query(RAGDocument).filter_by(id=doc_uuid).first()
        if db_doc:
            doc_info["original_filename"] = db_doc.original_filename
            doc_info["file_type"] = db_doc.file_type
            doc_info["file_size_bytes"] = db_doc.file_size_bytes
            doc_info["chunk_count"] = db_doc.chunk_count or len(matching_chunks)
            doc_info["status"] = db_doc.status
            doc_info["created_at"] = db_doc.created_at.isoformat() if db_doc.created_at else ""
    except Exception:
        pass

    if not matching_chunks and not doc_info.get("file_size_bytes"):
        raise HTTPException(status_code=404, detail="Document not found.")

    return success(doc_info)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Deletes document chunks from vector index and cleans up metadata."""
    deleted_chunks = vector_store.delete_document(document_id)

    # Delete from DB
    try:
        doc_uuid = uuid.UUID(document_id)
        db_doc = db.query(RAGDocument).filter_by(id=doc_uuid).first()
        if db_doc:
            if db_doc.storage_path and os.path.exists(db_doc.storage_path):
                try:
                    os.remove(db_doc.storage_path)
                except Exception:
                    pass
            db.delete(db_doc)
            db.commit()
    except Exception:
        db.rollback()

    return success({
        "document_id": document_id,
        "deleted_chunks": deleted_chunks,
        "message": "Document and associated vectors successfully removed.",
    })


# ─── Grounded RAG Query ───────────────────────────────────────────────────────

@router.post("/rag/query")
async def query_rag(
    payload: RAGQueryRequest,
    user: Optional[User] = Depends(get_optional_user),
):
    """
    Executes grounded RAG question answering over indexed documents:
    - Retries Top-K chunks via Cosine Similarity.
    - If no relevant context exists, strictly returns standard refusal message.
    - Answers only from context and appends structured clickable citations [1], [2].
    """
    user_id_str = str(user.id) if user else None
    response = await rag_engine.query(
        question=payload.question,
        provider=payload.provider,
        document_id=payload.document_id,
        user_id=user_id_str,
        top_k=payload.top_k,
        similarity_threshold=payload.similarity_threshold,
    )
    return success(response.model_dump())
