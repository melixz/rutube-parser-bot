from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import config
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

DATABASE_URL = config.DATABASE_URL


def remove_sslmode(url):
    url_parts = list(urlsplit(url))
    query = dict(parse_qsl(url_parts[3]))
    query.pop("sslmode", None)
    url_parts[3] = urlencode(query)
    return urlunsplit(url_parts)


DATABASE_URL = remove_sslmode(DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_session