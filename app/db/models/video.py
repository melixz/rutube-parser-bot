from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(Text)
    views: Mapped[str] = mapped_column(String)
    video_url: Mapped[str] = mapped_column(String, unique=True)
    channel_name: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='videos')

    __table_args__ = (UniqueConstraint("video_url", name="uq_video_url"),)
