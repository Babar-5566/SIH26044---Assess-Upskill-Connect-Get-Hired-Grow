from alembic import op
import sqlalchemy as sa

revision = "0002_phase_21_23_and_db_files"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    # 0001 already creates binary document storage on a clean migration chain.
    # These PostgreSQL-safe statements retain compatibility with older stamped
    # databases without requiring connection inspection in offline mode.
    op.execute("ALTER TABLE student_documents ADD COLUMN IF NOT EXISTS file_data BYTEA")
    op.execute("ALTER TABLE student_documents DROP COLUMN IF EXISTS file_path")
    op.create_table(
        "employment_outcomes",
        sa.Column("id", sa.Uuid(), nullable=False), sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("company_name", sa.String(200)),
        sa.Column("job_title", sa.String(200)), sa.Column("employment_type", sa.String(50)),
        sa.Column("joined_on", sa.Date()), sa.Column("ended_on", sa.Date()), sa.Column("salary", sa.Numeric(12, 2)),
        sa.Column("notes", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('SEEKING','EMPLOYED','LEFT_JOB','NOT_LOOKING')"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_employment_outcomes_student_id", "employment_outcomes", ["student_id"])
    op.create_table(
        "ai_executions", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("user_id", sa.Uuid()),
        sa.Column("feature", sa.String(80), nullable=False), sa.Column("provider", sa.String(80)), sa.Column("model_name", sa.String(120)),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("input_data", sa.JSON()), sa.Column("output_data", sa.JSON()),
        sa.Column("error_message", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)), sa.CheckConstraint("status IN ('PENDING','COMPLETED','FAILED')"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_executions_user_id", "ai_executions", ["user_id"]); op.create_index("ix_ai_executions_feature", "ai_executions", ["feature"])
    op.create_table(
        "recommendations", sa.Column("id", sa.Uuid(), nullable=False), sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_type", sa.String(20), nullable=False), sa.Column("title", sa.String(255), nullable=False),
        sa.Column("reason", sa.Text()), sa.Column("priority", sa.Integer(), nullable=False), sa.Column("source", sa.String(80), nullable=False),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("context", sa.JSON()), sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("recommendation_type IN ('CAREER','LEARNING','PROJECT','INTERNSHIP','JOB')"),
        sa.CheckConstraint("status IN ('ACTIVE','DISMISSED','COMPLETED','EXPIRED')"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_recommendations_student_id", "recommendations", ["student_id"])

def downgrade():
    op.drop_index("ix_recommendations_student_id", table_name="recommendations"); op.drop_table("recommendations")
    op.drop_index("ix_ai_executions_feature", table_name="ai_executions"); op.drop_index("ix_ai_executions_user_id", table_name="ai_executions"); op.drop_table("ai_executions")
    op.drop_index("ix_employment_outcomes_student_id", table_name="employment_outcomes"); op.drop_table("employment_outcomes")
    op.execute("ALTER TABLE student_documents ADD COLUMN IF NOT EXISTS file_path VARCHAR(500)")
    op.execute("ALTER TABLE student_documents DROP COLUMN IF EXISTS file_data")
