"""Authenticated Multi-LLM and document RAG endpoints."""

import logging
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.response import success
from app.db.session import get_db
from app.models import User
from app.models.rag_document import RAGDocument
from app.ai.multi_llm_orchestrator import multi_llm_orchestrator
from app.rag.parsers import parse_document
from app.rag.chunker import RecursiveTextChunker
from app.rag.embeddings import get_embedding_generator
from app.rag.vector_store import vector_store
from app.rag.engine import rag_engine
from app.schemas.ai_assistant import CompareRequest, ChatRequest, RAGQueryRequest, DocumentUploadResponse, DocumentListItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-assistant", tags=["Enterprise Multi-LLM & RAG Assistant"], dependencies=[Depends(get_current_user)])


def sanitize_filename(name: str) -> str:
    clean = name.replace("\\", "/").split("/")[-1]
    clean = re.sub(r"\.{2,}", "", clean)
    return re.sub(r"[^\w.\- ]", "_", clean)[:200]


def owned_document(db: Session, document_id: uuid.UUID, user: User) -> RAGDocument:
    document = db.query(RAGDocument).filter_by(id=document_id, user_id=user.id).first()
    if document is None:
        raise HTTPException(404, "Document not found.")
    return document


def document_summary(document: RAGDocument) -> dict:
    return DocumentListItem(
        id=str(document.id), original_filename=document.original_filename,
        file_type=document.file_type, file_size_bytes=document.file_size_bytes,
        chunk_count=document.chunk_count, status=document.status,
        created_at=document.created_at.isoformat() if document.created_at else "",
    ).model_dump()


@router.post("/compare")
async def compare_models(payload: CompareRequest):
    responses = await multi_llm_orchestrator.compare_all(prompt=payload.prompt, system_prompt=payload.system_prompt)
    return success([response.model_dump() for response in responses])


@router.post("/chat")
async def chat_single_model(payload: ChatRequest):
    response = await multi_llm_orchestrator.chat_single(
        provider=payload.provider, prompt=payload.prompt, system_prompt=payload.system_prompt,
        conversation_history=[message.model_dump() for message in payload.conversation_history],
    )
    return success(response.model_dump())


@router.get("/models")
async def list_available_models():
    return success(multi_llm_orchestrator.get_providers_status())


@router.post("/documents/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    filename = sanitize_filename(file.filename or "uploaded_document.txt")
    extension = Path(filename).suffix.lower()
    if extension not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(400, "Unsupported file type. Allowed extensions: .pdf, .docx, .txt")

    # Bound the read even when the multipart body was already spooled to disk.
    max_bytes = settings.rag_max_file_size_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(413, f"File exceeds maximum allowed size of {settings.rag_max_file_size_mb} MB.")
    if not content:
        raise HTTPException(400, "Uploaded file is empty.")

    document_id = str(uuid.uuid4())
    try:
        parsed = await run_in_threadpool(parse_document, content, filename, document_id)
        chunks = RecursiveTextChunker(settings.rag_chunk_size, settings.rag_chunk_overlap).chunk_document(parsed)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception as exc:
        logger.warning("Document parsing failed (%s)", type(exc).__name__)
        raise HTTPException(422, "Document could not be read. Check that it is a valid, unencrypted document.") from None
    if not chunks:
        raise HTTPException(422, "No readable text could be extracted from document.")

    generator = get_embedding_generator()
    for chunk in chunks:
        chunk.metadata.update(user_id=str(user.id), embedding_space=generator.embedding_space)
    try:
        embeddings = await generator.generate_embeddings([chunk.content for chunk in chunks])
    except Exception as exc:
        logger.warning("Document embedding failed (%s)", type(exc).__name__)
        raise HTTPException(502, "Embedding service unavailable. Check provider configuration and retry.") from None

    upload_dir = Path(settings.rag_storage_dir)
    # UUID-only paths avoid reserved names and Windows path length surprises.
    saved_path = upload_dir / f"{document_id}{extension}"
    indexed = False
    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        db.add(RAGDocument(
            id=uuid.UUID(document_id), user_id=user.id, original_filename=filename,
            storage_path=str(saved_path), file_type=extension.lstrip("."),
            file_size_bytes=len(content), chunk_count=len(chunks), status="READY",
        ))
        # Detect missing migrations/constraints before publishing vectors.
        db.flush()
        saved_path.write_bytes(content)
        vector_store.add_chunks(chunks, embeddings)
        indexed = True
        db.commit()
    except Exception as exc:
        db.rollback()
        if indexed:
            vector_store.delete_document(document_id)
        saved_path.unlink(missing_ok=True)
        logger.warning("Document persistence failed (%s)", type(exc).__name__)
        message = str(exc) if isinstance(exc, ValueError) else "Document could not be saved. Check storage and database migrations, then retry."
        raise HTTPException(503, message) from None

    return success(DocumentUploadResponse(
        document_id=document_id, original_filename=filename, file_type=extension.lstrip("."),
        file_size_bytes=len(content), chunk_count=len(chunks), status="READY",
        message="Document is ready for questioning.",
    ).model_dump())


@router.get("/documents")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    documents = db.query(RAGDocument).filter_by(user_id=user.id).order_by(RAGDocument.created_at.desc()).all()
    return success([document_summary(document) for document in documents])


@router.get("/documents/{document_id}")
def get_document_details(document_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = owned_document(db, document_id, user)
    chunks = [chunk.model_dump() for chunk in vector_store.chunks
              if chunk.document_id == str(document_id) and chunk.metadata.get("user_id") == str(user.id)]
    return success({**document_summary(document), "chunks": chunks})


@router.delete("/documents/{document_id}")
async def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = owned_document(db, document_id, user)
    saved_path = Path(document.storage_path).resolve()
    storage_root = Path(settings.rag_storage_dir).resolve()
    if not saved_path.is_relative_to(storage_root) or saved_path == storage_root:
        raise HTTPException(409, "Document storage path is invalid.")
    # Authorization is complete before any file/index mutation.
    try:
        deleted_chunks = vector_store.delete_document(str(document_id))
        saved_path.unlink(missing_ok=True)
        db.delete(document)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Document deletion failed (%s)", type(exc).__name__)
        raise HTTPException(503, "Document deletion could not be completed. Please retry.") from None
    return success({"document_id": str(document_id), "deleted_chunks": deleted_chunks,
                    "message": "Document and associated vectors successfully removed."})


@router.post("/rag/query")
async def query_rag(payload: RAGQueryRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.document_id is not None:
        owned_document(db, payload.document_id, user)
    response = await rag_engine.query(
        question=payload.question, provider=payload.provider,
        document_id=str(payload.document_id) if payload.document_id else None,
        user_id=str(user.id), top_k=payload.top_k, similarity_threshold=payload.similarity_threshold,
    )
    return success(response.model_dump())
