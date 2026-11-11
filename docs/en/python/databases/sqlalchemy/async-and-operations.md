<a id="async-события-и-миграции"></a>
# Async, events, and migrations

[Русский](../../../../ru/python/databases/sqlalchemy/async-and-operations.md)

Use this page to manage an async session, observe SQL, or change a schema with Alembic.
All modifying examples use a separate practice SQLite database.

| Task | Technique | Example / details |
| --- | --- | --- |
| Read an async relationship | `awaitable_attrs` or eager loading | [Async program and tests](#async-session) |
| Observe SQL and transactions | `event.listen` and handler removal | [Diagnostics](#events-and-diagnostics) |
| Change a schema | Autogenerate, manual review, upgrade | [Separate Alembic project](#alembic-in-a-separate-practice-project) |

[Reference](README.md) · [Shared schema](models-and-transactions.md)

**Level** — advanced.
Use Python 3.14. Install the selected example's dependencies before running it.
Prerequisites include transactions, async, and the distinction between schema changes and data changes.

- [Async session](#async-session)
- [Events and diagnostics](#events-and-diagnostics)
- [Alembic in a separate practice project](#alembic-in-a-separate-practice-project)

<a id="асинхронная-сессия"></a>
## Async session

Run `python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'aiosqlite==0.22.1' 'pytest==9.2.0' 'pytest-asyncio==1.4.1.post1'`.
The complete `demo_async.py` example follows.
Use the remaining classes from this topic's `demo_models.py`.
The driver uses only an in-memory SQLite database.

[`sqlalchemy/demo_async.py`](../../../../../examples/python/databases/sqlalchemy/demo_async.py)

Run `python demo_async.py`.
The result contains two `['Async Python']` lists.
The first list is obtained through `AsyncAttrs.awaitable_attrs`.
The second list is obtained through eager loading.
Close the session and engine with a context or finally block.
In an HTTP application, use lifespan and [dependencies](../../web/fastapi/database.md) to close the session and engine.
With `asyncio.gather`, each concurrent task requires its own session.
Avoid passing a sync driver to `create_async_engine`.

SQLite checks foreign keys only after `PRAGMA foreign_keys=ON` is enabled on the connection.
Like the sync factory, the async factory enables this mode for every new connection, including schema creation.
The handler is attached to `engine.sync_engine`.

Complete `test_async.py` follows.

[`sqlalchemy/test_async.py`](../../../../../examples/python/databases/sqlalchemy/test_async.py)

Sources include [SQLAlchemy asyncio, AsyncAttrs, and implicit I/O](https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html) and [SQLite foreign keys](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html#foreign-key-support).

<a id="события-и-диагностика"></a>
## Events and diagnostics

Use `demo_models.py` and the [shared schema dependencies](models-and-transactions.md#shared-schema-for-the-recipes).
Observing SQL does not require aiosqlite or Alembic.
The complete `demo_observe.py` demonstrates an engine event and session events.
The example removes its handlers after use.
Repeated runs therefore avoid duplicating handlers.

[`sqlalchemy/demo_observe.py`](../../../../../examples/python/databases/sqlalchemy/demo_observe.py)

Complete `test_observe.py` follows.

[`sqlalchemy/test_observe.py`](../../../../../examples/python/databases/sqlalchemy/test_observe.py)

Run `python -m pytest -q test_observe.py`.
The measured time covers DBAPI cursor execution.
It excludes the complete HTTP request lifecycle and some ORM overhead.

| Task | Technique / limitation |
| --- | --- |
| SQL logging | `logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)` after logging setup, or `create_engine(..., echo=True)` |
| Inspect an expression | `str(stmt.compile(engine))` compiles it without EXPLAIN or execution |
| Session hooks | `before_commit`, `after_commit`, `after_rollback`. After commit, SQL cannot continue in the completed transaction |
| Model hooks | `before_insert`, `before_update`, `load`. Mapper events restrict the permitted operations |
| Parameterized query | `select(User).where(User.id == bindparam("uid"))`, with parameters passed separately |
| Cache | Built-in compilation cache. It neither caches results nor performs server-side prepare |

The table snippets require imports and the model from the previous examples.
SQL logs can contain parameter values.
If the values are sensitive, use `hide_parameters=True`.
Apply the appropriate logging policy.
For async, event handlers often attach to `engine.sync_engine` or a sync Session.
In that case, define a regular handler function without `async def`.

Sources include [events](https://docs.sqlalchemy.org/en/21/core/event.html), [ORM events](https://docs.sqlalchemy.org/en/21/orm/events.html), and [cache](https://docs.sqlalchemy.org/en/21/core/connections.html#sql-caching).

<a id="alembic-отдельный-учебный-проект"></a>
## Alembic in a separate practice project

Create a separate empty directory and virtual environment.
Save the [complete shared schema](models-and-transactions.md#shared-schema-for-the-recipes) as `demo_models.py` in that directory.
The `asyncio` extra is required to import `AsyncAttrs` from the shared schema, including for a synchronous migration.
Avoid pointing the URL at an existing user database.
The SQLite check does not verify migration behavior in other dialects.

Run these shell commands.

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'alembic==1.20.1'
alembic init alembic
```

Use this `alembic.ini` fragment for the local practice file.

```ini
sqlalchemy.url = sqlite:///training-migrations.db
```

Replace `target_metadata = None` with the `alembic/env.py` snippet below.
Retain the rest of the generated file.

```python
from demo_models import Base

target_metadata = Base.metadata
```

```bash
alembic revision --autogenerate -m "create training schema"
```

Review the generated candidate.
This schema has a custom `JSONDict` type.
If Alembic emitted `demo_models.JSONDict()`, add `import demo_models` to the revision module.
Without that import, applying the revision raises `NameError`.
This step belongs to manual autogenerate review.
The step does not change `env.py`.

```bash
alembic upgrade head
alembic current
alembic history --verbose
```

`revision` creates a migration candidate.
Read the candidate before executing it.
`upgrade` changes the practice database's structure.
Autogenerate does not detect every change.
Autogenerate does not understand rename semantics.
For the next step, edit the model first.
Then create a new revision.

The next revision **fragment** follows.
The fragment adds a nullable column.
It then populates existing rows and tightens the constraint through SQLite batch operations.
The fragment requires `from alembic import op` and `import sqlalchemy as sa` in the generated module.
Take revision and down_revision identifiers from the actual migration chain.

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

Use these commands to change the migration version.

```bash
alembic upgrade +1
alembic downgrade -1
```

`downgrade -1` applies the reverse migration.
The command can delete a column **along with its data**.
Avoid running it solely to inspect history.
For a specific revision, supply its actual ID.
Values such as `abc123` are placeholders that need replacement before running a command.
Before applying the process to a real database, prepare a backup.
Check the migration.
Check rollback.
Prepare a plan for the specific dialect's limitations.
The async variant uses the special `alembic init -t async alembic` template.
Avoid wrapping a regular `env.py` in an arbitrary `AsyncEngine(...)`.

Sources include the [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [SQLite batch operations](https://alembic.sqlalchemy.org/en/latest/batch.html), and [async cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic).
