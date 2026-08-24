from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

def error_response(code, message, details=None, status=400):
    return JSONResponse(status_code=status, content={"success": False, "error": {"code": code, "message": message, **({"details": details} if details else {})}})
async def validation_handler(request: Request, exc: RequestValidationError): return error_response("VALIDATION_ERROR", "Validation failed", exc.errors(), 422)
async def integrity_handler(request: Request, exc: IntegrityError): return error_response("CONFLICT", "Resource already exists", status=409)
async def generic_handler(request: Request, exc: Exception): return error_response("INTERNAL_ERROR", "Internal server error", status=500)
