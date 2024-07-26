from sqlalchemy import Integer, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="user")
