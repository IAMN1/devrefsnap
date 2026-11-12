<a id="моки-и-асинхронные-тесты"></a>
# Mocks and asynchronous tests

[Русский](../../../../ru/python/testing/pytest/mocking-and-async.md)

Use this page to supply an external adapter's response in an offline test or check an `async def` function.
The example replaces the adapter in the module that calls it.

| Task | Technique | Example or details |
| --- | --- | --- |
| Check an adapter response or failure | `mocker.patch`, `side_effect` | [Complete test module](#test-an-external-contract-offline) |
| Check an async function | `pytest.mark.asyncio`, async fixture | [Complete module](#test-an-external-contract-offline) · [Event loop](#async-fixtures-and-the-event-loop) |
| Choose a web application test client | Flask, Django, or ASGI | [Integration scope](#testing-web-applications) |

The level is advanced.
Use [demo_service.py](fixtures.md#complete-practice-example), pytest, pytest-mock, and pytest-asyncio in one environment.
For the async test, review [the basics of `asyncio`](../../language/asyncio.md).
[pytest reference](README.md).
Exact package versions are listed in the [example environment](configuration.md#example-environment).

<a id="проверить-внешний-контракт-без-сети"></a>
## Test an external contract offline

Save the file next to `demo_service.py`.
Run `python -m pytest -q test_async_mock.py --asyncio-mode=strict`.
This complete example replaces the adapter in the module that uses it and runs offline.

[`pytest/test_async_mock.py`](../../../../../examples/python/testing/pytest/test_async_mock.py)

Expect **4 passed**.
The `inbox` fixture checks that the queue is empty after `test_async_result`, even if the test raises an exception.
`mocker` automatically removes patches.
`monkeypatch` restores environment changes after the test.
Checking a specific call is appropriate at an adapter boundary where its argument is part of the contract.
Patching every internal method makes tests brittle and can hide integration errors.

<a id="async-фикстуры-и-event-loop"></a>
## Async fixtures and the event loop

In strict mode, `@pytest.mark.asyncio` marks the test.
Declare async fixtures with `@pytest_asyncio.fixture`.
In auto mode, the plugin automatically handles asyncio tests and fixtures.
With several async plugins, explicit strict mode helps assign ownership.
Keep an object tied to an event loop within that loop's lifetime.
Choose compatible fixture scope and `loop_scope`.
For simple isolated tests, keep function scope.
Await directly inside an async test.
Calling `asyncio.run()` from an already running loop raises an error.

<a id="тестирование-веб-приложений"></a>
## Testing web applications

- For Flask, create separate fixtures for `app` and `client = app.test_client()`. See the [complete example](../../web/flask/testing.md).
- For Django, use `pytest-django`, project settings, and its `client` or `db` fixtures.
  Configure Django and a safe test database before using `django.test.Client`.
- An asynchronous HTTP client still needs an application compatible with its transport. A synchronous WSGI application requires an appropriate adapter for ASGI use.

<a id="источники"></a>
## Sources

[pytest-mock](https://pytest-mock.readthedocs.io/en/latest/usage.html),
[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html),
[pytest-asyncio concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html),
[pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html).
