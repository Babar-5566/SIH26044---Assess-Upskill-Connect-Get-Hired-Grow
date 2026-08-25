from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import AIExecution
from app.ai import AIOrchestrator
from app.ai.base import ProviderError

def create_execution(db: Session, user_id, feature: str, input_data: dict | None = None) -> AIExecution:
    execution = AIExecution(user_id=user_id, feature=feature, input_data=input_data, status="PENDING")
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution

def complete_execution(db: Session, execution: AIExecution, output_data: dict) -> AIExecution:
    execution.status = "COMPLETED"
    execution.output_data = output_data
    execution.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(execution)
    return execution

def fail_execution(db: Session, execution: AIExecution, error_message: str) -> AIExecution:
    execution.status = "FAILED"; execution.error_message = error_message[:2000]
    db.commit(); db.refresh(execution); return execution

def generate(db: Session, user_id, feature: str, system_prompt: str, user_prompt: str) -> tuple[AIExecution, dict]:
    execution = create_execution(db, user_id, feature, {"prompt": user_prompt[:10000]})
    try:
        provider, model, output = AIOrchestrator().generate_json(system_prompt, user_prompt)
        execution.provider = provider; execution.model_name = model
        return complete_execution(db, execution, output), output
    except ProviderError as exc:
        fail_execution(db, execution, str(exc)); raise
