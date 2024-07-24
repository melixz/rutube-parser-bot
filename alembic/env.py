from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Import your app config to get the DATABASE_URL
from app.config import config as app_config


# Remove sslmode from DATABASE_URL
def remove_sslmode(url):
    url_parts = list(urlsplit(url))
    query = dict(parse_qsl(url_parts[3]))
    query.pop("sslmode", None)
    url_parts[3] = urlencode(query)
    return urlunsplit(url_parts)


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the sqlalchemy.url programmatically
database_url = remove_sslmode(app_config.DATABASE_URL)
config.set_section_option(config.config_ini_section, "sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

from app.db.models.video import Base  # Import your model's Base

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        future=True,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
