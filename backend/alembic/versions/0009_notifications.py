"""add user notifications"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0009_notifications"; down_revision="0008_opportunity_organization_scope"; branch_labels=None; depends_on=None
def upgrade():
 op.create_table("notifications", sa.Column("id",postgresql.UUID(as_uuid=True),primary_key=True), sa.Column("user_id",postgresql.UUID(as_uuid=True),sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False), sa.Column("title",sa.String(200),nullable=False), sa.Column("message",sa.Text(),nullable=False), sa.Column("kind",sa.String(40),nullable=False), sa.Column("is_read",sa.Boolean(),nullable=False), sa.Column("created_at",sa.DateTime(timezone=True)))
 op.create_index("ix_notifications_user_id","notifications",["user_id"])
def downgrade():
 op.drop_index("ix_notifications_user_id",table_name="notifications"); op.drop_table("notifications")
