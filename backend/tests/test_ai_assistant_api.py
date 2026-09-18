"""
Integration & Functional API Tests for Multi-LLM & RAG Endpoints
Skills: agency-backend-architect, agency-software-architect
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

test_engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def api_client():
    table_names = ("users", "student_profiles", "rag_documents")
    tables = [Base.metadata.tables[name] for name in table_names if name in Base.metadata.tables]
    Base.metadata.create_all(test_engine, tables=tables)
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine, tables=tables)



def test_list_models_endpoint(api_client):
    """Verify /api/v1/ai-assistant/models returns 200 and array of models."""
    response = api_client.get("/api/v1/ai-assistant/models")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    providers = [m["provider"] for m in data["data"]]
    assert "openai" in providers
    assert "claude" in providers
    assert "gemini" in providers


def test_compare_models_endpoint(api_client):
    """Verify /api/v1/ai-assistant/compare dispatches parallel query."""
    payload = {"prompt": "What is enterprise architecture?"}
    response = api_client.post("/api/v1/ai-assistant/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3
    for model_res in data["data"]:
        assert "provider" in model_res
        assert "status" in model_res
        assert "latency_ms" in model_res


def test_chat_single_endpoint(api_client):
    """Verify /api/v1/ai-assistant/chat works for single-model dialogue."""
    payload = {
        "prompt": "Hello",
        "provider": "gemini",
        "conversation_history": []
    }
    response = api_client.post("/api/v1/ai-assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["provider"] == "gemini"


def test_document_upload_and_rag_query_lifecycle(api_client):
    """Verify end-to-end: Upload -> List -> Query -> Delete."""
    doc_content = (
        "Enterprise Multi-LLM Assistant Release Notes:\n"
        "Version 2.0 introduces side-by-side comparison of OpenAI, Claude, and Gemini.\n"
        "All document citations reference exact file names and page indices.\n"
        "The minimum required Python version is Python 3.10."
    )

    # 1. Upload valid document
    file_bytes = io.BytesIO(doc_content.encode("utf-8"))
    upload_res = api_client.post(
        "/api/v1/ai-assistant/documents/upload",
        files={"file": ("release_notes.txt", file_bytes, "text/plain")},
    )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    assert upload_data["success"] is True
    doc_id = upload_data["data"]["document_id"]
    assert upload_data["data"]["chunk_count"] >= 1

    # 2. List documents
    list_res = api_client.get("/api/v1/ai-assistant/documents")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert any(d["id"] == doc_id or d["original_filename"] == "release_notes.txt" for d in list_data["data"])

    # 3. RAG Query
    query_payload = {
        "question": "What is the minimum required Python version?",
        "provider": "gemini",
        "document_id": doc_id,
        "top_k": 3,
        "similarity_threshold": 0.1,
    }
    rag_res = api_client.post("/api/v1/ai-assistant/rag/query", json=query_payload)
    assert rag_res.status_code == 200
    rag_data = rag_res.json()
    assert rag_data["success"] is True
    assert "answer" in rag_data["data"]
    assert "sources" in rag_data["data"]
    assert rag_data["data"]["retrieved_chunks_count"] >= 1


    # 4. Delete document
    del_res = api_client.delete(f"/api/v1/ai-assistant/documents/{doc_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["success"] is True
    assert del_data["data"]["document_id"] == doc_id


def test_upload_invalid_file_extension(api_client):
    """Verify rejection of non-whitelisted file types."""
    file_bytes = io.BytesIO(b"malicious script")
    upload_res = api_client.post(
        "/api/v1/ai-assistant/documents/upload",
        files={"file": ("exploit.exe", file_bytes, "application/x-msdownload")},
    )
    assert upload_res.status_code == 400
    assert "Unsupported file type" in upload_res.json()["error"]["message"]
