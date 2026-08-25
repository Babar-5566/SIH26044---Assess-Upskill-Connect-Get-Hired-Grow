"""add organization scope to integrated opportunity tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0008_opportunity_organization_scope"; down_revision="0007_feature_tables"; branch_labels=None; depends_on=None
def upgrade():
 bind=op.get_bind(); inspector=sa.inspect(bind)
 for table in ("internship_postings","academician_opportunities"):
  columns={c["name"] for c in inspector.get_columns(table)}
  if "organization_id" not in columns:
   op.add_column(table, sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True))
  indexes={i["name"] for i in inspector.get_indexes(table)}
  if f"ix_{table}_organization_id" not in indexes: op.create_index(f"ix_{table}_organization_id", table, ["organization_id"])
def downgrade():
 bind=op.get_bind(); inspector=sa.inspect(bind)
 for table in ("academician_opportunities","internship_postings"):
  if f"ix_{table}_organization_id" in {i["name"] for i in inspector.get_indexes(table)}: op.drop_index(f"ix_{table}_organization_id", table_name=table)
  if "organization_id" in {c["name"] for c in inspector.get_columns(table)}: op.drop_column(table,"organization_id")
