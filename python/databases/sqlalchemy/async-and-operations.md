# Async, события и миграции

[Справочник](README.md) · [Общая схема](models-and-transactions.md)

**Уровень:** продвинутый. Сверено 2026-11-06 с SQLAlchemy 2.1 и Alembic. Выполнено 2026-11-06: async roundtrip/отношения, отказ при неверном FK с rollback и события проверены тремя тестами; миграция с backfill/NOT NULL/откатом проверена отдельно на временном файле SQLite. Python 3.14.7, SQLAlchemy 2.1.8, aiosqlite 0.22.1, SQLite 3.53.4, Alembic 1.20.1, pytest 9.2.0, pytest-asyncio 1.4.1.post1. Предпосылки: транзакции, async, различие изменения схемы и данных.

- [Асинхронная сессия](#асинхронная-сессия)
- [События и диагностика](#события-и-диагностика)
- [Alembic: отдельный учебный проект](#alembic-отдельный-учебный-проект)

## Асинхронная сессия

Установи `sqlalchemy[asyncio]`, `aiosqlite`, `pytest`, `pytest-asyncio`. Полный `demo_async.py`, остальные классы — из `demo_models.py` этой темы. Драйвер использует только SQLite в памяти.

<!-- example: sqlalchemy/demo_async.py -->
```python
import asyncio

from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from demo_models import Base, Post, User


def new_async_engine():
    engine = create_async_engine("sqlite+aiosqlite://")

    @event.listens_for(engine.sync_engine, "connect")
    def sqlite_foreign_keys(connection, record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


async def run():
    engine = new_async_engine()
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            async with session.begin():
                user = User(name="alice", email="alice@example.com", posts=[Post(title="Async Python")])
                session.add(user)
                await session.flush()
                user_id = user.id
        async with sessions() as session:
            user = await session.get(User, user_id)
            posts = await user.awaitable_attrs.posts
            titles = [post.title for post in posts]
        async with sessions() as session:
            loaded = await session.scalar(select(User).where(User.id == user_id).options(selectinload(User.posts)))
        return titles, [post.title for post in loaded.posts]
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print(asyncio.run(run()))
```

`python demo_async.py` возвращает два списка `['Async Python']`. Первый показан через `AsyncAttrs.awaitable_attrs`, второй — через предварительную загрузку. Сессию/движок закрывай через контекст/finally, а в HTTP-приложении — через lifespan/[зависимости](../../web/fastapi/database.md). Для `asyncio.gather` каждой конкурентной задаче нужна отдельная сессия. Не включай sync-драйвер в `create_async_engine`.

SQLite проверяет внешние ключи только после включения `PRAGMA foreign_keys=ON` на соединении. Как и sync-фабрика, async-фабрика включает его для каждого нового соединения, включая создание схемы; обработчик подключается к `engine.sync_engine`.

Полный `test_async.py`:

<!-- example: sqlalchemy/test_async.py -->
```python
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from demo_async import new_async_engine, run
from demo_models import Base, User


@pytest.mark.asyncio
async def test_async_roundtrip_and_loaded_relations():
    assert await run() == (["Async Python"], ["Async Python"])


@pytest.mark.asyncio
async def test_async_foreign_key_rejection_and_rollback():
    engine = new_async_engine()
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine)
        async with sessions() as session:
            session.add(User(name="orphan", email="orphan@example.com", manager_id=999))
            with pytest.raises(IntegrityError):
                await session.flush()
            await session.rollback()
            session.add(User(name="valid", email="valid@example.com"))
            await session.commit()
            assert await session.scalar(select(func.count()).select_from(User)) == 1
            assert await session.scalar(select(User.name)) == "valid"
    finally:
        await engine.dispose()
```

Источники: [SQLAlchemy asyncio, AsyncAttrs, implicit I/O](https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html), [SQLite foreign keys](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html#foreign-key-support).

## События и диагностика

Полный `demo_observe.py` показывает engine event и session events; обработчики удаляются после работы, чтобы повторный запуск не удваивал их.

<!-- example: sqlalchemy/demo_observe.py -->
```python
from time import perf_counter

from sqlalchemy import event, select
from sqlalchemy.orm import Session

from demo_models import User, new_engine


def run():
    engine = new_engine()
    elapsed, commits, inserts = [], [], []

    def before_sql(conn, cursor, statement, parameters, context, executemany):
        context.training_started = perf_counter()

    def after_sql(conn, cursor, statement, parameters, context, executemany):
        elapsed.append(perf_counter() - context.training_started)

    def after_commit(session):
        commits.append("committed")

    def before_insert(mapper, connection, target):
        target.name = target.name.strip()
        inserts.append(target.name)

    listeners = [(engine, "before_cursor_execute", before_sql), (engine, "after_cursor_execute", after_sql),
                 (Session, "after_commit", after_commit), (User, "before_insert", before_insert)]
    for target, name, callback in listeners:
        event.listen(target, name, callback)
    try:
        with Session(engine) as session, session.begin():
            session.add(User(name=" alice ", email="alice@example.com"))
        with Session(engine) as session:
            name = session.scalar(select(User.name))
        return name, commits, inserts, elapsed
    finally:
        for target, name, callback in listeners:
            event.remove(target, name, callback)
        engine.dispose()
```

Полный `test_observe.py`:

<!-- example: sqlalchemy/test_observe.py -->
```python
from demo_observe import run


def test_observed_commit_and_insert():
    name, commits, inserts, elapsed = run()
    assert name == "alice"
    assert commits == ["committed"]
    assert inserts == ["alice"]
    assert len(elapsed) >= 2
    assert all(value >= 0 for value in elapsed)
```

Запуск всех тестов темы: `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`. Время здесь охватывает выполнение DBAPI cursor, не полный lifecycle HTTP-запроса и не все расходы ORM.

| Задача | Приём / ограничение |
| --- | --- |
| SQL-лог | `logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)` после настройки logging либо `create_engine(..., echo=True)` |
| Посмотреть выражение | `str(stmt.compile(engine))`; это не EXPLAIN и не выполнение |
| Session hooks | `before_commit`, `after_commit`, `after_rollback`; после commit не рассчитывай продолжить SQL в завершённой транзакции |
| Model hooks | `before_insert`, `before_update`, `load`; mapper events имеют ограничения на допустимые действия |
| Параметризованный запрос | `select(User).where(User.id == bindparam("uid"))`, затем параметры отдельно |
| Кэш | Встроенный cache компиляции; он не кэширует результаты и не является серверным prepare |

Фрагменты таблицы предполагают импорты и модель из предыдущих примеров. SQL-логи могут содержать значения параметров; если они чувствительны, используй `hide_parameters=True` и соответствующую политику логирования. Для async события часто вешают на `engine.sync_engine` / sync Session, а не объявляют `async def` event handler. Профилирование нагрузки и подбор параметров пула не выполнялись.

Источники: [events](https://docs.sqlalchemy.org/en/21/core/event.html), [ORM events](https://docs.sqlalchemy.org/en/21/orm/events.html), [cache](https://docs.sqlalchemy.org/en/21/core/connections.html#sql-caching).

## Alembic: отдельный учебный проект

Эта последовательность проверена 2026-11-06 на отдельной SQLite с синтетическим пользователем: init/autogenerate/upgrade/current/history, затем добавление verified, backfill, NOT NULL и downgrade с сохранением остальных полей. Зависимость: `alembic`. Создай отдельную пустую папку, скопируй туда `demo_models.py`; не указывай URL существующей пользовательской БД. Проверка SQLite не подтверждает миграцию других диалектов.

Команды оболочки:

```bash
python -m pip install alembic
alembic init alembic
```

Фрагмент `alembic.ini` для локального учебного файла:

```ini
sqlalchemy.url = sqlite:///training-migrations.db
```

Фрагмент `alembic/env.py` **вместо** `target_metadata = None`; остальной сгенерированный файл сохраняется:

```python
from demo_models import Base

target_metadata = Base.metadata
```

```bash
alembic revision --autogenerate -m "create training schema"
```

Проверь сгенерированный кандидат. В этой схеме есть собственный `JSONDict`: если Alembic вывел `demo_models.JSONDict()`, добавь в модуль revision импорт `import demo_models`, иначе применение завершится `NameError`. Это часть ручной проверки autogenerate, не изменение `env.py`.

```bash
alembic upgrade head
alembic current
alembic history --verbose
```

`revision` создаёт кандидат миграции; прочитай его перед выполнением. `upgrade` меняет структуру учебной БД. Autogenerate не обнаруживает все изменения и не понимает семантику переименований. Для следующего шага сначала отредактируй модель и создай новую revision.

Пример **фрагмента** следующей revision: добавить nullable столбец, заполнить существующие строки, затем ужесточить ограничение через SQLite batch. Он требует `from alembic import op` и `import sqlalchemy as sa` в сгенерированном модуле; имена revision/down_revision берутся из реальной цепочки.

```python
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("users", sa.Column("verified", sa.Boolean(), nullable=True))
    op.execute(sa.text("UPDATE users SET verified = false WHERE verified IS NULL"))
    with op.batch_alter_table("users") as batch:
        batch.alter_column("verified", existing_type=sa.Boolean(), nullable=False)


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("verified")
```

Команды изменения версии:

```bash
alembic upgrade +1
alembic downgrade -1
```

`downgrade -1` применит обратную миграцию и может удалить столбец **вместе с данными**. Не запускай его только ради просмотра истории. Для конкретной revision укажи её настоящий id; значения вроде `abc123` — не готовые команды. Перед переносом на настоящую БД нужны резервная копия, проверка миграции/отката и план для ограничений конкретного диалекта. Async-вариант использует специальный шаблон `alembic init -t async alembic`; не оборачивай обычный `env.py` произвольным `AsyncEngine(...)`.

Источники: [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [batch для SQLite](https://alembic.sqlalchemy.org/en/latest/batch.html), [async cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic).
