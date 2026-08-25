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
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    for table in SCOPED_TABLES:
        if table not in tables:
            continue
        inspector = sa.inspect(bind)
        columns = {column["name"] for column in inspector.get_columns(table)}
        if "organization_id" not in columns:
            op.add_column(table, sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True))
        indexes = {index["name"] for index in sa.inspect(bind).get_indexes(table)}
        name = f"ix_{table}_organization_id"
        if name not in indexes:
            op.create_index(name, table, ["organization_id"])
    if bind.dialect.name == "postgresql":
        op.execute("UPDATE users SET role='INDUSTRY_ADMIN' WHERE role='INDUSTRY'")
        op.execute("UPDATE users SET role='INSTITUTION_ADMIN' WHERE role='INSTITUTION'")
        op.execute("UPDATE users SET role='FACULTY' WHERE role='ACADEMICIAN'")
        for table in ("internship_postings", "academician_opportunities"):
            if table in tables:
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
        if "internship_applications" in tables:
            op.execute("""UPDATE internship_applications AS application SET organization_id = posting.organization_id FROM internship_postings AS posting WHERE application.internship_id = posting.id AND application.organization_id IS NULL""")

def downgrade():
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    for table in reversed(SCOPED_TABLES):
        if table not in tables:
            continue
        inspector = sa.inspect(bind)
        name = f"ix_{table}_organization_id"
        if name in {index["name"] for index in inspector.get_indexes(table)}:
            op.drop_index(name, table_name=table)
        if "organization_id" in {column["name"] for column in inspector.get_columns(table)}:
            op.drop_column(table, "organization_id")
