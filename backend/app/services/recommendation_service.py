from sqlalchemy.orm import Session
from app.models import Recommendation

def create_recommendation(db: Session, student_id, recommendation_type: str, title: str, reason: str | None = None, context: dict | None = None) -> Recommendation:
    recommendation = Recommendation(student_id=student_id, recommendation_type=recommendation_type, title=title, reason=reason, context=context)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation

def create_from_ai(db: Session, student_id, output: dict, source: str) -> list[Recommendation]:
    created = []
    for item in output.get("recommendations", []):
        if not isinstance(item, dict) or item.get("type") not in {"CAREER", "LEARNING", "PROJECT", "INTERNSHIP", "JOB"}: continue
        created.append(create_recommendation(db, student_id, item["type"], str(item.get("title", "Recommendation"))[:255], str(item.get("reason", ""))[:4000], {"ai": True}))
        created[-1].source = source; created[-1].priority = max(0, min(100, int(item.get("priority", 0))))
    db.commit()
    return created

def rule_based_fallback(db: Session, student_id, context: dict) -> list[Recommendation]:
    items = []
    counts = context.get("counts", {})
    if not context.get("preferred_roles"): items.append(("CAREER", "Select preferred career roles", "Career roles help future modules compare your profile with role requirements.", 90))
    if counts.get("skills", 0) < 5: items.append(("LEARNING", "Add and strengthen core skills", "Maintain at least five relevant technical and soft skills for better matching.", 80))
    if counts.get("projects", 0) == 0: items.append(("PROJECT", "Build a role-relevant project", "A practical project provides evidence of applied skills.", 70))
    if counts.get("internships", 0) == 0: items.append(("INTERNSHIP", "Prepare for internship opportunities", "Add experience through internships, training, or live projects.", 60))
    created = [create_recommendation(db, student_id, kind, title, reason, {"fallback": True}) for kind, title, reason, _ in items]
    for row, item in zip(created, items): row.priority = item[3]; row.source = "RULE_BASED"
    db.commit()
    return created
