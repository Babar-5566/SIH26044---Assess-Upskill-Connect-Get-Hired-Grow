from alembic import context
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import engine_from_config, pool
from app.db.base import Base
from app import models
from app.core.config import settings
config=context.config
config.set_main_option('sqlalchemy.url',settings.DATABASE_URL)
target_metadata=Base.metadata
def run_migrations_online():
    with engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool).connect() as connection:
        # Several revision identifiers are longer than Alembic's historical
        # 32-character default. Keep the version table wide enough for the
        # complete revision IDs on a clean PostgreSQL database.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_pk=True,
            version_num_column_width=64,
        )
        with context.begin_transaction(): context.run_migrations()
run_migrations_online()
