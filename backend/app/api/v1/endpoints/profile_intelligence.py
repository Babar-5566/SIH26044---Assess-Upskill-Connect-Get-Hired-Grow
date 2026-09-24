from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.response import success
from app.db.session import get_db
from app.models import ProfileResumeAnalysis, InternshipPosting
from app.schemas.profile_intelligence import JobMatchRequest, ProfileChatRequest
from app.services.profile_context import active_resume, profile_snapshot
from app.services.profile_matching import match_job, learning_suggestions
from app.services.profile_chat import chat_profile
from app.services.profile_routing import recorded_topic_names
from app.services.profile_worker import enqueue_resume

router = APIRouter(prefix="/profile-intelligence", tags=["Profile AI"])
student = require_roles("STUDENT")


@router.get("")
def overview(db: Session = Depends(get_db), user=Depends(student)):
    snapshot = profile_snapshot(db, user.id)
    # Link metadata is separate from the personal evidence used for chat.
    snapshot["learning_resources"] = learning_suggestions(
        db, recorded_topic_names(snapshot), getattr(user, "active_organization_id", None),
    )
    return success(snapshot)


@router.post("/refresh", status_code=202)
def refresh(db: Session = Depends(get_db), user=Depends(student)):
    document = active_resume(db, user.id)
    if document:
        job = db.query(ProfileResumeAnalysis).filter_by(document_id=document.id).with_for_update().first()
        if job is None:
            job = enqueue_resume(db, document)
        if job.status not in {"PENDING", "PROCESSING"}:
            job.status, job.attempts = "PENDING", 0
            job.error_message, job.result, job.chunks, job.content_hash, job.lease_token = None, None, None, None, None
        db.commit()
    return success(profile_snapshot(db, user.id))


@router.get("/jobs")
def jobs(db: Session = Depends(get_db), user=Depends(student)):
    rows = db.query(InternshipPosting).filter(InternshipPosting.status == "open",
        InternshipPosting.type.in_(["job", "full_time", "graduate_opportunity"])).order_by(InternshipPosting.posted_at.desc()).limit(100).all()
    return success([{"id": str(row.id), "title": row.title, "company_name": row.company_name,
                     "required_skills": row.required_skills or []} for row in rows])


@router.post("/job-match")
def job_match(payload: JobMatchRequest, db: Session = Depends(get_db), user=Depends(student)):
    return success(match_job(db, profile_snapshot(db, user.id), payload, getattr(user, "active_organization_id", None)))


@router.post("/chat")
async def chat(payload: ProfileChatRequest, db: Session = Depends(get_db), user=Depends(student)):
    return success(await chat_profile(db, user, payload))
