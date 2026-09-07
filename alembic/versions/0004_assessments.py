"""add assessment tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "0004_assessments"
down_revision = "0003_organizations_memberships"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("assessments", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("title", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("category", sa.String(40), nullable=False), sa.Column("target_role", sa.String(100)), sa.Column("target_skills", postgresql.ARRAY(sa.String), nullable=False), sa.Column("duration_minutes", sa.Integer(), nullable=False), sa.Column("total_marks", sa.Integer(), nullable=False), sa.Column("passing_marks", sa.Integer(), nullable=False), sa.Column("is_proctored", sa.Boolean(), nullable=False), sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_table("questions", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False), sa.Column("q_type", sa.String(40), nullable=False), sa.Column("difficulty", sa.String(20), nullable=False), sa.Column("skill_tag", sa.String(100), nullable=False), sa.Column("prompt", sa.Text(), nullable=False), sa.Column("options", postgresql.JSONB()), sa.Column("correct_answers", postgresql.JSONB(), nullable=False), sa.Column("explanation", sa.Text()), sa.Column("marks", sa.Integer()), sa.Column("negative_marks", sa.Numeric(3,2)))
    op.create_table("assessment_attempts", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("assessment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False), sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(30)), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("score_obtained", sa.Numeric(5,2)), sa.Column("percentage", sa.Numeric(5,2)), sa.Column("passed", sa.Boolean()), sa.Column("skill_breakdown", postgresql.JSONB()), sa.Column("tab_switches_count", sa.Integer()))
    op.create_table("assessment_responses", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("attempt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("selected_options", postgresql.JSONB()), sa.Column("submitted_code", sa.Text()), sa.Column("programming_language", sa.String(50)), sa.Column("is_correct", sa.Boolean()), sa.Column("marks_awarded", sa.Numeric(5,2)), sa.Column("time_spent_seconds", sa.Integer()))

def downgrade():
    op.drop_table("assessment_responses"); op.drop_table("assessment_attempts"); op.drop_table("questions"); op.drop_table("assessments")
