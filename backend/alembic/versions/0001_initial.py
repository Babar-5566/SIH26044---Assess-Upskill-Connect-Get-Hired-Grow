from alembic import op
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    from app.db.base import Base
    from app import models
    Base.metadata.create_all(op.get_bind())
def downgrade():
    from app.db.base import Base
    from app import models
    Base.metadata.drop_all(op.get_bind())
