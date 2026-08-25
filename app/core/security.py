from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(subject: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "role": role, "iat": datetime.now(timezone.utc), "exp": exp}, settings.secret_value, algorithm=ALGORITHM)
def decode_token(token: str):
    try: return jwt.decode(token, settings.secret_value, algorithms=[ALGORITHM], options={"require_sub": True, "require_exp": True})
    except JWTError: return None
