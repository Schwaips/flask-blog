from datetime import datetime

from sqlalchemy import ForeignKey, Text, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .user import User


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped[User] = relationship()
    created: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
