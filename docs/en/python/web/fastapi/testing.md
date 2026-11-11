<a id="проверить-api-и-отказ-доступа"></a>
# Check the API and access rejection

[Русский](../../../../ru/python/web/fastapi/testing.md)

[Quick reference](README.md) · [Applications under test](recipes.md) · [Database](database.md) · [JWT](authentication.md)

Use this page to check an HTTP response or temporarily replace a dependency in a test.
`TestClient` sends requests to the application in process, without a network server.
Here, a dependency is a function that FastAPI calls through `Depends` before the handler.

| Situation | Technique | Example |
| --- | --- | --- |
| Check object creation and invalid input | Requests through `TestClient` | [CRUD and validation](#synchronous-testclient) |
| Check the header-validation rule itself | Keep the original dependency and send different headers | [Original function](recipes.md#check-a-header-before-the-handler) · [Complete test](dependency-overrides.md#complete-test-file) |
| Check the handler without header validation | Set `app.dependency_overrides` | [Override card](#dependency-override) |
| Check the API from `async def` | Use `ASGITransport` | [Async client](#async-client) |

| Parameter | Value |
| --- | --- |
| Level | Intermediate. Async clients and database isolation are advanced |
| Prerequisites | pytest, HTTP, and context managers. Async requires `async`/`await` |

<a id="навигация"></a>
## Navigation

- [Synchronous TestClient](#synchronous-testclient)
- [Dependency override](#dependency-override)
- [Async client](#async-client)
- [Files and middleware](#files-and-middleware)
- [Database sessions and lifespan](#database-sessions-and-lifespan)
- [Authentication](#authentication)

<a id="среда-примеров"></a>

<a id="зависимости-по-задаче"></a>
## Dependencies by task

For overrides, use the [standalone example with separate installation](dependency-overrides.md#minimal-standalone-example).
For the other tests, create a practice environment on Python 3.14.
Install the common packages with `python -m pip install 'fastapi==0.162.0' 'starlette==1.10.0' 'pytest==9.2.0' 'httpx2==2.16.0'`.
Then add only the dependencies of the selected application.

| Application under test | Additional installation |
| --- | --- |
| [main.py with CRUD and validation](http-api.md) | `python -m pip install 'pydantic[email]==2.14.3' 'email-validator==2.3.0'` |
| [uploads.py with multipart](uploads.md) | `python -m pip install 'python-multipart==0.0.33'` |
| [middleware_app.py with CORS](middleware.md) | No additional packages required |
| [db_app.py with a sync database](database.md#synchronous-sqlalchemy) | `python -m pip install 'sqlalchemy==2.1.8' 'pydantic[email]==2.14.3' 'email-validator==2.3.0'` |
| [async_db_app.py with an async database](database.md#async-sqlalchemy-and-lifespan) | `python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'aiosqlite==0.22.1'` |
| [auth_app.py with passwords and JWT](authentication.md) | `python -m pip install 'python-multipart==0.0.33' 'PyJWT==2.15.1' 'pwdlib[argon2]==0.3.1'` |

<a id="подготовка"></a>
## Setup

Save the selected application and corresponding [complete test module](testing-lab.md) together in the practice directory.
`test_integrations.py` needs both `uploads.py` and `middleware_app.py`.
`test_database.py` needs both database variants and their dependencies.
For the async test, add `pytest-asyncio==1.4.1.post1`.
Install the async test tools with this separate command.

```bash
python -m pip install pytest pytest-asyncio httpx2
```

Use `httpx2` with Starlette 1.10.0.
The earlier `httpx` package is still supported, but its use in TestClient is deprecated.
In older environments, adapt the async-client example by importing from `httpx` while retaining `ASGITransport`.
Avoid the direct `AsyncClient(app=app)` form.
HTTPX removed this argument in 0.28.0.

From the practice directory, run `python -m pytest -q TEST_FILE_NAME.py`.
For async tests, add `-o asyncio_default_fixture_loop_scope=function` to set the event-loop scope explicitly.
Tests execute requests in process.
They need neither a Uvicorn server nor external network access.

<a id="синхронный-testclient"></a>
## Synchronous TestClient

**Situation** — POST `/items` must create Book with price `25`, while a negative price must be rejected.
**Change** — check the status code and content using the actual handler.
This test snippet targets the [complete `main.py`](http-api.md#http-api-with-validation).

```python
from fastapi.testclient import TestClient
from main import app, items

items.clear()
try:
    with TestClient(app) as client:
        created = client.post("/items", json={"name": "Book", "price": 25})
        assert created.status_code == 201
        assert created.json()["name"] == "Book"
        assert client.post("/items", json={"name": "Book", "price": -1}).status_code == 422
finally:
    items.clear()
```

**Result** — a valid item is created, and invalid input is rejected.
The `TestClient` context runs lifespan. The dictionary is cleared even when an assertion fails.
The snippet assumes a separate test process without concurrent changes to the shared dictionary.
[Complete CRUD, PATCH, error, and output-model module](testing-lab.md#synchronous-testclient).

<a id="подмена-зависимости"></a>
## Dependency override

**Situation** — check a handler's response without calling the real dependency.
In the practice example, `/checked` returns JSON, and `verify_client` checks the `X-Client` header.
To check the header itself, keep the original dependency.
For a first run, use [one file with the application, installation, and two tests](dependency-overrides.md#minimal-standalone-example).

**Change** — add an original-function → replacement mapping to `app.dependency_overrides`.
`Depends(verify_client)` associates the route with the original function.
The dictionary key is that function object. The value is the replacement function, supplied without calling it.

**Example test fragment for the [complete `header_dependency.py`](recipes.md#check-a-header-before-the-handler)**

```python
from fastapi.testclient import TestClient

from header_dependency import app, verify_client


def skip_client_check():
    return None


def test_override():
    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = skip_client_check
        with TestClient(app) as client:
            response = client.get("/checked")
            assert response.status_code == 200
            assert response.json() == {"checked": True}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

**Result** — a request without the header receives `200` and `{"checked": true}`. The original dependency would return `422`.
`finally` also runs on an exception. Here, it restores the entire previous override dictionary.

**Limitations** — an override belongs to the application. Its scope extends beyond a client or one request.
Exiting `TestClient` does not clear the dictionary.
Avoid concurrent override changes on a shared `app` within one process.
`None` suits a decorator-level check. A dependency supplying handler data requires an appropriate value.

To choose a function, read the [dictionary-key, return-value, and sub-dependency explanations](dependency-overrides.md#choose-a-replacement-function).
To check cleanup, run the [restoration tests after test and dependency errors](dependency-overrides.md#complete-test-file).
See [FastAPI dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).

<a id="асинхронный-клиент"></a>
## Async client

**Situation** — the test already runs in `async def` and needs a request without a separate server.
**Change** — use `ASGITransport`, which replaces the removed `AsyncClient(app=...)` argument.
This async-test snippet targets the [complete `main.py`](http-api.md).

```python
import pytest
from httpx2 import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.json() == {"message": "Каталог работает"}
```

**Result** — the request executes in the test process.
`ASGITransport` does not start lifespan itself. Startup resources require a separate LifespanManager.
[Complete async test and cleanup boundaries](testing-lab.md#async-client).

<a id="файлы-и-middleware"></a>
## Files and middleware

**Situation** — `/upload` must measure a synthetic file without reading user files from disk.
**Change** — pass the name, bytes, and media type through `files`.
This test snippet targets the [complete `uploads.py`](uploads.md).

```python
from fastapi.testclient import TestClient
from uploads import app

with TestClient(app) as client:
    response = client.post("/upload", files={"file": ("demo.txt", b"abc", "text/plain")})
    assert response.status_code == 200
    assert response.json() == {"filename": "demo.txt", "size": 3}
```

**Result** — the handler returns size `3`.
This request does not check the proxy's total HTTP-body limit.
[Complete multiple-file, 413, CORS, and preflight checks](testing-lab.md#files-and-middleware).

<a id="сессии-бд-и-lifespan"></a>
## Database sessions and lifespan

**Situation** — a duplicate email must return `409`, and the test must avoid changing the application's practice database.
**Change** — before `TestClient`, replace the engine and factory with SQLite under `tmp_path`.
This test snippet uses `tmp_path` and `monkeypatch` fixtures for the [complete `db_app.py`](database.md#synchronous-sqlalchemy).

```python
import db_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(f"sqlite:///{tmp_path / 'users.db'}", connect_args={"check_same_thread": False})
monkeypatch.setattr(db_app, "engine", engine)
monkeypatch.setattr(db_app, "SessionLocal", sessionmaker(engine))
```

**Result** — lifespan creates the schema in a separate file. The dependency obtains sessions from the test factory.
Keep the replacement until the client context exits so lifespan closes the test engine.
The snippet prepares the resource. The [complete sync/async module](testing-lab.md#database-sessions-and-lifespan) checks the HTTP rejection itself.

<a id="аутентификация"></a>
## Authentication

**Situation** — `/users/me` must reject a request without a bearer token.
**Change** — keep the real authentication dependency and check the HTTP contract.
This snippet targets the [complete `auth_app.py`](authentication.md#complete-example) after [practice-key setup](authentication.md#setup).

```python
from fastapi.testclient import TestClient
from auth_app import app

with TestClient(app) as client:
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
```

**Result** — the client receives `401` and a bearer-authentication challenge.
Overriding `current_user` would bypass this check.
[Complete module covering passwords, signatures, expiration, and a disabled user](testing-lab.md#authentication).

<a id="источники"></a>
## Sources

- [FastAPI TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette current TestClient dependencies and async client](https://starlette.dev/testclient/).
- [FastAPI async tests and lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0 removal of app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio asyncio marker](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
