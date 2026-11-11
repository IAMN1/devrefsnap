<a id="собрать-пакет-внедрить-зависимости-и-проверить-сценарий"></a>
# Build a package, inject dependencies, and test a scenario

[Русский](../../../../ru/python/architecture/project-design/example.md)

The example looks up a product by SKU in memory or SQLite.
Use the example to build an installable package and test one scenario with two storage implementations.

| What to review | Technique | Code / run instructions |
| --- | --- | --- |
| Replace storage without changing the lookup | Pass an object with a `get` method | [Scenario](#model-and-scenario), [two adapters](#two-adapters) |
| Create dependencies in one place | Assemble objects before startup | [Settings and assembly](#settings-and-assembly) |
| Check success, a missing product, and invalid input | Run the same tests for both adapters | [Tests](#tests), [commands](#run) |

[Guide](README.md) · [Structure explanation](structure-and-decisions.md)

| Parameter | Value |
| --- | --- |
| Level | Intermediate for packaging, DI, and configuration. Advanced for testing two adapters |
| Prerequisites | Python, `pyproject.toml`, and pytest. The run commands use uv |

Use Python 3.14 and uv to run the example.
The dependencies are specified in `pyproject.toml` below.

The example covers read-only CLI product lookup. HTTP and writes to a production database are outside its scope.
Each link opens a complete example file.

<a id="навигация"></a>
## Navigation

- [Metadata and structure](#metadata-and-structure)
- [Model and scenario](#model-and-scenario)
- [Two adapters](#two-adapters)
- [Settings and assembly](#settings-and-assembly)
- [Run](#run)
- [Tests](#tests)
- [Extend the example](#extend-the-example)

<a id="метаданные-и-структура"></a>
## Metadata and structure

Create `src/catalog_demo/` and `tests/`.
Before running the example, save all files from the directory tree at the paths shown, including [`tests/test_catalog.py`](../../../../../examples/python/architecture/project-design/tests/test_catalog.py).
The packaging tool reads `pyproject.toml`.

[`project-design/pyproject.toml`](../../../../../examples/python/architecture/project-design/pyproject.toml)

Application dependency versions are pinned for this example.
The Python constraint and build backend choice do not verify every possible environment combination.
Record the resolved project environment, for example in `uv.lock`.
Update the environment deliberately.

`__init__.py` marks a regular package.
Here, the file contains only a docstring.

[`project-design/src/catalog_demo/__init__.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/__init__.py)

<a id="модель-и-сценарий"></a>
## Model and scenario

[`project-design/src/catalog_demo/domain.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/domain.py)

[`project-design/src/catalog_demo/application.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/application.py)

`...` is a valid method body in a `Protocol`, which describes an interface for static type checking.
The working implementations follow below. Tests verify their runtime behavior.

<a id="два-адаптера"></a>
## Two adapters

[`project-design/src/catalog_demo/adapters.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/adapters.py)

The adapter receives a connection from its caller.
There is no hidden global connection.
The schema must already exist.
The test creates the schema explicitly.
In an application, the selected migration mechanism creates the schema.
Pass the SKU value as a SQL parameter to keep it separate from the query text.

<a id="настройки-и-сборка"></a>
## Settings and assembly

[`project-design/src/catalog_demo/config.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/config.py)

The example does not read `.env` automatically.
Choose the settings source explicitly in your application.
Set settings precedence explicitly.
Environment variables, a specific `.env` file, secret storage, and launch arguments serve different purposes.
Import `BaseSettings` from **pydantic_settings**. Older `pydantic` v1 examples use a different import.

[`project-design/src/catalog_demo/bootstrap.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/bootstrap.py)

This is the composition root, the place where objects are wired to known concrete implementations.
If SQLite is needed, the composition root can create the connection.
It also handles connection closure.
It passes the SQLite adapter in place of the in-memory adapter.
`FindProduct` can keep its existing imports.

<a id="запуск"></a>
## Run

[`project-design/src/catalog_demo/__main__.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/__main__.py)

Run the commands from the root of the practice package.

```bash
uv sync --group dev
uv run python -m catalog_demo book
uv run pytest -q
```

The first invocation installs the package **in the practice directory**.
It also creates the environment and lockfile **in the practice directory**.
The lookup prints `book: Python guide`.
`uv run python -m catalog_demo unknown` exits with code `2` and an argparse message.
`CATALOG_DEMO_ENVIRONMENT=test` is valid.
With an unknown environment name, Settings rejects the value before assembling the application.

<a id="тесты"></a>
## Tests

[`project-design/tests/test_catalog.py`](../../../../../examples/python/architecture/project-design/tests/test_catalog.py)

The same checks run for both adapters.
SQLite runs in memory.
The SQLite connection closes after the test.
The test with a SQL-like value checks parameterization.
The tests leave global data and real databases untouched.

<a id="как-развивать-пример"></a>
## Extend the example

- An HTTP adapter maps `ProductNotFound` to the chosen API response. The domain error has no FastAPI or Flask dependency.
- Define the public response model at the application boundary. Define permissions at the application boundary. Validate external JSON at the application boundary.
- PostgreSQL requires its own integration tests. A passing SQLite test covers SQLite behavior.
- Data writes require an explicit transaction boundary and concurrency rules. This example covers read-only behavior.
- Use a DI container when it provides concrete benefits for the dependency graph and lifetimes. Manual assembly is sufficient here.

Sources include [PyPA pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/),
[Python sqlite3](https://docs.python.org/3.14/library/sqlite3.html), [PEP 544](https://peps.python.org/pep-0544/),
and [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
