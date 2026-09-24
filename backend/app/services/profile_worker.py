"""Database-backed jobs with leases; pending work survives process restarts."""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.db.session import SessionLocal
from app.models import ProfileResumeAnalysis, StudentDocument, Skill
from app.services.profile_extraction import EXTRACTOR_VERSION, extract_resume

logger = logging.getLogger(__name__)


def enqueue_resume(db: Session, document: StudentDocument) -> ProfileResumeAnalysis:
    job = db.get(ProfileResumeAnalysis, document.id)
    if job is None:
        job = ProfileResumeAnalysis(document_id=document.id, student_id=document.student_id,
                                    status="PENDING", extractor_version=EXTRACTOR_VERSION)
        db.add(job)
    return job


def process_next(session_factory=SessionLocal) -> bool:
    now = datetime.now(timezone.utc)
    lease = str(uuid.uuid4())
    with session_factory() as db:
        job = (db.query(ProfileResumeAnalysis).join(StudentDocument, StudentDocument.id == ProfileResumeAnalysis.document_id)
               .filter(StudentDocument.is_active.is_(True), StudentDocument.document_type == "RESUME",
                       or_(ProfileResumeAnalysis.status == "PENDING",
                           (ProfileResumeAnalysis.status == "PROCESSING") &
                           (ProfileResumeAnalysis.leased_at < now - timedelta(minutes=5))))
               .order_by(ProfileResumeAnalysis.updated_at).with_for_update(skip_locked=True).first())
        if job is None:
            return False
        if job.attempts >= 3:
            job.status = "NEEDS_ATTENTION"
            job.error_message = "Processing was interrupted repeatedly. Retry analysis or upload a new copy."
            db.commit()
            return True
        document = db.get(StudentDocument, job.document_id)
        document_id, filename, content = str(document.id), document.file_name, document.file_data
        catalog = [name for (name,) in db.query(Skill.name).filter(Skill.is_active.is_(True)).all()]
        job.status, job.lease_token, job.leased_at = "PROCESSING", lease, now
        job.attempts += 1
        db.commit()
    try:
        if not content:
            raise ValueError("The saved resume has no readable file data. Upload a new copy.")
        result, chunks = extract_resume(content, filename, document_id, catalog)
        error = None
    except ValueError as exc:
        result, chunks, error = None, None, str(exc)
    except Exception as exc:
        logger.warning("Resume extraction failed (%s)", type(exc).__name__)
        result, chunks, error = None, None, "The resume could not be processed. Check the file and retry."
    with session_factory() as db:
        # A newer lease, refresh or deletion wins over this worker.
        job = db.query(ProfileResumeAnalysis).filter_by(document_id=uuid.UUID(document_id), lease_token=lease).with_for_update().first()
        document = db.get(StudentDocument, uuid.UUID(document_id))
        if job and document and document.is_active:
            job.status = "NEEDS_ATTENTION" if error else "READY"
            job.result, job.chunks, job.error_message = result, chunks, error
            job.content_hash = result["content_hash"] if result else None
            job.extractor_version = EXTRACTOR_VERSION
            job.lease_token = None
            db.commit()
    return True


async def worker_loop():
    while True:
        try:
            worked = await run_in_threadpool(process_next)
        except Exception as exc:
            # Never print resumes, SQL parameters or credentials.
            logger.warning("Profile analysis worker unavailable (%s). Check database migrations.", type(exc).__name__)
            worked = False
        await asyncio.sleep(0.1 if worked else 3)
