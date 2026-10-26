from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# Possibilité de faire un équivalent de infer: true sur ROm avec DeferredReflection de SqlAlchemy.
# Gardons 
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)