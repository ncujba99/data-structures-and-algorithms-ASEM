"""Alembic compares the models with the database and writes the difference as a migration:

    alembic revision --autogenerate -m "add platform"
"""

from logging.config import fileConfig

from alembic import context
from alembic_utils.replaceable_entity import register_entities
from sqlalchemy import create_engine

from app.db import database_url
from app.models import PAGEINSPECT, Base

fileConfig(context.config.config_file_name)

# What the database should look like: the tables of models.py, plus the pageinspect extension.
target_metadata = Base.metadata
register_entities([PAGEINSPECT])


def run_migrations_offline():
    """`alembic upgrade head --sql`: print the SQL instead of running it."""
    context.configure(url=database_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with create_engine(database_url()).connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
