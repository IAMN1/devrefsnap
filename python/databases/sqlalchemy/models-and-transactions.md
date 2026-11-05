# Модели, CRUD и транзакции

[Справочник](README.md) · [Запросы](queries.md) · [Async и операции](async-and-operations.md)

**Уровень:** базовый → средний, savepoint и custom type — продвинутый. Сверено 2026-11-06 с SQLAlchemy 2.1. Выполнено 2026-11-06: 4 теста страницы прошли на Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0. Все примеры темы используют одну схему; зависимости: `sqlalchemy`, `pytest`. Создаётся только учебная SQLite в памяти.

## Единая схема для рецептов

Полный `demo_models.py` показывает scalar/optional/defaults, Enum, JSON TypeDecorator, constraints и четыре типа отношений.

<!-- example: sqlalchemy/demo_models.py -->
```python
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
```

Для даты рождения, больших целых и бинарных данных есть `Date`, `BigInteger`, `LargeBinary`; тип/диалект выбирай по данным. `DateTime(timezone=True)` не гарантирует одинаковое хранение timezone во всех СУБД: SQLite-пример хранит серверное время без такой гарантии. JSON TypeDecorator показан ради расширения; если диалект поддерживает нужный JSON, встроенный `JSON` обычно проще. `MutableDict` отслеживает верхний уровень словаря; вложенные dict/list требуют отдельной стратегии изменений.

## CRUD, транзакции и savepoint

Полный `demo_crud.py`; `User` создаётся со всеми обязательными полями.

<!-- example: sqlalchemy/demo_crud.py -->
```python
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from demo_models import User, new_engine


def run():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                user = User(name="alice", email="alice@example.com", age=30)
                session.add(user)
                session.flush()
                user_id = user.id
            with session.begin():
                row = session.get(User, user_id)
                row.full_name = "Alice Doe"
                session.execute(update(User).where(User.id == user_id).values(age=31))
                new_id = session.scalar(insert(User).values(name="bob", email="bob@example.com").returning(User.id))
            with session.begin():
                names = session.scalars(select(User.name).order_by(User.id)).all()
                session.execute(delete(User).where(User.id == new_id))
            return names
    finally:
        engine.dispose()


if __name__ == "__main__":
    print(run())
```

Запуск `python demo_crud.py` вернёт `['alice', 'bob']`. INSERT/UPDATE/DELETE меняют только эту временную базу, которая исчезнет после закрытия движка. `RETURNING` зависит от СУБД/версии; здесь проверяется SQLite из окружения запуска. Для существующей сессии учитывай autobegin: чтение тоже может открыть транзакцию, поэтому нельзя бездумно оборачивать уже начатую работу новым `session.begin()`.

Полный `test_models.py` проверяет откат, savepoint, constraints, отношения и custom type:

<!-- example: sqlalchemy/test_models.py -->
```python
from decimal import Decimal

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from demo_crud import run
from demo_models import Comment, Post, Product, Profile, Status, Tag, User, new_engine


def test_crud():
    assert run() == ["alice", "bob"]


def test_savepoint_keeps_outer_transaction():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                session.add(User(name="alice", email="alice@example.com"))
            with session.begin():
                session.add(User(name="bob", email="bob@example.com"))
                try:
                    with session.begin_nested():
                        session.add(User(name="duplicate", email="alice@example.com"))
                        session.flush()
                except IntegrityError:
                    pass
                session.add(User(name="carol", email="carol@example.com"))
            assert session.scalars(select(User.name).order_by(User.id)).all() == ["alice", "bob", "carol"]
    finally:
        engine.dispose()


def test_rollback_after_invalid_flush():
    engine = new_engine()
    try:
        with Session(engine) as session:
            session.add(User(name="bad", email="bad@example.com", age=-1))
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()
            session.add(User(name="good", email="good@example.com"))
            session.commit()
            assert session.scalar(select(func.count()).select_from(User)) == 1
    finally:
        engine.dispose()


def test_relations_enum_and_json():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                user = User(name="alice", email="alice@example.com", profile=Profile(bio="Author"))
                user.posts = [Post(title="Python", comments=[Comment(text="Useful")], tags=[Tag(name="python")])]
                product = Product(price=Decimal("10.25"), attributes={"color": "blue"})
                session.add_all([user, product])
            assert session.scalar(select(User)).status == Status.ACTIVE
            assert session.scalar(text("SELECT status FROM users")) == "active"
            product.attributes["color"] = "green"
            session.commit()
            session.expire_all()
            assert session.scalar(select(Product)).attributes == {"color": "green"}
            assert session.scalar(select(Product)).price == Decimal("10.25")
            session.delete(session.scalar(select(User)))
            session.commit()
            assert session.scalar(select(func.count()).select_from(Post)) == 0
            assert session.scalar(select(func.count()).select_from(Comment)) == 0
            assert session.scalar(select(func.count()).select_from(Profile)) == 0
    finally:
        engine.dispose()
```

Запуск: `python -m pytest -q test_models.py`. Savepoint должен пережить ошибку дублирующего email, а корректные изменения внешней транзакции — сохраниться. Исключение обрабатывается снаружи вложенного контекста; необработанное исключение вышло бы и из внешнего.

Для FastAPI сессия выдаётся через зависимость с `yield`; полный [sync/async HTTP-рецепт](../../web/fastapi/database.md) находится в теме FastAPI. Транзакционную границу выбирай в одном месте, не распределяй commit между несогласованными слоями.

Источники: [Declarative](https://docs.sqlalchemy.org/en/21/orm/declarative_tables.html), [отношения](https://docs.sqlalchemy.org/en/21/orm/basic_relationships.html), [транзакции/savepoint](https://docs.sqlalchemy.org/en/21/orm/session_transaction.html), [custom types](https://docs.sqlalchemy.org/en/21/core/custom_types.html), [MutableDict](https://docs.sqlalchemy.org/en/21/orm/extensions/mutable.html).
