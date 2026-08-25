import re
from sqlalchemy.orm import Session
from app.models import Skill, CareerRole, StudentSkill

def analyze_resume_text(text: str, target_role: str | None, db: Session):
    normalized = text.lower()
    skills = db.query(Skill).filter(Skill.is_active.is_(True)).all()
    extracted = [s.name for s in skills if re.search(r"(?<![a-z0-9])" + re.escape(s.name.lower()) + r"(?![a-z0-9])", normalized)]
    role = db.query(CareerRole).filter(CareerRole.name.ilike(target_role)).first() if target_role else None
    required = []
    if role and getattr(role, "required_skills", None): required = role.required_skills
    missing = [name for name in required if name.lower() not in {x.lower() for x in extracted}]
    score = round((len(required) - len(missing)) / max(len(required), 1) * 100, 1) if required else None
    suggestions = []
    if not extracted: suggestions.append("Add a dedicated skills section with specific technologies.")
    if "project" not in normalized: suggestions.append("Add measurable project outcomes and links.")
    if "experience" not in normalized and "internship" not in normalized: suggestions.append("Add internship or experience details where applicable.")
    return {"target_role": target_role, "extracted_skills": extracted, "missing_skills": missing, "compatibility_percent": score, "suggestions": suggestions}
