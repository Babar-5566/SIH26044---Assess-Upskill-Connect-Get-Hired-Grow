"""add organization scope to integrated opportunity tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0008_opportunity_org_scope"; down_revision="0007_feature_tables"; branch_labels=None; depends_on=None
def upgrade():
 for table in ("internship_postings","academician_opportunities"):
  op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL")
  op.execute(f"CREATE INDEX IF NOT EXISTS ix_{table}_organization_id ON {table} (organization_id)")
def downgrade():
 for table in ("academician_opportunities","internship_postings"):
  op.execute(f"DROP INDEX IF EXISTS ix_{table}_organization_id")
  op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS organization_id")
