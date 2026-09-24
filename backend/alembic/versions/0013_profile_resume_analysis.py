"""Durable automatic saved-resume extraction."""
from alembic import op
import sqlalchemy as sa

revision = "0013_profile_resume_analysis"
down_revision = "0012_rag_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "profile_resume_analyses",
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("student_documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("student_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("content_hash", sa.String(64)),
        sa.Column("extractor_version", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("lease_token", sa.String(36)),
        sa.Column("leased_at", sa.DateTime(timezone=True)),
        sa.Column("result", sa.JSON()),
        sa.Column("chunks", sa.JSON()),
        sa.Column("error_message", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('PENDING','PROCESSING','READY','NEEDS_ATTENTION')"),
    )
    op.create_index("ix_profile_resume_analyses_student_id", "profile_resume_analyses", ["student_id"])
    op.create_index("ix_profile_resume_analyses_status", "profile_resume_analyses", ["status"])
    # Existing active resumes are automatically picked up after upgrade.
    op.execute("""INSERT INTO profile_resume_analyses (document_id, student_id, status, extractor_version, attempts)
                  SELECT id, student_id, 'PENDING', '1', 0 FROM student_documents
                  WHERE document_type = 'RESUME' AND is_active = true""")


def downgrade():
    op.drop_table("profile_resume_analyses")
