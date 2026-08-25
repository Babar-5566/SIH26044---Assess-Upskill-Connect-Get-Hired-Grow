"""add notification delivery state"""
from alembic import op
import sqlalchemy as sa

revision = "0011_notification_delivery"
down_revision = "0010_organization_scope_and_backfill"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("notifications", sa.Column("delivery_status", sa.String(20), nullable=False, server_default="PENDING"))
    op.add_column("notifications", sa.Column("delivery_attempts", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("notifications", sa.Column("delivered_at", sa.DateTime(timezone=True)))
    op.add_column("notifications", sa.Column("last_delivery_error", sa.Text()))
    op.create_index("ix_notifications_delivery_status", "notifications", ["delivery_status"])

def downgrade():
    op.drop_index("ix_notifications_delivery_status", table_name="notifications")
    op.drop_column("notifications", "last_delivery_error")
    op.drop_column("notifications", "delivered_at")
    op.drop_column("notifications", "delivery_attempts")
    op.drop_column("notifications", "delivery_status")
