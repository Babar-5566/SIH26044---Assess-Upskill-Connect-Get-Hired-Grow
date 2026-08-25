from alembic import context
from sqlalchemy import engine_from_config, pool
from app.db.base import Base
from app import models
from app.core.config import settings
config=context.config
config.set_main_option('sqlalchemy.url',settings.DATABASE_URL)
target_metadata=Base.metadata
def run_migrations_online():
    with engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()
run_migrations_online()
