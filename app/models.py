from sqlalchemy import Boolean, Column, Integer, String

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    age = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    password_hash = Column(String(255), nullable=True)

    role = Column(
        String(20),
        default="user",
        server_default="user",
        nullable=False
    )