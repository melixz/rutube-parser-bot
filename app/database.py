import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url

Base = declarative_base()


def create_engine_and_session(database_url: str):
    url = make_url(database_url)
    logging.info(
        f"Connecting to database at {url.host}:{url.port}/{url.database} with user {url.username}"
    )

    query = dict(url.query)
    sslmode = query.pop("sslmode", None)
    url = url.set(query=query)

    connect_args = {}
    if sslmode:
        connect_args["ssl"] = sslmode

    engine = create_async_engine(
        url, echo=True, connect_args=connect_args, pool_timeout=60
    )
    SessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return engine, SessionLocal


async def get_db(SessionLocal):
    async with SessionLocal() as session:
        yield session


async def init_db(database_url: str):
    engine, SessionLocal = create_engine_and_session(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return SessionLocal
