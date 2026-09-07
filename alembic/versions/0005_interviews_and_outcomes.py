"""add interview and outcome tables when missing"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0005_interviews_and_outcomes"; down_revision="0004_assessments"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("interview_sessions",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("student_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE")),sa.Column("interview_type",sa.String(40)),sa.Column("target_role",sa.String(100)),sa.Column("target_company",sa.String(100)),sa.Column("difficulty",sa.String(20)),sa.Column("status",sa.String(30)),sa.Column("started_at",sa.DateTime(timezone=True)),sa.Column("ended_at",sa.DateTime(timezone=True)))
 op.create_table("interview_turns",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("session_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("interview_sessions.id",ondelete="CASCADE")),sa.Column("turn_number",sa.Integer()),sa.Column("ai_question",sa.Text()),sa.Column("expected_competency",sa.String(100)),sa.Column("student_audio_url",sa.String(500)),sa.Column("student_transcript",sa.Text),sa.Column("code_snippet",sa.Text),sa.Column("created_at",sa.DateTime(timezone=True)))
 op.create_table("interview_evaluations",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("session_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("interview_sessions.id",ondelete="CASCADE"),unique=True),sa.Column("technical_score",sa.Integer()),sa.Column("communication_score",sa.Integer()),sa.Column("problem_solving_score",sa.Integer()),sa.Column("behavioral_score",sa.Integer()),sa.Column("overall_score",sa.Integer()),sa.Column("strengths",postgresql.ARRAY(sa.Text)),sa.Column("areas_for_improvement",postgresql.ARRAY(sa.Text)),sa.Column("detailed_feedback",sa.Text),sa.Column("star_method_compliance",sa.String(50)),sa.Column("readiness_status",sa.String(50)),sa.Column("created_at",sa.DateTime(timezone=True)))
def downgrade():
 op.drop_table("interview_evaluations"); op.drop_table("interview_turns"); op.drop_table("interview_sessions")
