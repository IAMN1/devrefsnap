<a id="шпаргалки-по-разработке"></a>
<a name="english-reference"></a>
# Development cheat sheets

[Русский](../ru/README.md) · [Contributing](../../CONTRIBUTING.md#english)

A reference for Python, Go, C, C#, C++, TypeScript, algorithms, databases, Linux, development tools, and architecture.
Find an action through the [task and synonym index](tasks/README.md), or choose a familiar tool in the catalog.

<a id="быстрый-вход"></a>
## Quick start

| Task | Example |
| --- | --- |
| Build a project with its Dockerfile in a subdirectory | [Locate main.py, the Dockerfile and .dockerignore](tools/docker/build-context.md) · [Understand images, networks and volumes](tools/docker/guide.md) · [Run three services](tools/docker/lab.md) |
| Run your first program | [Price three tickets in Python](python/language/first-program.md) · [First C program](c/README.md#first-run) |
| Inspect an HTTP status and extract a JSON field | [HTTP and JSON in the terminal](tools/http-json.md) |
| Find why a CI test failed | [Read the GitHub Actions log](tools/compose-and-github-actions.md#find-the-cause-in-the-log) |
| Choose how to load related data | [SQLAlchemy strategy table](python/databases/sqlalchemy/relationship-loading.md#choose-a-strategy) |
| Look up familiar syntax | [C# collections](csharp/syntax.md#collections) |

<a id="разделы"></a>
## Sections

- [Python](python/README.md) covers the language, design, libraries, FastAPI, Flask, and Django.
- [Go](go/README.md) covers the language, standard library, concurrency, and testing.
- [C](c/README.md) covers C17 syntax, memory, builds and tests, design patterns, and application areas.
- [C#](csharp/README.md) covers C# 14 and .NET 10, NuGet, testing, and framework selection.
- [C++](cpp/README.md) covers C++20, the standard library, resource management, dependencies, and testing.
- [TypeScript](typescript/README.md) covers typing an HTTP client and validating JSON.
- [Algorithms](algorithms/README.md) covers estimating operation counts with Big O.
- [Databases](databases/README.md) covers SQL, PostgreSQL, SQLite, and Redis.
- [Operating systems](systems/README.md) covers Linux, the shell, and operational commands.
- [Architecture](architecture/README.md) covers task-based selection, SOLID cards, diagrams, and package layouts.
- [Development tools](tools/README.md) covers HTTP from the terminal, Docker Compose, Git, and GitHub.

<a id="каталог-материалов"></a>
## Material catalog

| Topic | Where to look |
| --- | --- |
| Read a large file one line at a time | [Read lines in Python](python/language/read-lines.md) |
| Python types | [Types and operations](python/language/types/README.md) |
| asyncio | [First coroutines and concurrent waits](python/language/asyncio.md) |
| Python project design | [Decisions, working package, and delivery](python/architecture/project-design/README.md) |
| Pydantic | [Data validation](python/validation/pydantic/README.md) |
| SQLAlchemy | [Reference](python/databases/sqlalchemy/README.md), [simple N+1 example](python/databases/sqlalchemy/n-plus-one.md), [choose loading by data and constraints](python/databases/sqlalchemy/relationship-loading.md#choose-a-strategy) |
| pytest | [Testing](python/testing/pytest/README.md) |
| structlog | [Structured logging](python/logging/structlog/README.md) |
| uv | [Python environments and dependencies](python/tooling/uv/README.md) |
| FastAPI | [Web applications and APIs](python/web/fastapi/README.md), [complete API](python/web/fastapi/http-api.md), [override a dependency in a test](python/web/fastapi/testing.md#dependency-override) |
| Django | [Model, migration, admin, and tests](python/web/django/README.md) |
| Flask | [WSGI applications, factories, and tests](python/web/flask/README.md) |
| Go | [Language, concurrency, and HTTP](go/README.md), [HTTP request timeout and cancellation](go/context.md), [complete module](go/examples/language.md) |
| C | [First run](c/README.md), [syntax](c/syntax.md), [builds, libraries, and testing](c/tooling-and-testing.md), [practices and application areas](c/practice.md) |
| C# | [First run](csharp/README.md), [syntax](csharp/syntax.md), [NuGet and testing](csharp/tooling-and-testing.md), [practices and application areas](csharp/practice.md) · [first HTTP service](csharp/first-http-service.md) · [Orders in SQLite](csharp/persist-orders.md) |
| C++ | [First run](cpp/README.md), [syntax](cpp/syntax.md), [builds, libraries, and testing](cpp/tooling-and-testing.md), [practices and application areas](cpp/practice.md) |
| SQL | [General SQL reference](databases/sql/README.md) · [duplicate email addresses](databases/sql/queries.md#duplicate-emails) |
| PostgreSQL | [Reference](databases/relational/postgresql/README.md), [backup and restore](databases/relational/postgresql/backup-and-restore.md) |
| SQLite | [Reference](databases/relational/sqlite/README.md), [backup and restore](databases/relational/sqlite/backup-and-restore.md) |
| Redis | [Data structures, caching, and messaging](databases/non-relational/redis/README.md), [RDB backup](databases/non-relational/redis/backup-and-restore.md), [AOF backup and restore](databases/non-relational/redis/aof-backup-and-restore.md) |
| curl and jq | [Send a request and inspect the HTTP response](tools/http-json.md) |
| Dockerfile and Docker Compose | [Cheat sheets](tools/docker/README.md) · [Concept guide](tools/docker/guide.md) · [Complete three-service files and exercises](tools/docker/lab.md) |
| Docker Compose and GitHub Actions | [Run an app with PostgreSQL and test it in CI](tools/compose-and-github-actions.md) |
| HTTP API contract | [FastAPI, PostgreSQL, and TypeScript in Compose and CI](tools/api-contract-lab.md) |
| Git | [Choose commands by task](tools/git/README.md) |
| GitHub Pull Requests | [Create, review, and merge PRs](tools/github-pull-requests/README.md) |
| Linux | [Shell, files, processes, and services](systems/linux/README.md), [find a process by port](systems/linux/process-by-port.md) |
| Design principles | [Boundary and trade-off cards](architecture/principles.md), [contract checks](architecture/contracts.md) |
| SOLID | [Five principles with before and after examples](architecture/solid.md) |
| Patterns | [Choose by task](architecture/patterns/README.md), [complete examples](architecture/patterns/code-examples.md), [data and failures](architecture/patterns/distributed-systems.md), [Outbox checks](architecture/patterns/outbox-example.md) |
| TypeScript | [Typed client for FastAPI](typescript/README.md) |
| Big O | [Linear and quadratic growth](algorithms/README.md#big-o) |

<a id="как-пользоваться-материалами"></a>
## Use the materials

Start with the quick lookup in the selected topic's README.
Use short cards for review.
For a first run, open a complete example with dependencies and setup.
Conditions and limitations appear beside each example.
Levels help you choose material when the tasks differ substantially.

| Level | Content |
| --- | --- |
| Beginner | First working operations, basic commands, and concepts |
| Intermediate | Common work scenarios and combinations of features |
| Advanced | Complex cases, concurrency, optimization, and operations |

Mermaid diagrams show interactions and dependencies.
GitHub renders diagrams directly in Markdown.
See [diagrams in GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams).
An editor without Mermaid support displays the diagram source.
[Language versions](../README.md) · [Material templates (Russian)](../../templates/README.md) · [Author guidelines (Russian)](../../AGENTS.md) · [Maintenance (Russian)](../../maintenance/README.md) · [Static checks and PR review (Russian)](../../scripts/README.md)
