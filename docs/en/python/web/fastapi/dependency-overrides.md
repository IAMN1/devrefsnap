<a id="проверить-подмену-зависимости-fastapi"></a>
# Test a FastAPI dependency override

[Русский](../../../../ru/python/web/fastapi/dependency-overrides.md)

Use this page to test a handler without calling the real dependency.
Start with the standalone program in one file.
To choose a technique, use the [short card](testing.md#dependency-override).

| Task | Technique | Example |
| --- | --- | --- |
| Check the original function and override for the first time | Create a small application and two tests | [One file, installation, and execution](#minimal-standalone-example) |
| Check restoration in detail | Use the recipe application and separate tests | [Two-file setup](#prepare-a-practice-directory) · [Complete test file](#complete-test-file) |
| Check restoration after a test or dependency error | Compare the dictionary and send a request after the block | [Restoration test](#complete-test-file) · [Expected result](#results-and-scope) |

Intermediate level. Checking cleanup requires understanding Python context managers.
Prerequisites include functions, dictionaries, imports, `with`, `try`/`finally`, and `assert` checks.
<a id="среда-примеров"></a>

Running the examples requires Python 3.14. Installation commands accompany each example.

<a id="минимальный-самостоятельный-пример"></a>
## Minimal standalone example

**Situation** — check the handler's response while temporarily bypassing the real header check.
The dependency is `verify_client`, which checks the header before the handler runs.
`Depends(verify_client)` declares the connection between the route and this function.
FastAPI normally calls the original function. An override tells FastAPI which replacement function to call.
`dependency_overrides` is an application dictionary. The key is the original function object, and the value is the replacement function.
`TestClient` sends a request to the application in process, without a network server.
`pytest` discovers `test_*` functions. `assert` checks the expected result.
`finally` performs cleanup when execution leaves `try`, including when an exception occurs.
`Header()` sets the source of `x_client` to the `X-Client` header.
`Annotated` associates the `str` type with this configuration.

Create a separate `fastapi-override-demo` directory.
Save [`test_dependency_override.py`](../../../../../examples/python/web/fastapi/test_dependency_override.py) in that directory.
This file contains the application, practice data, and tests.

[`test_dependency_override.py`](../../../../../examples/python/web/fastapi/test_dependency_override.py)

Open a terminal in `fastapi-override-demo`.
Use Python 3.14 to create a separate environment.
Run the shell commands on macOS or Linux.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'
python -m pytest -q test_dependency_override.py
```

**Expected result** — `2 passed`.
The first test checks the original responses for a missing header (`422`), an incorrect header (`400`), and the practice header (`200`).
The second test checks that the replacement is called and that the request without a header returns `200`.
After `finally`, the same test checks the previous dictionary and the return of the original HTTP responses. Test order does not affect the check.

**Limitations** — the practice header does not authenticate the request.
The override applies to the entire application while the entry remains in the dictionary.
Avoid changing overrides concurrently for a shared `app` within one process.
For concurrent tests, create a separate application per test.
Exiting `TestClient` does not clear the overrides by itself.
The replacement returns `None` here because the route uses the dependency only as a check.
For a dependency that passes data to the handler, return an appropriate value.

The tests run without external network access. Installation requires access to the package index.
Data is synthetic. The example uses no secrets or external services.
The [extended scenario](#complete-test-file) checks existing overrides and errors inside the block.
The [function-selection explanation](#choose-a-replacement-function) covers further limits for sub-dependencies and direct calls.

<a id="выбрать-функцию-для-подмены"></a>
## Choose a replacement function

| What to check | Action | What the test confirms |
| --- | --- | --- |
| The header-validation rule | Keep `verify_client` | `422`, `400`, and `200` responses for different requests |
| The handler response without header validation | Override `verify_client` | The handler returns the expected JSON without the header |
| The handler receives data from the dependency | Return a practice value from the replacement | The handler uses a value with the required type and contents |

The key in `app.dependency_overrides` is the same function object passed to `Depends`.
Supply the function object `verify_client`. A string `"verify_client"` or the result of `verify_client()` is unsuitable.
If the application is in another module, import the function from that module.

The example route declares `dependencies=[Depends(verify_client)]` and receives no check result.
Therefore, `skip_client_check` can return `None`.
If a handler receives a user or database session through a `Depends` parameter, `None` is usually unsuitable.
The replacement must return a value that supports the operations the handler performs on it.
The header example demonstrates the mechanism. Real database connections and operations fall outside its scope.

The override applies wherever this `app` resolves the original dependency through FastAPI.
The original function's sub-dependencies are also skipped.
A sub-dependency is a function that the original dependency receives through its own `Depends`.
FastAPI resolves the replacement's own dependencies as usual.
A direct Python call to `verify_client(...)` does not use the override dictionary.

`finally` restores state even when the test or request raises an exception.
`clear()` and `update(previous)` together restore the complete previous dictionary, including unrelated overrides.
`clear()` alone suffices only if the previous dictionary was empty.

<a id="подготовить-учебную-папку"></a>
## Prepare a practice directory

For the extended check, prepare the application and tests in two files.
Create a separate practice directory.
Save the [complete original `header_dependency.py`](recipes.md#check-a-header-before-the-handler) in that directory.
Save [`test_dependencies.py`](../../../../../examples/python/web/fastapi/test_dependencies.py) next to the application.
The other applications in the FastAPI section are unnecessary.
Data is synthetic. The example uses no secrets or external services.

Run the shell commands from the practice directory.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'
python -m pytest -q test_dependencies.py
```

Installation requires access to the package index.
The tests run without external network access.
Starlette uses HTTPX2 for `TestClient`.

<a id="полный-файл-тестов"></a>
## Complete test file

The complete `test_dependencies.py` uses only `header_dependency.py` from setup.
A fixture is a function that prepares a test and cleans up afterward.
`autouse=True` applies the fixture to all tests in this file.
The fixture temporarily clears earlier overrides so the first test checks the original function.

The `overridden_client` helper scopes the override to a `with` block.
The `@contextmanager` decorator turns a function with `yield` into a context manager.
The code before `yield` prepares the client. `finally` restores the dictionary when the block exits.

[`test_dependencies.py`](../../../../../examples/python/web/fastapi/test_dependencies.py)

<a id="результат-и-границы"></a>
## Results and scope

Expect `8 passed`.
The first two tests check the original function and the replacement call.
Parameterization runs the restoration test six times, with and without earlier entries for each of three exit paths.
The paths are normal exit, a failed test assertion, and an exception from the replacement function.
`pytest.raises` checks for an expected exception. The test fails if that exception is absent.
By default, `TestClient` propagates an unhandled application exception into the test.
The assertion after `pytest.raises` confirms restoration before the test ends and the fixture cleans up.
The previous `verify_client` entry is restored along with an unrelated entry.
A request after the block receives `403` from the previous override, or the original `422` if there were no previous overrides.
This request verifies the behavior of the restored dependency in addition to the dictionary contents.

`None` is suitable here because the route decorator uses the dependency only as a check.
For a dependency that returns a user or database session to the handler, choose an appropriate return value.
The [function-selection explanation](#choose-a-replacement-function) describes the dictionary key, sub-dependencies, and override scope.

The scenario excludes concurrent changes to a shared `app`, dependencies with `yield`, and external-provider behavior.
The checks use synchronous `TestClient`. The async client is covered [separately](testing.md#async-client).
Avoid running these tests concurrently with other tests of the same `app` within one process.

<a id="источники"></a>
## Sources

- [FastAPI dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [FastAPI decorator dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
- [FastAPI 0.162.0 dependency resolution](https://github.com/fastapi/fastapi/blob/0.162.0/fastapi/dependencies/utils.py).
- [FastAPI release notes 0.162.0](https://fastapi.tiangolo.com/release-notes/#01620-2026-10-23).
- [Starlette TestClient](https://starlette.dev/testclient/).

[Override card](testing.md#dependency-override) · [FastAPI reference](README.md) · [Task index](../../../tasks/README.md#http-apis-and-web-applications)
