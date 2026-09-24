"""Explainable keyword coverage, separate for the submitted resume and profile."""
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import InternshipPosting, LearningResource, Skill
from app.schemas.profile_intelligence import JobMatchRequest
from app.services.profile_context import digest, resume_chunks
from app.services.profile_extraction import SKILL_ALIASES, safe_url, skill_evidence, skill_pattern, canonical_skill


def job_target(db: Session, request: JobMatchRequest) -> dict:
    if request.job_id:
        job = db.query(InternshipPosting).filter(
            InternshipPosting.id == request.job_id, InternshipPosting.status == "open",
            InternshipPosting.type.in_(["job", "full_time", "graduate_opportunity"]),
        ).first()
        if not job:
            raise HTTPException(404, "Open job not found.")
        target = {"id": str(job.id), "title": job.title, "description": job.description or "",
                  "required_skills": list(job.required_skills or []), "requirements_origin": "job_posting",
                  "education": job.required_education, "minimum_cgpa": job.required_cgpa}
    else:
        catalog = list(SKILL_ALIASES) + [name for (name,) in db.query(Skill.name).filter(Skill.is_active.is_(True)).all()]
        names = request.required_skills or [name for name in catalog if skill_pattern(name).search(request.job_description or "")]
        target = {"id": None, "title": "Your job description", "description": request.job_description,
                  "required_skills": names, "requirements_origin": "user_confirmed" if request.required_skills else "detected_mentions",
                  "education": None, "minimum_cgpa": None}
    target["required_skills"] = list({canonical_skill(name).casefold(): name.strip() for name in target["required_skills"] if name.strip()}.values())
    target["version"] = digest(target)
    return target


def learning_suggestions(db: Session, skills: list[str], organization_id: UUID | None) -> list[dict]:
    visibility = LearningResource.organization_id.is_(None)
    if organization_id:
        visibility = or_(visibility, LearningResource.organization_id == organization_id)
    results = []
    for resource in db.query(LearningResource).filter(visibility).order_by(LearningResource.id).all():
        relevant = [name for name in skills if any(skill_pattern(name).fullmatch(covered) for covered in resource.skills_covered or [])]
        url = safe_url(resource.url)
        if relevant and url:
            results.append({"id": str(resource.id), "title": resource.title, "url": url, "provider": resource.provider,
                            "skills": relevant, "level": resource.target_level, "is_free": resource.is_free})
        if len(results) == 6:
            break
    return results


def match_job(db: Session, snapshot: dict, request: JobMatchRequest, organization_id=None) -> dict:
    target = job_target(db, request)
    chunks = resume_chunks(db, snapshot)
    readable = bool(snapshot["resume"] and snapshot["resume"]["status"] == "READY" and snapshot["resume"]["analysis"].get("complete_text", True))
    rows = []
    for name in target["required_skills"]:
        evidence = skill_evidence(name, chunks)
        direct = [skill["name"] for skill in snapshot["skills"] if skill_pattern(name).fullmatch(skill["name"])]
        projects = [project["title"] for project in snapshot["projects"]
                    if any(skill_pattern(name).fullmatch(tech) for tech in project.get("technologies", []))]
        rows.append({"skill": name, "resume_status": "found" if evidence else "not_found" if readable else "unknown",
                     "resume_evidence": evidence, "profile_status": "recorded" if direct or projects else "not_recorded",
                     "profile_evidence": direct + projects})
    found = sum(row["resume_status"] == "found" for row in rows)
    profile_found = sum(row["profile_status"] == "recorded" for row in rows)
    missing = [row["skill"] for row in rows if row["resume_status"] == "not_found"]
    learning_gaps = [row["skill"] for row in rows if row["profile_status"] == "not_recorded" and row["resume_status"] != "found"]
    return {
        "version": snapshot["version"], "target": target, "requirements": rows,
        "resume_coverage": {"found": found, "total": len(rows), "percent": round(found / len(rows) * 100) if rows and readable else None},
        "profile_coverage": {"found": profile_found, "total": len(rows)},
        "note": "Explicit skill keyword coverage only. Not an ATS score, proficiency assessment or hiring prediction. Education, experience and other eligibility requirements need separate review.",
        "requirements_note": "Detected mentions can include optional or negated requirements. Review the skill list before relying on coverage." if target["requirements_origin"] == "detected_mentions" else "Coverage uses the explicit required skills supplied for this target.",
        "summary": [
            f"{found} of {len(rows)} target skill mentions found in your resume." if readable and rows else "Resume coverage is unavailable until both a readable resume and target skills are available.",
            "Not found in resume: " + ", ".join(missing[:8]) + "." if missing else "Review the requirement evidence and non-skill eligibility criteria.",
            "Add truthful project evidence for relevant skills, then tailor your resume to this job.",
        ],
        "resources": learning_suggestions(db, learning_gaps, organization_id),
        "project_suggestions": [
            {"title": f"Build a small project using {name}", "skill": name,
             "description": f"Choose a problem you understand, implement it with {name}, add tests and a README, and record a measurable result. This is a suggestion, not an existing project."}
            for name in learning_gaps[:3]
        ],
    }
