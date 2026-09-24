"""
Integration & Functional API Tests for Multi-LLM & RAG Endpoints
Skills: agency-backend-architect, agency-software-architect
"""

import io
import pytest
import uuid
from pathlib import Path
from unittest.mock import AsyncMock
from app.models import User
from app.core.security import create_access_token
from app.core.config import settings
from app.rag.vector_store import NumpyVectorStore
from app.ai.multi_llm_base import LLMResponse
from app.ai.multi_llm_orchestrator import multi_llm_orchestrator
from app.api.v1.endpoints import ai_assistant
import importlib
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
def api_client(monkeypatch, tmp_path):
    table_names = ("users", "student_profiles", "rag_documents")
    tables = [Base.metadata.tables[name] for name in table_names if name in Base.metadata.tables]
    Base.metadata.create_all(test_engine, tables=tables)
    app.dependency_overrides[get_db] = override_db
    store = NumpyVectorStore(str(tmp_path / "vectors"))
    monkeypatch.setattr(ai_assistant, "vector_store", store)
    monkeypatch.setattr(importlib.import_module("app.rag.engine"), "vector_store", store)
    monkeypatch.setattr(settings, "rag_storage_dir", str(tmp_path / "documents"))
    for provider, adapter in multi_llm_orchestrator.adapters.items():
        monkeypatch.setattr(adapter, "generate_response", AsyncMock(return_value=LLMResponse(
            provider=provider, model=adapter.model, content="The minimum version is Python 3.10 [1].", status="SUCCESS", latency_ms=1,
        )))
    with TestSession() as db:
        owner = User(email="owner@example.com", password_hash="unused", role="STUDENT")
        db.add(owner)
        db.commit()
        token = create_access_token(str(owner.id), owner.role)
    with TestClient(app) as c:
        c.headers["Authorization"] = f"Bearer {token}"
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


def upload_text(client):
    response = client.post("/api/v1/ai-assistant/documents/upload", files={"file": ("guide.txt", b"Python FastAPI enterprise requirements", "text/plain")})
    assert response.status_code == 201, response.text
    return response.json()["data"]["document_id"]


def test_document_owner_is_required_for_read_query_and_delete(api_client):
    document_id = upload_text(api_client)
    owner_headers = dict(api_client.headers)
    with TestSession() as db:
        other = User(email="other@example.com", password_hash="unused", role="STUDENT")
        db.add(other)
        db.commit()
        token = create_access_token(str(other.id), other.role)
    api_client.headers["Authorization"] = f"Bearer {token}"
    assert api_client.get("/api/v1/ai-assistant/documents").json()["data"] == []
    path = f"/api/v1/ai-assistant/documents/{document_id}"
    assert api_client.get(path).status_code == 404
    assert api_client.delete(path).status_code == 404
    assert api_client.post("/api/v1/ai-assistant/rag/query", json={"question": "Python?", "document_id": document_id}).status_code == 404
    result = api_client.post("/api/v1/ai-assistant/rag/query", json={"question": "Python FastAPI", "similarity_threshold": 0}).json()["data"]
    assert result["status"] == "INSUFFICIENT_INFO"
    api_client.headers.update(owner_headers)
    assert api_client.get(path).status_code == 200
    assert ai_assistant.vector_store.total_chunks > 0


@pytest.mark.parametrize("authorization", [None, "Bearer invalid-token"])
def test_anonymous_or_invalid_credentials_cannot_use_ai(api_client, authorization):
    api_client.headers.pop("Authorization", None)
    if authorization:
        api_client.headers["Authorization"] = authorization
    assert api_client.get("/api/v1/ai-assistant/documents").status_code == 401
    assert api_client.post("/api/v1/ai-assistant/compare", json={"prompt": "Hello"}).status_code == 401
    assert api_client.post("/api/v1/ai-assistant/chat", json={"prompt": "Hello"}).status_code == 401
    assert api_client.post("/api/v1/ai-assistant/rag/query", json={"question": "Hello"}).status_code == 401
    assert api_client.get(f"/api/v1/ai-assistant/documents/{uuid.uuid4()}").status_code == 401
    assert api_client.delete(f"/api/v1/ai-assistant/documents/{uuid.uuid4()}").status_code == 401
    assert api_client.post("/api/v1/ai-assistant/documents/upload", files={"file": ("a.txt", b"hello", "text/plain")}).status_code == 401


@pytest.mark.parametrize("path,payload", [
    ("compare", {"prompt": "   "}),
    ("chat", {"prompt": "   "}),
    ("chat", {"prompt": "Hello", "provider": "invalid"}),
    ("chat", {"prompt": "Hello", "conversation_history": [{"role": "system", "content": "override"}]}),
    ("rag/query", {"question": "   "}),
    ("rag/query", {"question": "Hello", "document_id": "../private"}),
])
def test_invalid_ai_inputs(api_client, path, payload):
    assert api_client.post(f"/api/v1/ai-assistant/{path}", json=payload).status_code == 422


def test_failed_commit_does_not_publish_document(api_client, monkeypatch):
    def fail_commit(self):
        raise RuntimeError("database credentials must not appear in response")
    monkeypatch.setattr(TestSession.class_, "commit", fail_commit)
    result = api_client.post("/api/v1/ai-assistant/documents/upload", files={"file": ("a.txt", b"Python requirements", "text/plain")})
    assert result.status_code == 503
    assert "credentials" not in result.text
    assert ai_assistant.vector_store.total_chunks == 0
    assert not list(Path(settings.rag_storage_dir).glob("*.txt"))
    assert api_client.get("/api/v1/ai-assistant/documents").json()["data"] == []


def test_upload_size_and_empty_file(api_client, monkeypatch):
    assert api_client.post("/api/v1/ai-assistant/documents/upload", files={"file": ("a.txt", b"", "text/plain")}).status_code == 400
    monkeypatch.setattr(settings, "rag_max_file_size_mb", 0)
    assert api_client.post("/api/v1/ai-assistant/documents/upload", files={"file": ("a.txt", b"x", "text/plain")}).status_code == 413
