from app.db.base import Base
import app.models

def test_phase_21_23_tables_are_registered():
    expected = {"employment_outcomes", "ai_executions", "recommendations"}
    assert expected.issubset(Base.metadata.tables)

def test_documents_use_database_binary_storage():
    columns = Base.metadata.tables["student_documents"].columns
    assert "file_data" in columns
    assert "file_path" not in columns
