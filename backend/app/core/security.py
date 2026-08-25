from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from threading import Lock
from uuid import uuid4
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
_revoked_tokens: dict[str, float] = {}
_revocation_lock = Lock()
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "role": role, "jti": str(uuid4()), "iat": now, "exp": exp}, settings.secret_value, algorithm=ALGORITHM)
def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_value, algorithms=[ALGORITHM], options={"require_sub": True, "require_exp": True})
        jti = payload.get("jti")
        now = datetime.now(timezone.utc).timestamp()
        with _revocation_lock:
            expired = [key for key, expiry in _revoked_tokens.items() if expiry <= now]
            for key in expired: _revoked_tokens.pop(key, None)
            if jti and jti in _revoked_tokens: return None
        return payload
    except JWTError: return None

def revoke_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.secret_value, algorithms=[ALGORITHM], options={"require_sub": True, "require_exp": True})
        jti = payload.get("jti")
        if not jti: return False
        with _revocation_lock: _revoked_tokens[jti] = float(payload["exp"])
        return True
    except (JWTError, KeyError, TypeError, ValueError):
        return False

def clear_revoked_tokens() -> None:
    with _revocation_lock: _revoked_tokens.clear()
