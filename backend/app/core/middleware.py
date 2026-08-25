import json
import logging
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.security import ALGORITHM

audit_logger = logging.getLogger("skillbridge.audit")


class InMemoryRateLimiter:
    def __init__(self):
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window: int, now: float | None = None) -> tuple[bool, int]:
        current = time.monotonic() if now is None else now
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= current - window: requests.popleft()
            if len(requests) >= limit:
                return False, max(1, int(window - (current - requests[0])))
            requests.append(current)
            return True, 0

    def clear(self) -> None:
        with self._lock: self._requests.clear()


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled or request.url.path.endswith("/health"):
            return await call_next(request)
        is_auth = request.url.path.endswith("/auth/login") or request.url.path.endswith("/auth/register/student")
        limit = settings.auth_rate_limit_requests if is_auth else settings.rate_limit_requests
        client = request.client.host if request.client else "unknown"
        allowed, retry_after = rate_limiter.check(f"{client}:{'auth' if is_auth else 'api'}", limit, settings.rate_limit_window_seconds)
        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={"success": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests"}},
            )
        return await call_next(request)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started = time.monotonic()
        response = await call_next(request)
        is_auth = "/auth/" in request.url.path
        is_mutation = request.method in {"POST", "PUT", "PATCH", "DELETE"}
        if is_auth or is_mutation:
            user_id = None
            authorization = request.headers.get("authorization", "")
            if authorization.lower().startswith("bearer "):
                try:
                    payload = jwt.decode(authorization[7:], settings.secret_value, algorithms=[ALGORITHM], options={"verify_exp": False})
                    user_id = payload.get("sub")
                except JWTError:
                    pass
            audit_event = {
                "event": "api_audit",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_id": user_id,
                "ip": request.client.host if request.client else None,
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
            }
            audit_logger.info(json.dumps(audit_event, separators=(",", ":")))
            try:
                if not settings.audit_persist_enabled:
                    return response
                from app.db.session import SessionLocal
                from app.models import AuditLog
                with SessionLocal() as db:
                    db.add(AuditLog(user_id=user_id, action=f"{request.method} {request.url.path}", entity="api", details=audit_event, ip=audit_event["ip"]))
                    db.commit()
            except Exception:
                audit_logger.exception("audit persistence failed")
        return response
