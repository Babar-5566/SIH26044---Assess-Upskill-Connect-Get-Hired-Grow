import os
import tempfile
import atexit

# Test collection must never load live credentials or mutate the user's index.
_test_storage = tempfile.TemporaryDirectory(prefix="skillbridge-tests-")
atexit.register(_test_storage.cleanup)
for _key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"):
    os.environ[_key] = ""
os.environ["RAG_STORAGE_DIR"] = os.path.join(_test_storage.name, "documents")
os.environ["RAG_VECTORS_DIR"] = os.path.join(_test_storage.name, "vectors")
os.environ["DEBUG"] = "false"
os.environ["PROFILE_ANALYSIS_WORKER_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    tables = [Base.metadata.tables[name] for name in ("users", "student_profiles", "skills", "student_skills", "student_projects", "student_certifications", "student_achievements", "student_internships", "organizations", "organization_memberships") if name in Base.metadata.tables]
    Base.metadata.create_all(engine, tables=tables)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine, tables=tables)
