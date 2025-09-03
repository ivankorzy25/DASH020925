from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.database import Base
from app.utils.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py
def run_migrations_online():
    connectable = create_engine(settings.DATABASE_URL)
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )
        
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
