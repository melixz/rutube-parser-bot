from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    views = Column(String)
    video_url = Column(String, unique=True)
    channel_name = Column(String)

    __table_args__ = (UniqueConstraint("video_url", name="uq_video_url"),)
