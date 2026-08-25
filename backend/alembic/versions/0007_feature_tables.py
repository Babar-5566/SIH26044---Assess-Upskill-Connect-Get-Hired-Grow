"""materialize integrated learning, opportunity, intelligence, and domain tables"""
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.engine import Connection
from app.db.base import Base
from app import models

revision="0007_feature_tables"; down_revision="0006_mentor_assignments"; branch_labels=None; depends_on=None
TABLES={"learning_resources","learning_certifications","student_learning_plans","learning_plan_items","learning_outcomes","internship_postings","academician_opportunities","internship_applications","internship_progress","internship_mentor_feedback","employment_outcomes","ai_executions","recommendations","audit_logs","student_documents"}
def upgrade():
 bind=op.get_bind(); existing=set(inspect(bind).get_table_names())
 Base.metadata.create_all(bind=bind, tables=[t for t in Base.metadata.sorted_tables if t.name in TABLES and t.name not in existing])
def downgrade():
 bind=op.get_bind(); existing=set(inspect(bind).get_table_names())
 for t in reversed(Base.metadata.sorted_tables):
  if t.name in TABLES and t.name in existing: t.drop(bind=bind)
