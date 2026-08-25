from sqlalchemy.orm import Session
from app.models import EmploymentOutcome

def create_outcome(db: Session, student_id, data: dict) -> EmploymentOutcome:
    outcome = EmploymentOutcome(student_id=student_id, **data)
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome
