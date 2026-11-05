# Выдать сессию БД на запрос

[Краткий справочник](README.md) · [Тестирование](testing.md) · [SQLAlchemy](../../databases/sqlalchemy/README.md)

| Параметр | Значение |
| --- | --- |
| Уровень | Средний: синхронная сессия; продвинутый: async и жизненный цикл |
| Предпосылки | SQL, транзакции, SQLAlchemy, `Depends`; для async — `async with` |
| Сверено с документацией | 2026-11-06, FastAPI 0.162.0, SQLAlchemy API 2.0, Pydantic v2 |
| Выполнено | 2026-11-06: lifespan, запись/чтение sync/async SQLite, duplicate email → 409. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, SQLAlchemy 2.1.8, aiosqlite 0.22.1; тесты использовали временные файлы |

Оба примера самостоятельны. Не объединяй их `Base`, движки и фабрики сессий. Используется локальная SQLite с синтетическими данными; производственные подключения здесь не нужны.

## Синхронный SQLAlchemy

Установи в отдельное окружение `fastapi==0.162.0`, `uvicorn[standard]`, `sqlalchemy`, `pydantic[email]`. Полный файл `db_app.py`:

<!-- example: db_app.py -->
```python
from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

engine = create_engine(
    "sqlite:///./fastapi-sync.db",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(200), unique=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserOut(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(engine)
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
    row = UserDB(**user.model_dump())
    session.add(row)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(409, "Email уже используется") from exc
    session.refresh(row)
    return UserOut.model_validate(row)


@app.get("/users", response_model=list[UserOut])
def list_users(session: Annotated[Session, Depends(get_session)]):
    return session.scalars(select(UserDB).order_by(UserDB.id)).all()
```

```bash
uvicorn db_app:app --reload
```

```bash
curl -i -X POST http://127.0.0.1:8000/users -H 'Content-Type: application/json' -d '{"username":"alice","email":"alice@example.com"}'
curl http://127.0.0.1:8000/users
```

Ожидается `201` с `id`, затем список пользователей. Повтор того же email — `409`. Рецепт создаёт/пополняет `fastapi-sync.db` в папке запуска; повторный запуск сохраняет данные. Для чистого опыта используй новую учебную папку.

`check_same_thread=False` снимает ограничение SQLite на поток использования соединения; он не делает `Session` безопасной для параллельного общего доступа. У каждого запроса своя сессия. Блокирующие операции находятся в `def`-обработчиках, которые FastAPI выполняет в пуле потоков. Синхронный `create_all` в lifespan допустим здесь для крошечной учебной базы; в приложении применяй миграции отдельным шагом.

Источники: [SQLAlchemy: Session и транзакции](https://docs.sqlalchemy.org/en/20/orm/session_basics.html), [FastAPI: зависимости с yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/), [Pydantic: чтение атрибутов объектов](https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances).

## Async SQLAlchemy и lifespan

Установи дополнительно `sqlalchemy[asyncio]` и `aiosqlite`. Полный независимый файл `async_db_app.py`:

<!-- example: async_db_app.py -->
```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///./fastapi-async.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class NoteDB(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(200))


class NoteCreate(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class NoteOut(NoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


@app.post("/notes", response_model=NoteOut, status_code=201)
async def create_note(note: NoteCreate, session: Annotated[AsyncSession, Depends(get_session)]):
    async with session.begin():
        row = NoteDB(**note.model_dump())
        session.add(row)
        await session.flush()
    return NoteOut.model_validate(row)


@app.get("/notes", response_model=list[NoteOut])
async def list_notes(session: Annotated[AsyncSession, Depends(get_session)]):
    return (await session.scalars(select(NoteDB).order_by(NoteDB.id))).all()
```

Запуск: `uvicorn async_db_app:app --reload`. POST `/notes` с JSON `{"text":"Прочитать документацию"}` даёт `201`, GET `/notes` — список заметок. Файл `fastapi-async.db` создаётся в папке запуска.

До `yield` lifespan открывает/готовит ресурс, после `yield` закрывает. Здесь он заменяет прежние `@app.on_event("startup")` / `shutdown`. `session.begin()` фиксирует изменения при успешном выходе и откатывает их при исключении. Не разделяй один `AsyncSession` между одновременно работающими задачами. Драйвер и URL должны соответствовать async-движку; `async def` вокруг обычного синхронного драйвера не делает его неблокирующим.

Страница не реализует production-миграции, пул PostgreSQL, relationship lazy loading и восстановление БД: это самостоятельные задачи SQLAlchemy/Alembic. Старый пример с пакетом `databases` заменён одним SQLAlchemy API для sync/async; тот же принцип lifespan применим и к другим клиентам.

Источники: [FastAPI: lifespan](https://fastapi.tiangolo.com/advanced/events/), [SQLAlchemy: async API](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html), [AsyncSession и конкурентные задачи](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks).
