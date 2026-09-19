"""
Security Audit & Vulnerability Resilience Unit Tests
Skills: agency-application-security-engineer, agency-master-plan-architect
"""

import io
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.ai_assistant import sanitize_filename
from app.core.config import settings


def test_path_traversal_filename_sanitization():
    """Verify that path traversal attempts (../, ..\\) are stripped from filenames."""
    dirty_names = [
        "../../etc/passwd.txt",
        "..\\..\\windows\\system32\\config.pdf",
        "/absolute/root/path/report.docx",
        "nested/sub/dir/notes.txt",
    ]
    for name in dirty_names:
        cleaned = sanitize_filename(name)
        assert "/" not in cleaned
        assert "\\" not in cleaned
        assert ".." not in cleaned
        assert cleaned in ("passwd.txt", "config.pdf", "report.docx", "notes.txt")


def test_special_characters_filename_sanitization():
    """Verify that non-alphanumeric special characters are sanitized."""
    raw = "my<script>alert(1)</script>file*.pdf"
    cleaned = sanitize_filename(raw)
    assert "<" not in cleaned
    assert ">" not in cleaned
    assert "*" not in cleaned
    assert cleaned.endswith(".pdf")


def test_secret_hygiene_no_hardcoded_keys():
    """
    Scans Python codebase to ensure no real API keys are hardcoded in source files.
    Matches standard OpenAI (sk-proj-), Anthropic (sk-ant-), and Google keys.
    """
    backend_dir = Path(__file__).resolve().parent.parent / "app"
    forbidden_patterns = [
        re.compile(r"sk-proj-[A-Za-z0-9_\-]{30,}"),
        re.compile(r"sk-ant-[A-Za-z0-9_\-]{30,}"),
        re.compile(r"AIzaSy[A-Za-z0-9_\-]{30,}"),
    ]

    for py_file in backend_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for pattern in forbidden_patterns:
            matches = pattern.findall(content)
            assert not matches, f"Hardcoded secret detected in {py_file.name}: {matches}"


def test_file_size_limit_rejection(client):
    """Authenticated uploads exceeding the size limit are rejected."""
    registration = client.post('/api/v1/auth/register/student', json={
        'email': 'upload-limit@example.com', 'password': 'StrongPass123', 'first_name': 'Test', 'last_name': 'User',
    })
    assert registration.status_code == 201
    login = client.post('/api/v1/auth/login', json={'email': 'upload-limit@example.com', 'password': 'StrongPass123'})
    client.headers['Authorization'] = 'Bearer ' + login.json()['data']['access_token']
    oversized = b"A" * (settings.rag_max_file_size_mb * 1024 * 1024 + 1024)
    response = client.post('/api/v1/ai-assistant/documents/upload',
                           files={'file': ('huge_doc.txt', io.BytesIO(oversized), 'text/plain')})
    assert response.status_code == 413
    assert 'File exceeds maximum allowed size' in response.json()['error']['message']
