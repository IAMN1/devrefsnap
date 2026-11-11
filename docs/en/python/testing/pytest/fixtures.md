<a id="фикстуры-данные-и-assertions"></a>
# Fixtures, data, and assertions

[Русский](../../../../ru/python/testing/pytest/fixtures.md)

Use this page to check function results, expected exceptions, and resource cleanup.
The complete suite uses in-memory SQLite and temporary files.

| Task | Technique | Example or details |
| --- | --- | --- |
| Check results and invalid input | `parametrize`, `approx`, `raises` | [Complete suite](#complete-practice-example) |
| Provide a resource and close it | Fixture with `yield` and `finally` | [Complete suite](#complete-practice-example) |
| Choose data lifetime | Scope and fixture factory | [Scope](#scope-and-factories) |
| Try independent variations | Multiple `parametrize` decorators | [Cartesian product](#parametrize-independent-dimensions) |

The level is basic to intermediate.
Use Python 3.14 and pytest 9.2.0 to reproduce the examples.
[pytest reference](README.md).

<a id="полный-учебный-пример"></a>
## Complete practice example

Create the two files below in one temporary directory.
Install pytest in a separate environment.
SQLite is part of the Python standard library.
Activate the environment and run `python -m pytest -q test_basics.py`.
The example uses only an in-memory database and temporary files.

[`pytest/demo_service.py`](../../../../../examples/python/testing/pytest/demo_service.py)

[`pytest/test_basics.py`](../../../../../examples/python/testing/pytest/test_basics.py)

Expect **13 passed**.
The tests check valid and invalid quantities, SQL, fixture isolation, two encodings, output, and a warning.
For Python floats, `0.1 + 0.2 == 0.3` is usually false.
Choose a tolerance based on the data's meaning.
For monetary amounts, consider Decimal or integer minor units.

<a id="область-действия-и-фабрики"></a>
## Scope and factories

| Scope | Value lifetime |
| --- | --- |
| `function` | Each test invocation, the default |
| `class` | One test class |
| `module` | One module |
| `package` | One package |
| `session` | One pytest session in a particular process |

A session-scoped fixture cannot depend on a function-scoped resource.
pytest reports ScopeMismatch.
`autouse=True` makes the fixture apply implicitly to tests in its scope.
Use it for genuinely shared, required setup.
Put shared fixtures in `conftest.py`.
Avoid unnecessary imports of heavy dependencies.

This fixture factory snippet fits any test file with `import pytest`.

```python
@pytest.fixture
def user_factory():
    def build(**overrides):
        data = {"username": "alice", "is_active": True}
        data.update(overrides)
        return data
    return build
```

In a test, `user_factory(username="bob")` creates independent data.
When checking model validation, pass the data through real validation.

<a id="параметризовать-независимые-измерения"></a>
## Parametrize independent dimensions

Stacking two `parametrize` decorators produces a Cartesian product of the cases.
Give each case a meaningful expected result.
Use `ids` and individual `pytest.param(..., marks=...)` entries as needed.
For expensive setup, use a parametrized fixture or indirect parameters.
Keep simple input-variation tests offline.

<a id="источники"></a>
## Sources

[Fixture scopes and teardown](https://docs.pytest.org/en/stable/how-to/fixtures.html),
[parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html),
[assertions](https://docs.pytest.org/en/stable/how-to/assert.html).
