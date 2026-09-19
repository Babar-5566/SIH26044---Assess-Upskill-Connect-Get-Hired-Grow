import asyncio
from contextlib import asynccontextmanager, suppress
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.api.v1.router import router
from app.core.config import settings
from app.core.exceptions import validation_handler, integrity_handler, generic_handler, error_response
from app.core.middleware import AuditMiddleware, RateLimitMiddleware
@asynccontextmanager
async def lifespan(app):
    from app.services.profile_worker import worker_loop
    task = asyncio.create_task(worker_loop()) if settings.profile_analysis_worker_enabled else None
    try:
        yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

app = FastAPI(title="SkillBridge AI", debug=settings.debug, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware)
app.include_router(router, prefix="/api/v1")
app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(IntegrityError, integrity_handler)
@app.exception_handler(HTTPException)
async def http_handler(request: Request, exc: HTTPException):
    codes = {401:"UNAUTHORIZED",403:"FORBIDDEN",404:"NOT_FOUND",409:"CONFLICT",422:"VALIDATION_ERROR"}
    return error_response(codes.get(exc.status_code,"VALIDATION_ERROR"), str(exc.detail), status=exc.status_code)
app.add_exception_handler(Exception, generic_handler)
