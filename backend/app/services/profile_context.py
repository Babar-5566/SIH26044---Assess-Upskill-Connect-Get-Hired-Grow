"""Live profile facts and versioned resume evidence, always scoped to one user."""
import hashlib
import json
from copy import deepcopy
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import (StudentProfile, StudentSkill, StudentProject, StudentCertification,
                        StudentInternship, StudentAchievement, StudentDocument, ProfileResumeAnalysis, RAGDocument)
from app.services.profile_extraction import safe_url, canonical_skill, skill_evidence
from app.services.profile_worker import enqueue_resume
from app.core.config import settings


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()


def active_resume(db: Session, user_id: UUID):
    return (db.query(StudentDocument).filter_by(student_id=user_id, document_type="RESUME", is_active=True)
            .order_by(StudentDocument.uploaded_at.desc(), StudentDocument.id.desc()).first())


def record(row, fields):
    return {field: (str(value) if isinstance(value, UUID) else value.isoformat() if hasattr(value, "isoformat") else value)
            for field in fields if (value := getattr(row, field, None)) is not None}


def profile_snapshot(db: Session, user_id: UUID) -> dict:
    profile = db.get(StudentProfile, user_id)
    details = record(profile, ["first_name", "last_name", "summary", "degree", "department", "institution_name",
                               "graduation_year", "city", "state", "github_url", "linkedin_url", "portfolio_url"]) if profile else {}
    for key in ("github_url", "linkedin_url", "portfolio_url"):
        if key in details:
            details[key] = safe_url(details[key])
    skills = [
        {"id": str(row.id), "name": row.skill.name, "proficiency_level": row.proficiency_level,
         "source": row.source, "score": row.score}
        for row in db.query(StudentSkill).options(joinedload(StudentSkill.skill)).filter_by(student_id=user_id).order_by(StudentSkill.created_at, StudentSkill.id).all()
    ]
    projects = [record(row, ["id", "title", "description", "technologies", "project_url", "status"])
                for row in db.query(StudentProject).filter_by(student_id=user_id).order_by(StudentProject.created_at, StudentProject.id).all()]
    for project in projects:
        project["project_url"] = safe_url(project.get("project_url"))
        project["content_fetched"] = False
    certifications = [record(row, ["id", "name", "issuer", "issue_date", "credential_url"])
                      for row in db.query(StudentCertification).filter_by(student_id=user_id).order_by(StudentCertification.id).all()]
    internships = [record(row, ["id", "company_name", "role", "description", "start_date", "end_date"])
                   for row in db.query(StudentInternship).filter_by(student_id=user_id).order_by(StudentInternship.id).all()]
    achievements = [record(row, ["id", "title", "description"])
                    for row in db.query(StudentAchievement).filter_by(student_id=user_id).order_by(StudentAchievement.id).all()]
    document = active_resume(db, user_id)
    resume = None
    if document:
        job = db.get(ProfileResumeAnalysis, document.id)
        if job is None:
            # Covers files saved before this feature and clients using the existing upload API.
            db.query(StudentDocument).filter_by(id=document.id).with_for_update().first()
            job = enqueue_resume(db, document)
            db.commit()
        analysis = deepcopy(job.result) if job.status == "READY" and job.result else None
        if analysis:
            # A newly recorded custom skill can be recognized without re-parsing the file.
            recognized = {canonical_skill(item["name"]).casefold() for item in analysis["skills"]}
            for name in [skill["name"] for skill in skills] + [tech for project in projects for tech in project.get("technologies", [])]:
                canonical = canonical_skill(name)
                if canonical.casefold() not in recognized and (evidence := skill_evidence(canonical, job.chunks or [])):
                    analysis["skills"].append({"name": canonical, "evidence": evidence})
                    recognized.add(canonical.casefold())
            for check in analysis["quality"]["checks"]:
                if check["id"] == "skills":
                    check["passed"] = bool(analysis["skills"])
            analysis["quality"]["passed"] = sum(check["passed"] for check in analysis["quality"]["checks"])
        resume = {
            "id": str(document.id), "filename": document.file_name, "status": job.status,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "error": job.error_message, "analysis": analysis,
            "content_hash": job.content_hash if job.status == "READY" else None,
        }
    documents = [
        {"id": str(row.id), "filename": row.original_filename, "status": row.status, "chunk_count": row.chunk_count}
        for row in db.query(RAGDocument).filter_by(user_id=user_id).order_by(RAGDocument.id).all()
    ]
    data = {"profile": details, "skills": skills, "projects": projects, "certifications": certifications,
            "internships": internships, "achievements": achievements, "resume": resume, "documents": documents}
    data["version"] = digest(data)
    data["limits"] = {"resume_max_size_mb": settings.max_resume_size_mb}
    extracted = resume["analysis"]["skills"] if resume and resume["analysis"] else []
    profile_names = {canonical_skill(skill["name"]).casefold() for skill in skills}
    extracted_names = {canonical_skill(skill["name"]).casefold() for skill in extracted}
    data["suggested_skills"] = [skill for skill in extracted if canonical_skill(skill["name"]).casefold() not in profile_names]
    data["profile_only_skills"] = [skill["name"] for skill in skills if canonical_skill(skill["name"]).casefold() not in extracted_names] if resume and resume["status"] == "READY" and resume["analysis"].get("complete_text", True) else []
    education = " · ".join(str(details[key]) for key in ("degree", "department", "institution_name") if details.get(key))
    sections = resume["analysis"]["sections"] if resume and resume["analysis"] else {}
    if not education and sections.get("education"):
        education = "Resume education: " + " · ".join(line["text"] for line in sections["education"][:2])
    names = [skill["name"] for skill in skills] or [skill["name"] for skill in extracted]
    experience = []
    if projects:
        experience.append("Projects: " + ", ".join(project["title"] for project in projects[:3]) + ".")
    if internships:
        experience.append("Experience: " + ", ".join(item["role"] + " at " + item["company_name"] for item in internships[:2]) + ".")
    if not experience and sections.get("projects"):
        experience.append("Resume project details: " + " ".join(line["text"] for line in sections["projects"][:2]))
    data["summary"] = [
        education or "Add your education to complete your professional introduction.",
        ("Profile skills: " if skills else "Resume mentions: ") + ", ".join(names[:8]) + (f" (+{len(names) - 8} more)." if len(names) > 8 else "."),
        " ".join(experience)[:700] or "Add a project or experience record to complete your professional introduction.",
    ]
    if not names:
        data["summary"][1] = "No skills recorded yet. Save your skills or upload a readable resume."
    data["improvement_summary"] = [
        f"{len(extracted)} recognized skill mention(s) in the resume." if resume and resume["status"] == "READY" else "Save a readable resume to receive document feedback.",
        ("Profile skills not found in the resume: " + ", ".join(data["profile_only_skills"][:6]) + ".") if data["profile_only_skills"] else "Choose a target job to identify requirement gaps.",
        next((check["detail"] for check in resume["analysis"]["quality"]["checks"] if not check["passed"]), "Review project evidence and tailor it to your target job.") if resume and resume["analysis"] else "Upload a PDF or DOCX; analysis will run automatically.",
    ]
    return data


def resume_chunks(db: Session, snapshot: dict) -> list[dict]:
    resume = snapshot.get("resume")
    if not resume or resume["status"] != "READY":
        return []
    job = db.get(ProfileResumeAnalysis, UUID(resume["id"]))
    return job.chunks or [] if job else []


def check_version(snapshot: dict, version: str | None):
    if version and snapshot["version"] != version:
        raise HTTPException(409, "Your profile or sources changed. Refresh the analysis and ask again.")
