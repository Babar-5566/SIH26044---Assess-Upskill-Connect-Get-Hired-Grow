from io import BytesIO
from types import SimpleNamespace

import pytest

from app.core.middleware import InMemoryRateLimiter
from app.core.security import clear_revoked_tokens, create_access_token, decode_token, revoke_token
from app.services.resume_service import read_resume


def test_rate_limiter_enforces_window_and_retry_after():
    limiter = InMemoryRateLimiter()
    assert limiter.check("client", 2, 60, now=100)[0]
    assert limiter.check("client", 2, 60, now=101)[0]
    allowed, retry_after = limiter.check("client", 2, 60, now=102)
    assert not allowed
    assert retry_after >= 58
    assert limiter.check("client", 2, 60, now=161)[0]


def test_logout_revokes_jti_until_expiry():
    clear_revoked_tokens()
    token = create_access_token("00000000-0000-0000-0000-000000000001", "STUDENT")
    assert decode_token(token)
    assert revoke_token(token)
    assert decode_token(token) is None
    clear_revoked_tokens()


@pytest.mark.parametrize(
    ("filename", "payload", "content_type"),
    [
        ("resume.pdf", b"not a pdf", "application/pdf"),
        ("resume.doc", b"not a doc", "application/msword"),
        ("resume.docx", b"not a zip", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ],
)
def test_resume_rejects_extension_only_uploads(filename, payload, content_type):
    file = SimpleNamespace(filename=filename, content_type=content_type, file=BytesIO(payload))
    with pytest.raises(ValueError, match="content"):
        read_resume(file)
