
# Python

[Русский](../../ru/python/README.md)

[Find an example by task or synonym](../tasks/README.md) for types, asyncio, environments, validation, tests, logs, APIs, and database access.

This section covers the Python language, application design, libraries, and tools in the Python ecosystem.
Find SQL and database-specific behavior in [Databases](../databases/README.md).
Find Git and GitHub in [Development tools](../tools/README.md).

<a id="материалы"></a>
## Materials

| Topic | Contents |
| --- | --- |
| [Python types](language/types/README.md) | Types, operations, copying, and hashability |
| [asyncio basics](language/asyncio.md) | Coroutines, `await`, `asyncio.run`, and concurrent waits |
| [Project design](architecture/project-design/README.md) | Decisions, structure, a working package, and delivery |
| [Pydantic](validation/pydantic/README.md) | Models, validation, serialization, and settings |
| [SQLAlchemy](databases/sqlalchemy/README.md) | Models, [N+1 and loading](databases/sqlalchemy/relationship-loading.md), queries, transactions, async, and migrations |
| [pytest](testing/pytest/README.md) | Tests, fixtures, parametrization, mocks, and plugins |
| [structlog](logging/structlog/README.md) | Processors, context, and integrations |
| [uv](tooling/uv/README.md) | Environments, dependencies, locks, and automation |
| [FastAPI](web/fastapi/README.md) | HTTP APIs, dependencies, databases, JWT, and tests |
| [Flask](web/flask/README.md) | Factories, blueprints, configuration, and WSGI |
| [Django](web/django/README.md) | Model, SQLite migration, admin, and testing |

Each topic states its API versions, dependencies, and conditions of use.
General principles and patterns are in [Architecture](../architecture/README.md).
The design guide here applies those principles and patterns to a Python project.

<a id="связанные-темы"></a>
## Related topics

- SQLAlchemy uses [SQL](../databases/sql/README.md) and a specific database such as [PostgreSQL](../databases/relational/postgresql/README.md) or [SQLite](../databases/relational/sqlite/README.md).
- Manage pytest dependencies with [uv](tooling/uv/README.md). See [pytest](testing/pytest/README.md) to write tests.
- FastAPI data models build on [Pydantic](validation/pydantic/README.md).

[All materials](../README.md)
