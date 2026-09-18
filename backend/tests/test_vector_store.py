"""
Unit tests for Vector Store & Cosine Similarity Engine
Skill: agency-rag-pipeline-engineer, agency-software-architect
"""

import shutil
import pytest
import numpy as np
from app.rag.embeddings import DeterministicFallbackEmbeddingGenerator
from app.rag.vector_store import NumpyVectorStore
from app.rag.schemas import DocumentChunk


@pytest.fixture
def temp_vector_store(tmp_path):
    """Creates a vector store isolated in a temporary directory for each test."""
    store_dir = tmp_path / "test_vectors"
    store = NumpyVectorStore(storage_dir=str(store_dir))
    yield store
    shutil.rmtree(str(store_dir), ignore_errors=True)


@pytest.mark.asyncio
async def test_embedding_normalization():
    """Verify that generated embeddings have unit norm (norm == 1.0)."""
    generator = DeterministicFallbackEmbeddingGenerator(dimension=128)
    vecs = await generator.generate_embeddings(["Machine learning with Python", "Database indexing"])
    assert len(vecs) == 2
    for v in vecs:
        norm = np.linalg.norm(v)
        assert pytest.approx(norm, rel=1e-3) == 1.0


@pytest.mark.asyncio
async def test_add_and_search_ranking(temp_vector_store):
    """Verify that Cosine Similarity correctly ranks the most relevant chunk first."""
    generator = DeterministicFallbackEmbeddingGenerator(dimension=128)

    chunk1 = DocumentChunk(
        chunk_id="doc1_c0",
        document_id="doc1",
        chunk_index=0,
        filename="ai_guide.txt",
        page_number=1,
        content="Python and FastAPI are excellent tools for building AI microservices.",
    )
    chunk2 = DocumentChunk(
        chunk_id="doc2_c0",
        document_id="doc2",
        chunk_index=0,
        filename="cooking_recipes.txt",
        page_number=1,
        content="To make authentic Italian pasta, boil water and add sea salt.",
    )

    embeddings = await generator.generate_embeddings([chunk1.content, chunk2.content])
    temp_vector_store.add_chunks([chunk1, chunk2], embeddings)

    assert temp_vector_store.total_chunks == 2

    # Query for Python API
    query_vec = await generator.generate_query_embedding("Python FastAPI services")
    results = temp_vector_store.search(query_vec, top_k=2, similarity_threshold=0.0)

    assert len(results) >= 1
    top_chunk, top_score = results[0]
    assert top_chunk.chunk_id == "doc1_c0"
    assert "FastAPI" in top_chunk.content


@pytest.mark.asyncio
async def test_similarity_threshold_filtering(temp_vector_store):
    """Verify that chunks with similarity below threshold are excluded."""
    generator = DeterministicFallbackEmbeddingGenerator(dimension=128)

    chunk = DocumentChunk(
        chunk_id="doc1_c0",
        document_id="doc1",
        chunk_index=0,
        filename="doc.txt",
        page_number=1,
        content="Solar energy systems harness sunlight using photovoltaic panels.",
    )
    embeddings = await generator.generate_embeddings([chunk.content])
    temp_vector_store.add_chunks([chunk], embeddings)

    # Completely unrelated query with high threshold
    query_vec = await generator.generate_query_embedding("Pizza mozzarella recipe dough")
    results = temp_vector_store.search(query_vec, top_k=5, similarity_threshold=0.95)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_delete_document(temp_vector_store):
    """Verify document deletion removes only targeted chunks."""
    generator = DeterministicFallbackEmbeddingGenerator(dimension=128)

    chunk1 = DocumentChunk(chunk_id="d1_c0", document_id="doc_a", chunk_index=0, filename="a.txt", content="Doc A text")
    chunk2 = DocumentChunk(chunk_id="d2_c0", document_id="doc_b", chunk_index=0, filename="b.txt", content="Doc B text")

    embeddings = await generator.generate_embeddings([chunk1.content, chunk2.content])
    temp_vector_store.add_chunks([chunk1, chunk2], embeddings)
    assert temp_vector_store.total_chunks == 2

    deleted = temp_vector_store.delete_document("doc_a")
    assert deleted == 1
    assert temp_vector_store.total_chunks == 1
    assert temp_vector_store.chunks[0].document_id == "doc_b"


@pytest.mark.asyncio
async def test_disk_persistence(tmp_path):
    """Verify that vector store persists to disk and reloads on startup."""
    store_dir = tmp_path / "persist_test"
    generator = DeterministicFallbackEmbeddingGenerator(dimension=128)

    # First instance creates and saves
    store1 = NumpyVectorStore(storage_dir=str(store_dir))
    chunk = DocumentChunk(chunk_id="p_c0", document_id="doc_p", chunk_index=0, filename="p.txt", content="Persistent data")
    embeddings = await generator.generate_embeddings([chunk.content])
    store1.add_chunks([chunk], embeddings)
    assert store1.total_chunks == 1

    # Second instance loads from disk
    store2 = NumpyVectorStore(storage_dir=str(store_dir))
    assert store2.total_chunks == 1
    assert store2.chunks[0].chunk_id == "p_c0"
    assert store2.matrix is not None
    assert store2.matrix.shape == (1, 128)
