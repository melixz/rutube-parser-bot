from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    views = Column(String)
    video_url = Column(String)  # новое поле
    channel_name = Column(String)
