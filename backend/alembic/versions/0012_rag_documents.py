"""Persist document ownership and ingestion metadata."""
from alembic import op
import sqlalchemy as sa

revision = "0012_rag_documents"
down_revision = "0011_notification_delivery"
branch_labels = None
depends_on = None


def upgrade():
    # Older local installations may already have this table from create_all.
    op.create_table(
        "rag_documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        if_not_exists=True,
    )
    op.create_index("ix_rag_documents_user_id", "rag_documents", ["user_id"], if_not_exists=True)


def downgrade():
    op.drop_index("ix_rag_documents_user_id", table_name="rag_documents")
    op.drop_table("rag_documents")
