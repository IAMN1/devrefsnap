# SQLAlchemy 2.0 Cheat Sheet

## Содержание
- [Установка и настройка](#установка-и-настройка)
- [Основные компоненты](#основные-компоненты)
- [Декларативные модели с typing](#декларативные-модели-с-typing)
- [Конфигурация Mapped](#конфигурация-mapped)
- [Сессии и транзакции](#сессии-и-транзакции)
- [CRUD операции](#crud-операции)
- [Запросы 2.0 Style](#запросы-20-style)
- [Отношения и связанные объекты](#отношения-и-связанные-объекты)
- [Асинхронное использование](#асинхронное-использование)
- [Работа с типами данных](#работа-с-типами-данных)
- [Композитные индексы и констрейнты](#композитные-индексы-и-констрейнты)
- [События и хуки](#события-и-хуки)
- [Миграции Alembic](#миграции-alembic)
- [Производительность и оптимизация](#производительность-и-оптимизация)

---

## Установка и настройка

```bash
# Базовая установка
pip install sqlalchemy

# С async поддержкой
pip install sqlalchemy[asyncio]

# Для конкретных диалектов
pip install sqlalchemy[postgresql]
pip install sqlalchemy[mysql]
pip install sqlalchemy[mssql]
```

## Основные компоненты

```python
from sqlalchemy import (
    create_engine, MetaData, Table, Column, 
    Integer, String, ForeignKey, select, update, delete,
    func, text, case, cast, and_, or_, not_
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, 
    Session, sessionmaker, relationship,
    aliased, joinedload, selectinload, 
    contains_eager, with_loader_criteria
)
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, 
    async_sessionmaker
)
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import enum
```

## Декларативные модели с typing

### Новый стиль (рекомендуется для 2.0+)
```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from datetime import datetime

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass

class User(Base):
    __tablename__ = 'users'
    
    # Обязательные поля с типизацией
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    
    # Optional поля
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Поля со значениями по умолчанию
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        onupdate=datetime.utcnow
    )
    
    # Boolean поле
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Enum поле
    class Status(enum.Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        BANNED = "banned"
    
    status: Mapped[Status] = mapped_column(
        default=Status.ACTIVE,
        server_default="active"
    )
    
    # Отношения (позже будет развернуто)
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"
```

### Устаревший стиль (для совместимости)
```python
# Не рекомендуется для новых проектов
from sqlalchemy import Column, Integer, String

class OldStyleUser(Base):
    __tablename__ = 'old_users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
```

## Конфигурация Mapped

### Базовые типы
```python
# Строки
name: Mapped[str] = mapped_column(String(50))
description: Mapped[Optional[str]] = mapped_column(Text)

# Числа
age: Mapped[int] = mapped_column(Integer)
price: Mapped[float] = mapped_column(Numeric(10, 2))
count: Mapped[int] = mapped_column(BigInteger)

# Даты
birth_date: Mapped[date] = mapped_column(Date)
created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
updated: Mapped[Optional[datetime]] = mapped_column(DateTime)

# Binary
data: Mapped[bytes] = mapped_column(LargeBinary)
```

### Конфигурация столбцов
```python
# Primary key
id: Mapped[int] = mapped_column(
    Integer, 
    primary_key=True, 
    autoincrement=True
)

# Уникальность и индексы
email: Mapped[str] = mapped_column(
    String(100), 
    unique=True, 
    index=True
)

# Внешние ключи
user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True
)

# Дефолтные значения
is_admin: Mapped[bool] = mapped_column(
    Boolean, 
    default=False, 
    server_default="false"
)

# С ограничениями
score: Mapped[int] = mapped_column(
    Integer,
    CheckConstraint("score >= 0 AND score <= 100")
)

# Комментарии к столбцам
title: Mapped[str] = mapped_column(
    String(200),
    comment="Заголовок статьи"
)
```

## Сессии и транзакции

### Синхронные сессии
```python
from sqlalchemy.orm import Session, sessionmaker

# Создание движка
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    # Рекомендуемые параметры
    echo=False,  # В продакшне False
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Проверка соединения
    pool_recycle=3600,   # Пересоздание соединений
)

# Фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=True,
    expire_on_commit=False,  # False для работы с объектами после коммита
    class_=Session
)

# Паттерн для FastAPI/Django
def get_db():
    """Dependency для FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Использование с контекстным менеджером
with SessionLocal() as session:
    # Автоматический коммит при успехе, откат при ошибке
    with session.begin():
        user = User(username="john")
        session.add(user)
        # session.commit() не нужен - делается автоматически
```

### Вложенные транзакции
```python
with SessionLocal() as session:
    # Внешняя транзакция
    with session.begin():
        user = User(username="john")
        session.add(user)
        
        # Внутренняя savepoint
        with session.begin_nested():
            profile = Profile(user_id=user.id)
            session.add(profile)
            # Если здесь ошибка - откатится только savepoint
        
        # user все еще в сессии
```

## CRUD операции

### Create (Вставка)
```python
# Единичная вставка
user = User(username="john", email="john@example.com")
session.add(user)
session.flush()  # Получаем ID без коммита
print(user.id)   # Доступен после flush

# Массовая вставка
users = [
    User(username=f"user{i}", email=f"user{i}@example.com")
    for i in range(10)
]
session.add_all(users)
session.commit()

# INSERT ... RETURNING
from sqlalchemy import insert
stmt = insert(User).values(
    username="jane",
    email="jane@example.com"
).returning(User.id, User.created_at)

result = session.execute(stmt)
new_user_data = result.first()
```

### Read (Чтение)
```python
# По первичному ключу (рекомендуется)
user = session.get(User, 1)  # Возвращает None если нет

# Устаревший способ (но иногда нужен)
user = session.query(User).get(1)

# Получение с блокировкой
from sqlalchemy import select
from sqlalchemy.orm import with_for_update

stmt = select(User).where(User.id == 1).with_for_update()
user = session.execute(stmt).scalar_one()
```

### Update (Обновление)
```python
# Способ 1: Обновление объекта
user = session.get(User, 1)
user.username = "new_username"
user.updated_at = datetime.utcnow()
session.commit()

# Способ 2: Массовое обновление
from sqlalchemy import update

stmt = update(User).where(User.id == 1).values(
    username="updated",
    updated_at=datetime.utcnow()
)
session.execute(stmt)
session.commit()

# Способ 3: UPDATE ... FROM (сложные условия)
stmt = update(User).values(
    is_active=False
).where(
    User.id.in_(
        select(Post.user_id).where(Post.created_at < '2023-01-01')
    )
)
```

### Delete (Удаление)
```python
# Способ 1: Удаление объекта
user = session.get(User, 1)
session.delete(user)
session.commit()

# Способ 2: Массовое удаление
from sqlalchemy import delete

stmt = delete(User).where(User.id > 1000)
session.execute(stmt)
session.commit()

# Способ 3: Каскадное удаление (настраивается в отношениях)
```

## Запросы 2.0 Style

### Базовые SELECT запросы
```python
from sqlalchemy import select

# Выборка всех полей
stmt = select(User)
result = session.execute(stmt)
users = result.scalars().all()  # Все объекты

# Выборка конкретных полей
stmt = select(User.username, User.email)
result = session.execute(stmt)
for username, email in result:
    print(username, email)

# С WHERE условиями
stmt = select(User).where(
    User.is_active == True,
    User.created_at > datetime(2023, 1, 1)
)

# Сортировка и ограничение
stmt = select(User).order_by(
    User.created_at.desc()
).limit(10).offset(20)

# Группировка и агрегация
from sqlalchemy import func

stmt = select(
    func.count(User.id).label("total"),
    func.avg(User.age).label("avg_age"),
    User.status
).group_by(User.status)

# DISTINCT
stmt = select(User.status).distinct()
```

### JOIN запросы
```python
from sqlalchemy.orm import aliased

# Простой JOIN
stmt = select(User, Post).join(Post, User.id == Post.user_id)

# JOIN с загрузкой отношений
stmt = select(User).join(User.posts).where(Post.title.like("%Python%"))

# Множественные JOIN
stmt = (
    select(User)
    .join(User.posts)
    .join(Post.comments)
    .where(Comment.is_approved == True)
)

# SELF JOIN (алиасы)
manager_alias = aliased(User)
stmt = select(User, manager_alias).join(
    manager_alias, User.manager_id == manager_alias.id
)

# OUTER JOIN
stmt = select(User).outerjoin(User.posts)
```

### Подзапросы и CTE
```python
# Подзапрос в SELECT
subq = select(func.count(Post.id)).where(Post.user_id == User.id).scalar_subquery()
stmt = select(User.username, subq.label("post_count"))

# Подзапрос в FROM
subq = select(Post).where(Post.is_published == True).subquery()
post_alias = aliased(Post, subq)
stmt = select(User).join(post_alias, User.id == post_alias.user_id)

# CTE (Common Table Expressions)
from sqlalchemy import text

cte = select(User).where(User.is_active == True).cte("active_users")
stmt = select(cte.c.username, cte.c.email)
```

### Продвинутые техники
```python
# CASE выражения
from sqlalchemy import case

stmt = select(
    User.username,
    case(
        (User.age < 18, "minor"),
        (User.age.between(18, 65), "adult"),
        else_="senior"
    ).label("age_group")
)

# UNION
stmt1 = select(User).where(User.age < 18)
stmt2 = select(User).where(User.age > 65)
union_stmt = stmt1.union(stmt2)

# EXISTS
subq = select(1).where(Post.user_id == User.id).exists()
stmt = select(User).where(subq)
```

## Отношения и связанные объекты

### One-to-Many
```python
class Post(Base):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Отношение к User
    author: Mapped["User"] = relationship(back_populates="posts")
    
    # Каскадное удаление комментариев при удалении поста
    comments: Mapped[List["Comment"]] = relationship(
        cascade="all, delete-orphan"
    )

class User(Base):
    __tablename__ = 'users'
    # ... другие поля ...
    
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        order_by=Post.created_at.desc(),
        lazy="selectin"  # Оптимизация для загрузки коллекций
    )
```

### Many-to-One
```python
class Comment(Base):
    __tablename__ = 'comments'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    
    # Many-to-One к Post
    post: Mapped["Post"] = relationship(back_populates="comments")
```

### One-to-One
```python
class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    
    # One-to-One отношение
    user: Mapped["User"] = relationship(back_populates="profile")

class User(Base):
    __tablename__ = 'users'
    # ... другие поля ...
    
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False  # Ключевой параметр для One-to-One
    )
```

### Many-to-Many
```python
# Ассоциативная таблица
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)

class Tag(Base):
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    
    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )

class Post(Base):
    __tablename__ = 'posts'
    # ... другие поля ...
    
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin"
    )
```

### Стратегии загрузки
```python
from sqlalchemy.orm import selectinload, joinedload, contains_eager

# SELECT IN загрузка (рекомендуется для коллекций)
stmt = select(User).options(selectinload(User.posts))
result = session.execute(stmt)
users = result.scalars().all()  # Посты загружены одним запросом

# JOINED загрузка (рекомендуется для одиночных отношений)
stmt = select(Post).options(joinedload(Post.author))
result = session.execute(stmt)
posts = result.unique().scalars().all()

# contains_eager для ручных JOIN
stmt = select(Post).join(Post.author).options(contains_eager(Post.author))
```

## Асинхронное использование

### Настройка асинхронного движка
```python
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, 
    async_sessionmaker, AsyncAttrs
)

class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс с поддержкой async attr loading"""
    pass

# Асинхронный движок
async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/dbname",
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "server_settings": {
            "application_name": "my_app"
        }
    }
)

# Асинхронная фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)
```

### Асинхронные операции
```python
async def create_user(username: str, email: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = User(username=username, email=email)
            session.add(user)
            # await session.flush() если нужен ID
        # Автоматический коммит при выходе
        return user

async def get_user_with_posts(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.id == user_id).options(
            selectinload(User.posts)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        # Асинхронная загрузка атрибутов
        if user:
            await user.awaitable_attrs.posts
        return user

async def transaction_example():
    async with AsyncSessionLocal() as session:
        try:
            # Начало транзакции
            await session.begin()
            
            user = User(username="async_user")
            session.add(user)
            await session.flush()
            
            post = Post(title="Async Post", user_id=user.id)
            session.add(post)
            
            # Коммит транзакции
            await session.commit()
            
        except Exception as e:
            # Откат при ошибке
            await session.rollback()
            raise e
```

## Работа с типами данных

### Кастомные типы
```python
from sqlalchemy import TypeDecorator
import json

class JSONEncodedDict(TypeDecorator):
    """Кастомный тип для хранения JSON в базе данных"""
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, ensure_ascii=False)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONEncodedDict)
    
    # Использование
    # product.metadata = {"color": "red", "size": "XL"}
```

### Enum типы
```python
from enum import Enum as PyEnum
from sqlalchemy import Enum

class UserRole(PyEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class User(Base):
    __tablename__ = 'users'
    
    # Enum сохраняется как строка в базе
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.USER
    )
    
    # Или как integer
    class Status(PyEnum):
        ACTIVE = 1
        INACTIVE = 2
        BANNED = 3
    
    status: Mapped[Status] = mapped_column(
        Enum(Status, create_constraint=True),
        default=Status.ACTIVE
    )
```

## Композитные индексы и констрейнты

```python
from sqlalchemy import UniqueConstraint, Index, CheckConstraint

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    
    # Композитный уникальный констрейнт
    __table_args__ = (
        # Уникальность username в пределах tenant
        UniqueConstraint('tenant_id', 'username', name='uq_tenant_username'),
        
        # Композитный индекс
        Index('idx_tenant_status', 'tenant_id', 'is_active'),
        
        # Проверочный констрейнт
        CheckConstraint('char_length(username) >= 3'),
        
        # Частичный индекс (PostgreSQL)
        Index('idx_active_users', 'id', postgresql_where='is_active = true'),
        
        # Уникальность с условием (PostgreSQL)
        # UniqueConstraint('email', postgresql_where='deleted_at IS NULL'),
    )
```

## События и хуки

### События сессии
```python
from sqlalchemy import event
from sqlalchemy.orm import Session

@event.listens_for(Session, 'before_commit')
def before_commit(session):
    """Вызывается перед коммитом"""
    print(f"Коммит {len(session.dirty)} измененных объектов")

@event.listens_for(Session, 'after_commit')
def after_commit(session):
    """Вызывается после успешного коммита"""
    print("Коммит успешен")

@event.listens_for(Session, 'after_rollback')
def after_rollback(session):
    """Вызывается после отката"""
    print("Откат транзакции")
```

### События модели
```python
from sqlalchemy.orm import Mapper

@event.listens_for(User, 'before_insert')
def before_insert(mapper, connection, target):
    """Вызывается перед вставкой"""
    target.created_at = datetime.utcnow()

@event.listens_for(User, 'before_update')
def before_update(mapper, connection, target):
    """Вызывается перед обновлением"""
    target.updated_at = datetime.utcnow()

@event.listens_for(User, 'load')
def after_load(target, context):
    """Вызывается при загрузке из базы"""
    print(f"Загружен пользователь {target.id}")
```

## Миграции Alembic

### Настройка
```bash
# Установка
pip install alembic

# Инициализация
alembic init alembic

# Конфигурация alembic.ini
# sqlalchemy.url = postgresql://user:pass@localhost/dbname

# Редактируем env.py для поддержки моделей
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from models import Base
target_metadata = Base.metadata

# Для async поддержки
# from sqlalchemy.ext.asyncio import AsyncEngine
# connectable = AsyncEngine(...)
```

### Команды Alembic
```bash
# Автогенерация миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

# Откат на одну миграцию
alembic downgrade -1

# Откат на конкретную версию
alembic downgrade abc123

# Проверка текущей версии
alembic current

# История миграций
alembic history --verbose

# Обновление до конкретной версии
alembic upgrade +2  # на 2 версии вперед
```

### Пример миграции
```python
# alembic/versions/abc123_initial_migration.py
"""Initial migration

Revision ID: abc123
Revises: 
Create Date: 2024-01-15 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Создание таблицы
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Создание индекса
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Добавление столбца
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # Массовое обновление данных
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")
    
    # Установка NOT NULL после заполнения
    op.alter_column('users', 'is_active', nullable=False)

def downgrade() -> None:
    # Откат изменений в обратном порядке
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

## Производительность и оптимизация

### Стратегии загрузки
```python
# 1. selectinload - для коллекций (рекомендуется)
stmt = select(User).options(selectinload(User.posts))

# 2. joinedload - для одиночных отношений
stmt = select(Post).options(joinedload(Post.author))

# 3. raiseload - защита от N+1
stmt = select(User).options(
    selectinload(User.posts),
    raiseload(User.comments)  # Вызовет исключение если обратиться
)

# 4. lazyload - ленивая загрузка (по умолчанию)
stmt = select(User)  # Отношения загружаются при обращении
```

### Пакетная обработка
```python
# yield_per для больших выборок
stmt = select(User).execution_options(yield_per=1000)
result = session.execute(stmt)

for partition in result.partitions(100):
    for user in partition:
        process_user(user)
    session.expire_all()  # Очистка сессии

# Массовые операции
from sqlalchemy.dialects.postgresql import insert as pg_insert

# UPSERT (ON CONFLICT DO UPDATE)
stmt = pg_insert(User).values([
    {"username": "user1", "email": "u1@ex.com"},
    {"username": "user2", "email": "u2@ex.com"}
]).on_conflict_do_update(
    index_elements=['username'],
    set_={'email': stmt.excluded.email}
)

# Массовое обновление с CTE
cte = (
    select(User.id, func.concat(User.username, '_new').label('new_username'))
    .where(User.age > 18)
    .cte('users_to_update')
)

stmt = update(User).where(User.id == cte.c.id).values(
    username=cte.c.new_username
)
```

### Кэширование
```python
from sqlalchemy.orm import Query
from sqlalchemy.ext.baked import bakery

# Baked queries (устаревшее, но полезно)
bakery = bakery()

@bakery
def get_user_by_id(bk, user_id):
    return bk(lambda session: session.query(User).filter(User.id == user_id))

# Современный подход - подготовленные statement
prepared_stmt = select(User).where(User.id == bindparam('uid'))

# Многократное выполнение
for user_id in user_ids:
    result = session.execute(prepared_stmt, {'uid': user_id})
    user = result.scalar_one()
```

### Мониторинг и отладка
```python
# Включение логирования
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Или через echo
engine = create_engine(..., echo=True)

# Просмотр сгенерированного SQL
stmt = select(User).where(User.id == 1)
print(stmt.compile(engine))

# Статистика запросов
from sqlalchemy import event
import time

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    print(f"Query took: {total:.3f}s")
```

---

## Важные изменения в 2.0+

1. **Обязательная типизация**: Все модели должны использовать `Mapped[]`
2. **Session.query() deprecated**: Используйте `select()` + `session.execute()`
3. **autocommit removed**: Все операции должны быть в транзакциях
4. **Новые соглашения именования**: `mapped_column()` вместо `Column()`
5. **Улучшенная async поддержка**: Полная интеграция с asyncio

## Полезные ссылки

- [Документация SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Руководство по миграции с 1.x на 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [API Reference](https://docs.sqlalchemy.org/en/20/orm/index.html)
- [Генератор запросов](https://docs.sqlalchemy.org/en/20/core/selectable.html)

## Частые ошибки и решения

```python
# Ошибка: Instance <User at 0x...> is not bound to a Session
# Решение: Не используйте объекты после закрытия сессии
# Сохраняйте нужные данные в переменные

# Ошибка: This Session's transaction has been rolled back
# Решение: Всегда обрабатывайте исключения и делайте rollback

# Ошибка: DetachedInstanceError
# Решение: Используйте expire_on_commit=False или перезагружайте объекты
```
