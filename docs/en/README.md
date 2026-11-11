<a id="шпаргалки-по-разработке"></a>
# Development cheat sheets

[Русский](../ru/README.md) · [Contributing](../../CONTRIBUTING.md#english)

A reference for Python, Go, databases, Linux, development tools, and architecture.
Find an action through the [task and synonym index](tasks/README.md), or choose a familiar tool in the catalog.

<a id="быстрый-вход"></a>
## Quick start

| Situation | How to look | Example |
| --- | --- | --- |
| You remember the task but forgot the technique's name | Find an action or synonym | [Task index](tasks/README.md) |
| You chose a tool and want to review syntax | Open the topic's quick lookup | [Material catalog](#material-catalog) |
| You need to choose between approaches | Compare conditions and limitations in the card | [Loading related data](python/databases/sqlalchemy/relationship-loading.md#choose-a-strategy) |
| You need a first standalone run | Follow the card to a complete example | [Python package with tests](python/architecture/project-design/example.md) |

<a id="разделы"></a>
## Sections

- [Python](python/README.md) covers the language, design, libraries, FastAPI, and Flask.
- [Go](go/README.md) covers the language, standard library, concurrency, and testing.
- [Databases](databases/README.md) covers SQL, PostgreSQL, SQLite, and Redis.
- [Operating systems](systems/README.md) covers Linux, the shell, and operational commands.
- [Architecture](architecture/README.md) covers task-based selection, SOLID cards, diagrams, and package layouts.
- [Development tools](tools/README.md) covers Git and pull requests on GitHub.

<a id="каталог-материалов"></a>
## Material catalog

| Topic | Where to look |
| --- | --- |
| Python types | [Types and operations](python/language/types/README.md) |
| Python project design | [Decisions, working package, and delivery](python/architecture/project-design/README.md) |
| Pydantic | [Data validation](python/validation/pydantic/README.md) |
| SQLAlchemy | [Reference](python/databases/sqlalchemy/README.md), [simple N+1 example](python/databases/sqlalchemy/n-plus-one.md), [choose loading by data and constraints](python/databases/sqlalchemy/relationship-loading.md#choose-a-strategy) |
| pytest | [Testing](python/testing/pytest/README.md) |
| structlog | [Structured logging](python/logging/structlog/README.md) |
| uv | [Python environments and dependencies](python/tooling/uv/README.md) |
| FastAPI | [Web applications and APIs](python/web/fastapi/README.md), [complete API](python/web/fastapi/http-api.md), [override a dependency in a test](python/web/fastapi/testing.md#dependency-override) |
| Flask | [WSGI applications, factories, and tests](python/web/flask/README.md) |
| Go | [Language, concurrency, and HTTP](go/README.md), [complete module](go/examples/language.md) |
| SQL | [General SQL reference](databases/sql/README.md) |
| PostgreSQL | [Reference](databases/relational/postgresql/README.md), [backup and restore](databases/relational/postgresql/backup-and-restore.md) |
| SQLite | [Reference](databases/relational/sqlite/README.md), [backup and restore](databases/relational/sqlite/backup-and-restore.md) |
| Redis | [Data structures, caching, and messaging](databases/non-relational/redis/README.md), [RDB backup](databases/non-relational/redis/backup-and-restore.md), [AOF backup and restore](databases/non-relational/redis/aof-backup-and-restore.md) |
| Git | [Choose commands by task](tools/git/README.md) |
| GitHub Pull Requests | [Create, review, and merge PRs](tools/github-pull-requests/README.md) |
| Linux | [Shell, files, processes, and services](systems/linux/README.md), [find a process by port](systems/linux/process-by-port.md) |
| Design principles | [Boundary and trade-off cards](architecture/principles.md), [contract checks](architecture/contracts.md) |
| SOLID | [Five principles with before and after examples](architecture/solid.md) |
| Patterns | [Choose by task](architecture/patterns/README.md), [complete examples](architecture/patterns/code-examples.md), [data and failures](architecture/patterns/distributed-systems.md), [Outbox checks](architecture/patterns/outbox-example.md) |

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
