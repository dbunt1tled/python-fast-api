import asyncio
import importlib
import pkgutil
import sys
import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import src.app
from src.core.db.entity import Entity
from src.core.settings.setting import app_config  # type: ignore

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Entity.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
def url() -> str:
    db_url: str = str(app_config.sqlalchemy_database_uri)
    return db_url if db_url else config.get_main_option("sqlalchemy.url", "")


def import_entities(package) -> None:  # type: ignore
    for m in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(m.name)
        except Exception as e:
            print(f"Failed to import {m.name}: {e}")


import_entities(src.app)


def run_migrations_offline() -> None:
    context.configure(
        url=url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
