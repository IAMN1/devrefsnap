<a id="выполнить-полные-проверки-fastapi"></a>
# Run the complete FastAPI checks

[Русский](../../../../ru/python/web/fastapi/testing-lab.md)

Use this page to reproduce a complete test module for a specific practice application.
Choose one task. TestClient and ASGITransport execute requests in process.

| Task | Technique | Complete module |
| --- | --- | --- |
| Check CRUD, PATCH, and invalid input | `TestClient` and dictionary isolation | [test_main.py](#synchronous-testclient) |
| Check an async request | `ASGITransport` and pytest-asyncio | [test_async.py](#async-client) |
| Check multipart and CORS | Synthetic bytes and preflight | [test_integrations.py](#files-and-middleware) |
| Check database access and lifespan | Separate SQLite database per test | [test_database.py](#database-sessions-and-lifespan) |
| Check passwords, JWT, and rejection | Actual practice-token verification | [test_auth.py](#authentication) |

[Short cards](testing.md) · [Applications](recipes.md) · [Dependency override](dependency-overrides.md)

Intermediate level. Async and databases are advanced.
Requires pytest and HTTP. Async requires `async`/`await`.
Install the [selected application's packages](testing.md#среда-примеров) and [prepare the required files](testing.md#setup).
Complete application files include [main.py](http-api.md), [uploads.py](uploads.md), [middleware_app.py](middleware.md), [databases](database.md), and [JWT](authentication.md).
Save the required application and corresponding test together.
Run `python -m pytest -q TEST_FILE_NAME.py`.
For async tests, add `-o asyncio_default_fixture_loop_scope=function`.

<a id="синхронный-testclient"></a>
## Synchronous TestClient

The complete `test_main.py` uses `main.py` from the HTTP recipe.
The fixture clears the practice dictionary before and after each test.
Tests therefore do not depend on execution order.

[`test_main.py`](../../../../../examples/python/web/fastapi/test_main.py)

The `with TestClient(app)` context starts lifespan.
The fixture sets `raise_server_exceptions=False`.
With this setting, a server error becomes a `500` response.
That response fails the status assertion.
By default, unhandled exceptions propagate into the test.
The numeric test sends raw JSON.
Converting `1e999` to infinity must not allow an invalid item to be saved.
That conversion must also avoid causing a response-serialization error.

<a id="асинхронный-клиент"></a>
## Async client

The complete `test_async.py` uses `pytest-asyncio` and the same `main.py`.

[`test_async.py`](../../../../../examples/python/web/fastapi/test_async.py)

`ASGITransport` does not start lifespan itself.
`main.py` has no startup resources.
If the application has startup resources, install `asgi-lifespan`.
With startup resources, wrap client use in `async with LifespanManager(app)` from `asgi_lifespan`.
For database clients, creating and using resources in the correct event loop is particularly important.
Avoid running tests against a shared in-memory dictionary concurrently within one process.

<a id="файлы-и-middleware"></a>
## Files and middleware

The complete `test_integrations.py` follows.
File contents are synthetic.
The tests do not read real user files.

[`test_integrations.py`](../../../../../examples/python/web/fastapi/test_integrations.py)

<a id="сессии-бд-и-lifespan"></a>
## Database sessions and lifespan

The complete `test_database.py` follows.
Each test gets its own SQLite file in `tmp_path`.
Before starting lifespan, the test replaces the engine and factory.
The main practice databases are left untouched.

[`test_database.py`](../../../../../examples/python/web/fastapi/test_database.py)

<a id="аутентификация"></a>
## Authentication

The complete `test_auth.py` follows.
Before importing the application, the tests set a fixed practice key in their process.
This assignment is independent of the parent process's environment variable.
For an actual application run, perform the [key setup](authentication.md#setup).

[`test_auth.py`](../../../../../examples/python/web/fastapi/test_auth.py)

These tests check the practice contracts.
Their scope excludes load testing, an actual proxy, HTTPS, and external login-provider integration.
A successful HTTP response does not verify the whole system's security.

<a id="источники"></a>
## Sources

- [FastAPI TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette current TestClient dependencies and async client](https://starlette.dev/testclient/).
- [FastAPI async tests and lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0 removal of app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio asyncio marker](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
