"""add mentor assignments"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0006_mentor_assignments"; down_revision="0005_interviews_and_outcomes"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("mentor_assignments",sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True),sa.Column("mentor_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("student_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("organization_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("organizations.id",ondelete="SET NULL")),sa.Column("status",sa.String(20),nullable=False),sa.Column("focus_area",sa.String(120)),sa.Column("notes",sa.Text),sa.Column("created_at",sa.DateTime(timezone=True)))
def downgrade(): op.drop_table("mentor_assignments")
