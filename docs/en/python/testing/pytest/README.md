
# pytest

[Русский](../../../../ru/python/testing/pytest/README.md)

Use pytest to check Python program behavior with assertions, fixtures, parametrization, and plugins.
Several related assertions can check one scenario.
pytest allows multiple assertions in a test.

<a id="быстрый-поиск"></a>
## Quick reference

Run individual commands from the test project directory.
Use `python` from the required environment.

| Task | Command or API | Details |
| --- | --- | --- |
| Run tests | `python -m pytest` | [Configuration](configuration.md) |
| Run one test | `python -m pytest test_basics.py::test_database_write` | [Complete example](fixtures.md) |
| Show verbose output | `python -m pytest -v` | [Debugging](configuration.md#test-selection-and-debugging) |
| Select by name substring or marker | `-k 'subtotal'` / `-m 'not slow'` | [Test selection](configuration.md#test-selection-and-debugging) |
| Expect an exception | `pytest.raises(ValueError, match='quantity')` | [Assertions](fixtures.md) |
| Compare approximate numbers | `pytest.approx(0.3)` | [Assertions](fixtures.md) |
| Use a temporary path or capture output | `tmp_path`, `capsys` | [Fixtures](fixtures.md) |
| Replace a dependency | `monkeypatch`, `mocker.patch` | [Mocks](mocking-and-async.md) |
| Run an async test | `@pytest.mark.asyncio` and pytest-asyncio | [Async](mocking-and-async.md) |
| Generate a JUnit report | `--junitxml=report.xml` | [CI](configuration.md#plugins-and-reports) |

| Item | Details |
| --- | --- |
| API series | pytest 9. Some features require plugins. |
| Prerequisites | Python, an isolated environment, and basic familiarity with functions and exceptions |

<a id="навигация"></a>

<a id="базовый-уровень"></a>

To reproduce the examples, use their [exact dependencies](configuration.md#example-environment).

<a id="написать-осмысленный-тест"></a>
## Write a meaningful test

`subtotal(3, 2.5)` should return `7.5`, and a negative quantity should raise an error.
Define the expected result independently of the implementation.
This test file snippet uses the [complete demo_service.py](fixtures.md#complete-practice-example).

```python
import pytest
from demo_service import subtotal


def test_subtotal_and_rejection():
    assert subtotal(3, 2.5) == pytest.approx(7.5)
    with pytest.raises(ValueError, match="quantity"):
        subtotal(-1, 2.5)
```

The test passes for the specified behavior and fails if negative quantities go unchecked.
Choose approximate comparison tolerances based on the data.
[Complete suite and run command](fixtures.md#complete-practice-example).

Create and activate an [environment for the example](../../README.md#create-an-environment-for-an-example). Run `python -m pip install 'pytest==9.2.0'`.
In a uv project, use `uv add --dev pytest` and `uv run pytest`.
See the [uv reference](../../tooling/uv/README.md).
A test sets up data, performs an action, and checks an observable result.
It must fail when the program behaves incorrectly.

By default, pytest discovers `test_*.py` and `*_test.py` files, `test_*` functions, and methods in `Test*` classes without a custom `__init__`.
`conftest.py` makes fixtures available in its directory and descendants.
pytest loads it automatically.
A larger project can place code in `src/package/` and tests in `tests/`.
Install the package in the test environment.

The [complete example](fixtures.md) includes the function, imports, a database fixture, and an invalid-input check.

<a id="средний-уровень"></a>

<a id="управлять-подготовкой-и-вариантами-данных"></a>
## Manage setup and input variations

To give two tests independent lists, create the list in a function-scoped fixture.
This standalone test module requires pytest.

```python
import pytest


@pytest.fixture
def names():
    return []


def test_append(names):
    names.append("alice")
    assert names == ["alice"]


def test_empty(names):
    assert names == []
```

Both tests pass regardless of order.
Increasing the scope makes the mutable list shared by several tests.
[Complete resource and parameter examples](fixtures.md).

pytest injects a fixture by matching its name to a test argument.
`yield` separates setup from teardown.
If setup fails before yield, that fixture's code after yield never runs.
For several resources, arrange cleanup immediately after each resource is created successfully.
Use separate fixtures or context managers.

The diagram shows setup, test execution, and resource cleanup.

```mermaid
flowchart LR
    A[Fixture request] -->|Create resource| B[Resource setup]
    B -->|Provide value| C[yield passes value to test]
    C -->|Run test| D[Test succeeds or raises]
    D -->|Finish using resource| E[Resource teardown]
```

`@pytest.mark.parametrize` runs independent cases with explicit expected values.
`tmp_path`, `capsys`, and `monkeypatch` help isolate files, output, and environment state.
Use the [examples and scope rules](fixtures.md#scope-and-factories) to keep tests independent of execution order.

<a id="продвинутый-уровень"></a>

<a id="проверять-границы-без-реальных-внешних-сервисов"></a>
## Test boundaries with a replaced external adapter

Check that `status_label(7)` formats an adapter response while keeping the test offline.
Replace the name in the module that uses the adapter.
This snippet requires pytest-mock and the [complete demo_service.py](fixtures.md#complete-practice-example).

```python
import demo_service


def test_status_label(mocker):
    adapter = mocker.patch("demo_service.read_remote", return_value={"status": "ready"})
    assert demo_service.status_label(7) == "order 7: ready"
    adapter.assert_called_once_with(7)
```

The test checks the resulting text and the ID passed to the external adapter.
The real service implementation requires separate verification.
[Complete module with failure and async tests](mocking-and-async.md#test-an-external-contract-offline).

Patch the network client or adapter where the module under test looks it up.
Check the user-visible result and essential call contract.
Avoid assertions about arbitrary internal call counts.
The [mock and async examples](mocking-and-async.md) contain complete offline tests.

[Configuration and plugins](configuration.md) distinguish pytest features from pytest-asyncio, pytest-mock, pytest-cov, and xdist.
Parallel execution requires independent data.
Each worker process creates its own session-scoped fixture instance.

<a id="частые-ошибки"></a>
## Common mistakes

| Problem | What to do |
| --- | --- |
| Describing `minversion` as the Python version | It specifies the minimum pytest version. Constrain Python in project metadata. |
| Using `-k 'not slow'` to filter a marker | `-k` selects names and keywords. Use `-m` for markers. |
| `assert result == result` | Compare against an independently defined expected value |
| `fixture 'mocker' not found` | Install pytest-mock in the test environment |
| Unknown `--json=...` | Choose a JSON report plugin and use its documented flags |
| Using a Django client with Flask | Create a fixture with `app.test_client()`. See [Flask](../../web/flask/testing.md). |
| Library deprecations go unnoticed | Keep DeprecationWarning visible by default. Filter only a specific known cause. |

<a id="источники"></a>
## Sources

- [Running tests](https://docs.pytest.org/en/stable/how-to/usage.html), [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- [Parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html), [API and configuration](https://docs.pytest.org/en/stable/reference/reference.html).
- [Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html), [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).

[Python catalog](../../README.md)
