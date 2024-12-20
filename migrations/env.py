## env file
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
# Import your Base here
from app.database import Base
from app.models.employer import *

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # Set the target metadata to use in migrations

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata  # Ensure this is passed to configure
        )

        with context.begin_transaction():
            context.run_migrations()

