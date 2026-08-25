from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router=APIRouter(tags=["Health"])
@router.get("/ready")
def ready(db: Session=Depends(get_db)):
 try:
  db.execute(text("SELECT 1"))
  return {"status":"ready","database":"ok"}
 except SQLAlchemyError:
  return {"status":"degraded","database":"unavailable"}
