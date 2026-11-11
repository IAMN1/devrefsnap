import enum
import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Index
from sqlalchemy import Integer, Numeric, String, Table, Text, UniqueConstraint, create_engine, event, false, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Status(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_users_tenant_name"),
        CheckConstraint("age >= 0", name="ck_users_age"),
        Index("ix_users_tenant_active", "tenant_id", "is_active"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(default=1)
    name: Mapped[str] = mapped_column(String(50), comment="Имя пользователя")
    email: Mapped[str] = mapped_column(String(200), unique=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.current_timestamp())
    status: Mapped[Status] = mapped_column(
        Enum(Status, values_callable=lambda members: [member.value for member in members],
             native_enum=False, create_constraint=True, name="user_status"),
        default=Status.ACTIVE, server_default="active",
    )
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    manager: Mapped["User | None"] = relationship(remote_side="User.id")
    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    profile: Mapped["Profile | None"] = relationship(back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    user: Mapped[User] = relationship(back_populates="profile")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, default="")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    post: Mapped[Post] = relationship(back_populates="comments")


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list[Post]] = relationship(secondary=post_tags, back_populates="tags")


class JSONDict(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return None if value is None else json.dumps(value, allow_nan=False)

    def process_result_value(self, value, dialect):
        return None if value is None else json.loads(value)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    attributes: Mapped[dict[str, Any]] = mapped_column("metadata", MutableDict.as_mutable(JSONDict))


def new_engine():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    return engine
