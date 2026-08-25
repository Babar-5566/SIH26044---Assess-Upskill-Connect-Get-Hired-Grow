from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.api.v1.router import router
from app.core.config import settings
from app.core.exceptions import validation_handler, integrity_handler, generic_handler, error_response
app = FastAPI(title="SkillBridge AI", debug=settings.debug)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")
app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(IntegrityError, integrity_handler)
@app.exception_handler(HTTPException)
async def http_handler(request: Request, exc: HTTPException):
    codes = {401:"UNAUTHORIZED",403:"FORBIDDEN",404:"NOT_FOUND",409:"CONFLICT",422:"VALIDATION_ERROR"}
    return error_response(codes.get(exc.status_code,"VALIDATION_ERROR"), str(exc.detail), status=exc.status_code)
app.add_exception_handler(Exception, generic_handler)
