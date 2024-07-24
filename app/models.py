from sqlalchemy import Column, Integer, String, Text
from app.database import Base
from app.database import engine


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    views = Column(Integer)
    url = Column(String)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
