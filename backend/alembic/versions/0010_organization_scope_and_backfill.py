"""scope domain records to organizations and backfill legacy ownership"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_org_scope_backfill"
down_revision = "0009_notifications"
branch_labels = None
depends_on = None

SCOPED_TABLES = ("learning_resources", "student_learning_plans", "assessments", "interview_sessions", "internship_applications", "employment_outcomes")

def upgrade():
    for table in SCOPED_TABLES:
        op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL")
        op.execute(f"CREATE INDEX IF NOT EXISTS ix_{table}_organization_id ON {table} (organization_id)")
    op.execute("UPDATE users SET role='INDUSTRY_ADMIN' WHERE role='INDUSTRY'")
    op.execute("UPDATE users SET role='INSTITUTION_ADMIN' WHERE role='INSTITUTION'")
    op.execute("UPDATE users SET role='FACULTY' WHERE role='ACADEMICIAN'")
    for table in ("internship_postings", "academician_opportunities"):
        op.execute(sa.text(f"""
                    UPDATE {table} AS opportunity
                    SET organization_id = (
                        SELECT membership.organization_id
                        FROM organization_memberships AS membership
                        WHERE membership.user_id = opportunity.company_id
                          AND membership.status = 'ACTIVE'
                        ORDER BY membership.is_primary DESC, membership.created_at ASC
                        LIMIT 1
                    )
                    WHERE opportunity.organization_id IS NULL
                """))
    op.execute("""UPDATE internship_applications AS application SET organization_id = posting.organization_id FROM internship_postings AS posting WHERE application.internship_id = posting.id AND application.organization_id IS NULL""")

def downgrade():
    for table in reversed(SCOPED_TABLES):
        op.execute(f"DROP INDEX IF EXISTS ix_{table}_organization_id")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS organization_id")
