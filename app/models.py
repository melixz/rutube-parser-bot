from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    views = Column(Integer)
    url = Column(String)
