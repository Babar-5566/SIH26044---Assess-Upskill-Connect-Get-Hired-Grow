"""
Unit tests for Grounded RAG Engine & Citation Generation
Skills: agency-rag-pipeline-engineer, agency-master-plan-architect
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.rag.engine import RAGEngine, INSUFFICIENT_INFO_MESSAGE
from app.rag.schemas import DocumentChunk
from app.ai.multi_llm_base import LLMResponse


@pytest.mark.asyncio
async def test_rag_empty_question():
    """Verify that an empty question is rejected with clear error status."""
    engine = RAGEngine()
    res = await engine.query("   ")
    assert res.status == "ERROR"
    assert "Empty question" in (res.error_message or "")


@pytest.mark.asyncio
async def test_rag_insufficient_info_fallback():
    """Verify that when no chunks meet the similarity threshold, the exact refusal phrase is returned."""
    engine = RAGEngine()
    with patch("app.rag.engine.vector_store.search", return_value=[]):
        res = await engine.query("What is the quarterly revenue of ACME Corp?")
        assert res.status == "INSUFFICIENT_INFO"
        assert res.answer == INSUFFICIENT_INFO_MESSAGE
        assert len(res.sources) == 0


def test_context_block_and_citations_building():
    """Verify that retrieved chunks are correctly assembled with XML boundaries and page numbers."""
    engine = RAGEngine()
    chunk1 = DocumentChunk(
        chunk_id="doc1_c0",
        document_id="doc1",
        chunk_index=0,
        filename="system_spec.pdf",
        page_number=3,
        content="System requires Python 3.10+ and FastAPI framework.",
    )
    chunk2 = DocumentChunk(
        chunk_id="doc2_c1",
        document_id="doc2",
        chunk_index=1,
        filename="database_spec.docx",
        page_number=None,
        content="PostgreSQL 16 is used for database storage.",
    )

    retrieved = [(chunk1, 0.9123), (chunk2, 0.8456)]
    context_str, sources = engine._build_context_block(retrieved)

    assert "<retrieved_context>" in context_str
    assert "</retrieved_context>" in context_str
    assert "[1] system_spec.pdf — Page 3" in context_str
    assert "[2] database_spec.docx" in context_str
    assert len(sources) == 2
    assert sources[0].index == 1
    assert sources[0].filename == "system_spec.pdf"
    assert sources[0].page_number == 3
    assert sources[0].similarity_score == 0.9123
    assert sources[1].index == 2
    assert sources[1].page_number is None


@pytest.mark.asyncio
async def test_rag_query_end_to_end_with_citations():
    """Verify end-to-end grounded synthesis and citation mapping."""
    engine = RAGEngine()
    chunk = DocumentChunk(
        chunk_id="spec_c0",
        document_id="spec_doc",
        chunk_index=0,
        filename="architecture.pdf",
        page_number=2,
        content="The system runs on Python 3.10+ with FastAPI.",
    )

    mock_llm_response = LLMResponse(
        provider="openai",
        model="gpt-4o",
        content="The system requires Python 3.10+ and FastAPI [1].",
        latency_ms=350,
        status="SUCCESS",
    )

    with patch("app.rag.engine.vector_store.search", return_value=[(chunk, 0.89)]):
        with patch(
            "app.rag.engine.multi_llm_orchestrator.chat_single",
            new_callable=AsyncMock,
            return_value=mock_llm_response,
        ):
            res = await engine.query("What version of Python is required?", provider="openai")

            assert res.status == "SUCCESS"
            assert "[1]" in res.answer
            assert len(res.sources) == 1
            assert res.sources[0].filename == "architecture.pdf"
            assert res.sources[0].page_number == 2
            assert res.retrieved_chunks_count == 1
