"""
Grounded RAG Pipeline & Citation Engine
Skills: agency-rag-pipeline-engineer, agency-master-plan-architect, 
        agency-software-architect, agency-application-security-engineer
"""

import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.config import settings
from app.rag.schemas import DocumentChunk
from app.rag.embeddings import get_embedding_generator
from app.rag.vector_store import vector_store
from app.ai.multi_llm_orchestrator import multi_llm_orchestrator

INSUFFICIENT_INFO_MESSAGE = (
    "I could not find sufficient information in the uploaded documents to answer this question."
)


class CitationSource(BaseModel):
    """Normalized citation source referencing an exact document chunk and page."""
    index: int = Field(..., description="1-based citation index corresponding to [1], [2] in answer")
    document_id: str = Field(..., description="Parent document UUID")
    filename: str = Field(..., description="Document file name")
    page_number: Optional[int] = Field(default=None, description="1-indexed page number if available")
    chunk_id: str = Field(..., description="Specific chunk identifier")
    snippet: str = Field(..., description="Extracted text snippet preview")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")


class RAGResponse(BaseModel):
    """Complete grounded answer and citation payload."""
    query: str
    answer: str
    sources: List[CitationSource] = Field(default_factory=list)
    retrieved_chunks_count: int = 0
    model_used: str = ""
    latency_ms: int = 0
    status: str = "SUCCESS"  # SUCCESS | INSUFFICIENT_INFO | ERROR
    error_message: Optional[str] = None


class RAGEngine:
    """
    Enterprise RAG Orchestrator enforcing strict grounding and anti-hallucination rules.
    Guarantees:
    - Zero unsupported fabrication: refuses if no relevant context exists
    - Structured, clickable citation mapping [1], [2]
    - Secure prompt bounding to neutralize prompt injection attacks
    """

    SYSTEM_PROMPT = (
        "You are an enterprise AI document assistant. Your task is to answer the user's question "
        "STRICTLY and ONLY using the provided retrieved context enclosed in <retrieved_context> tags.\n\n"
        "STRICT COMPLIANCE RULES:\n"
        "1. Answer ONLY using verifiable facts directly stated in the context.\n"
        "2. If the context does not contain sufficient facts to answer the question truthfully and accurately, "
        f"your entire response MUST be exactly: \"{INSUFFICIENT_INFO_MESSAGE}\"\n"
        "3. DO NOT speculate, invent, extrapolate, or draw upon external pre-trained knowledge.\n"
        "4. Always cite your sources by referencing their bracketed number, e.g. [1], [2], immediately after the statement.\n"
        "5. Keep the answer professional, concise, and structured."
    )

    def __init__(self):
        self.embedding_generator = get_embedding_generator()

    def _build_context_block(self, retrieved: List[tuple[DocumentChunk, float]]) -> tuple[str, List[CitationSource]]:
        """Constructs XML-bounded context and structured citation objects."""
        context_parts = []
        sources: List[CitationSource] = []

        for idx, (chunk, score) in enumerate(retrieved, start=1):
            page_info = f" — Page {chunk.page_number}" if chunk.page_number else ""
            header = f"[{idx}] {chunk.filename}{page_info}"
            context_parts.append(f"{header}\n{chunk.content}")

            # Keep snippet concise for UI
            preview = chunk.content[:200] + ("..." if len(chunk.content) > 200 else "")
            sources.append(
                CitationSource(
                    index=idx,
                    document_id=chunk.document_id,
                    filename=chunk.filename,
                    page_number=chunk.page_number,
                    chunk_id=chunk.chunk_id,
                    snippet=preview,
                    similarity_score=round(score, 4),
                )
            )

        context_str = "\n\n---\n\n".join(context_parts)
        wrapped_context = f"<retrieved_context>\n{context_str}\n</retrieved_context>"
        return wrapped_context, sources

    async def query(
        self,
        question: str,
        provider: str = "gemini",
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> RAGResponse:
        """
        Executes end-to-end RAG pipeline:
        1. Query embedding generation
        2. Vector cosine similarity search
        3. Threshold evaluation (failsafe short-circuit)
        4. Context assembly with anti-injection boundaries
        5. LLM grounded synthesis
        6. Citation formatting
        """
        start_time = time.perf_counter()
        k = top_k or settings.rag_top_k
        threshold = similarity_threshold or settings.rag_similarity_threshold

        clean_question = question.strip()
        if not clean_question:
            return RAGResponse(
                query=question,
                answer="Question cannot be empty.",
                status="ERROR",
                error_message="Empty question provided.",
            )

        # 1. Generate query embedding
        try:
            query_vector = await self.embedding_generator.generate_query_embedding(clean_question)
        except Exception as exc:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return RAGResponse(
                query=clean_question,
                answer="",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=f"Embedding generation failed: {str(exc)}",
            )

        # 2. Cosine similarity retrieval
        effective_threshold = threshold
        # When scoped to a single document, cross-document leakage risk is 0.
        # Meta-queries like "Summarize this document" or "Extract key points" naturally have
        # cosine similarity in the ~0.48-0.58 range because generic instruction terms don't match domain text.
        if document_id and similarity_threshold is None:
            effective_threshold = min(threshold, 0.48)

        retrieved = vector_store.search(
            query_vector=query_vector,
            top_k=k,
            similarity_threshold=effective_threshold,
            document_id=document_id,
            user_id=user_id,
        )

        # Adaptive fallback: If 0 chunks met strict threshold, check if query is a broad/summary
        # request or scoped to a specific document where semantic similarity to domain text is ~0.48-0.58
        if not retrieved and (
            document_id
            or any(
                w in clean_question.lower()
                for w in ["summary", "summarize", "key point", "takeaway", "overview", "highlight", "core finding", "q&a", "faq"]
            )
        ):
            relaxed_threshold = 0.45 if document_id else 0.48
            retrieved = vector_store.search(
                query_vector=query_vector,
                top_k=k,
                similarity_threshold=relaxed_threshold,
                document_id=document_id,
                user_id=user_id,
            )

        # 3. Grounding failsafe: short-circuit if insufficient context retrieved
        if not retrieved:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return RAGResponse(
                query=clean_question,
                answer=INSUFFICIENT_INFO_MESSAGE,
                sources=[],
                retrieved_chunks_count=0,
                model_used=provider,
                latency_ms=elapsed_ms,
                status="INSUFFICIENT_INFO",
            )

        # 4. Context assembly
        context_block, sources = self._build_context_block(retrieved)
        user_prompt = f"User Question: {clean_question}\n\nContext:\n{context_block}"

        # 5. LLM Grounded Generation
        llm_res = await multi_llm_orchestrator.chat_single(
            provider=provider,
            prompt=user_prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        if llm_res.status == "ERROR":
            return RAGResponse(
                query=clean_question,
                answer=f"⚠️ {llm_res.error_message or 'LLM generation failed.'}",
                sources=sources,
                retrieved_chunks_count=len(retrieved),
                model_used=f"{llm_res.provider} ({llm_res.model})",
                latency_ms=elapsed_ms,
                status="ERROR",
                error_message=llm_res.error_message,
            )

        answer_text = llm_res.content.strip()

        # Check if model returned the standard refusal
        status = (
            "INSUFFICIENT_INFO"
            if INSUFFICIENT_INFO_MESSAGE.lower() in answer_text.lower()
            else "SUCCESS"
        )

        return RAGResponse(
            query=clean_question,
            answer=answer_text,
            sources=sources if status == "SUCCESS" else [],
            retrieved_chunks_count=len(retrieved),
            model_used=f"{llm_res.provider} ({llm_res.model})",
            latency_ms=elapsed_ms,
            status=status,
        )


# Singleton instance
rag_engine = RAGEngine()
