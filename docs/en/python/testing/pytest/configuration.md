<a id="конфигурация-плагины-отладка-и-ci-pytest"></a>
# pytest configuration, plugins, debugging, and CI

[Русский](../../../../ru/python/testing/pytest/configuration.md)

Use this page to select tests, register markers, or configure reports.
Check whether an option comes from pytest itself or an installed plugin.

| Task | Technique | Example or details |
| --- | --- | --- |
| Configure discovery and markers | `pytest.ini`, `--strict-markers` | [Configuration](#configure-test-discovery-and-markers) |
| Reproduce a failure | `--lf`, `-x`, `--tb=short` | [Debugging](#test-selection-and-debugging) |
| Generate reports or run in parallel | JUnit or a plugin | [Plugins](#plugins-and-reports) |
| Reproduce the examples | Separate environment with pinned packages | [Versions](#example-environment) |

The level is intermediate to advanced.
Prerequisites include tests and pytest installed in the project environment.
[pytest reference](README.md).

<a id="настроить-сбор-тестов-и-markers"></a>
## Configure test discovery and markers

Use this complete `pytest.ini` for the practice files in this topic.

[`pytest/pytest.ini`](../../../../../examples/python/testing/pytest/pytest.ini)

`minversion` constrains **pytest**.
`asyncio_mode` requires pytest-asyncio.
If that plugin is absent and you have no async tests, remove the setting.
Real projects usually set `testpaths = tests`.
Install code from `src/package` as a package.
Alternatively, use `[tool.pytest.ini_options]` in `pyproject.toml`.
Keep one authoritative configuration.
Add build directories to `norecursedirs` if needed while preserving test discovery.

You can also register a marker with `config.addinivalue_line("markers", "slow: ...")` in the `pytest_configure` hook.
Static configuration is usually simpler.

These test module snippets require `import pytest` and `import sys`.

```python
@pytest.mark.skip(reason="нужен отдельный сервис")
def test_external_service():
    raise AssertionError("этот тест намеренно пропущен")

@pytest.mark.skipif(sys.platform == "win32", reason="проверяется Unix-поведение")
def test_unix_path():
    assert sys.platform != "win32"

@pytest.mark.xfail(strict=True, reason="воспроизводится issue #123")
def test_known_regression():
    assert 2 + 2 == 5
```

These are independent examples of individual features.
`xfail(strict=True)` treats an unexpected pass as a failure.
Remove the marker after fixing the issue.
A skip leaves the behavior untested.

<a id="выбор-тестов-и-отладка"></a>
## Test selection and debugging

Run these commands individually.
Optional debugging flags may open an interactive debugger.

```bash
python -m pytest --collect-only
python -m pytest -k 'subtotal'
python -m pytest -m 'not slow'
python -m pytest -x
python -m pytest --lf
python -m pytest --ff
python -m pytest --sw
python -m pytest -s -v
python -m pytest --durations=10
python -m pytest -rs
```

`--lf` uses the last-failure cache.
If the cache is empty, the default behavior can run all tests.
`--ff` runs previous failures first.
`--sw` stops at a failure and saves where to resume.
`-s` disables capture.
xdist imposes additional output capture limitations.
`--pdb` enters pdb on failure.
`--trace` enters pdb at the start of a test.
Install pytest-ipdb only if you need its specific features.
`--tb=auto|short|line|no` controls traceback detail.
Keep enough diagnostics visible in CI.

<a id="плагины-и-отчёты"></a>
## Plugins and reports

| Feature | Dependency | Command snippet |
| --- | --- | --- |
| JUnit XML | Built into pytest | `python -m pytest --junitxml=report.xml` |
| Coverage | pytest-cov | `python -m pytest --cov=demo_service --cov-report=term-missing --cov-report=html` |
| Parallel workers | pytest-xdist | `python -m pytest -n 2` or `-n auto` |
| Asyncio | pytest-asyncio | `python -m pytest --asyncio-mode=strict` |
| `mocker` | pytest-mock | Fixture used in a test |

Install dependencies in an existing uv project with `uv add --dev pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio`.
According to xdist documentation, `-n auto` selects physical CPU cores.
Limit process counts based on CI resources.
Each worker has its own session-scoped fixture.
Partition a shared external database by worker or avoid shared state.
Keep tests independent of execution order.
Use pytest-order only for a justified scenario.
Refer to plugin documentation for extensions such as pytest-cases.

JUnit is built into pytest.
JSON test reports require a plugin.
For example, [pytest-json-report](https://github.com/numirias/pytest-json-report) uses `--json-report --json-report-file=report.json`.
Test result JSON and **coverage** JSON serve separate purposes.
Keep DeprecationWarning visible.
When necessary, define a narrow `filterwarnings` rule by category, message, and module.
Record the reason for the filter.

<a id="среда-примеров"></a>
## Example environment

Use CPython 3.14 to reproduce the examples.
Install the packages in a separate environment with `python -m pip install 'pytest==9.2.0' 'pytest-mock==3.17.0' 'pytest-asyncio==1.4.1.post1' 'pytest-cov==7.1.0' 'pytest-xdist==3.8.0'`.

Coverage reports which lines ran.
Assess whether assertions are sufficient separately.
Check invalid inputs and external adapter failures.

<a id="источники"></a>
## Sources

[Configuration and API](https://docs.pytest.org/en/stable/reference/reference.html),
[running tests](https://docs.pytest.org/en/stable/how-to/usage.html),
[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/reporting.html),
[xdist](https://pytest-xdist.readthedocs.io/en/stable/distribution.html).
