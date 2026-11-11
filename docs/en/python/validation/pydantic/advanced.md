<a id="типы-настройки-и-интеграции"></a>
# Types, settings, and integrations

[Русский](../../../../ru/python/validation/pydantic/advanced.md)

Use this page to validate a list directly, load settings, or migrate Pydantic v1 code.
Choose Core Schema when you need a custom low-level type.

| Task | Technique | Example or details |
| --- | --- | --- |
| Validate a list or generic | `TypeAdapter`, `Page[T]` | [Types and complete tests](#generics-typeadapter-and-custom-types) |
| Load environment variables | `pydantic-settings.BaseSettings` | [Settings](#application-settings) |
| Validate query parameters | `Annotated[Filters, Query()]` | [FastAPI](#fastapi-query-model) |
| Migrate v1 or measure speed | Migration guide and equivalent operations | [Migration and measurements](#migration-and-performance) |

[Reference](README.md) · [Core models](models.md)

The level is intermediate to advanced.
Prerequisites include generics, `Annotated`, and environment variables.
Each example has its own dependencies. Install only the packages for your chosen task.

<a id="generic-typeadapter-и-собственный-тип"></a>
## Generics, TypeAdapter, and custom types

Use Python 3.14 to reproduce the example.
Run `python -m pip install 'pydantic==2.14.3' 'pytest==9.2.0'`.
Save the complete example as `demo_advanced.py`.
Copy `demo_types.py` from the [previous page](models.md#attributes-configuration-and-types).

[`pydantic/demo_advanced.py`](../../../../../examples/python/validation/pydantic/demo_advanced.py)

Expect user-page JSON and `{"slug":"python-guide"}`.
The example constructs `TypeAdapter` once for reuse.
For a simple slug, `Annotated[str, Field(pattern=...)]` is sufficient.
The separate class demonstrates integrations that need a custom Python type.
The Core Schema hook is sensitive to API changes.
Pin the version.
Check JSON Schema and serialization as well as object construction.

Complete `test_advanced.py` follows.

[`pydantic/test_advanced.py`](../../../../../examples/python/validation/pydantic/test_advanced.py)

<a id="настройки-приложения"></a>
## Application settings

In a separate environment, run `python -m pip install 'pydantic-settings==2.16.2' 'pytest==9.2.0'`.
The complete `demo_settings.py` reads only variables with the practice prefix.
It requires no database connection.

[`pydantic/demo_settings.py`](../../../../../examples/python/validation/pydantic/demo_settings.py)

The complete `test_settings.py` uses only a synthetic environment.

[`pydantic/test_settings.py`](../../../../../examples/python/validation/pydantic/test_settings.py)

For a separate practice dotenv file, pass `Settings(_env_file="training.env", _env_file_encoding="utf-8")`.
Environment variables take precedence over dotenv.
`get_secret_value()` reveals the underlying value, so printing its result bypasses `SecretStr` masking.
[Settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

<a id="query-модель-fastapi"></a>
## FastAPI query model

In a separate environment, run `python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'`.
The complete `demo_query.py` follows.
`Query()` explicitly populates the model from URL parameters.

[`pydantic/demo_query.py`](../../../../../examples/python/validation/pydantic/demo_query.py)

Complete `test_query.py` follows.

[`pydantic/test_query.py`](../../../../../examples/python/validation/pydantic/test_query.py)

Run only the required module with `python -m pytest -q test_advanced.py`, `test_settings.py`, or `test_query.py`.
To print JSON, run `python demo_advanced.py` from that example's practice directory.
[FastAPI documentation](https://fastapi.tiangolo.com/tutorial/query-param-models/).
See the [FastAPI reference](../../web/fastapi/README.md) for other HTTP tasks.

<a id="миграция-и-производительность"></a>
## Migration and performance

| v1 | v2 |
| --- | --- |
| `class Config`, `orm_mode` | `model_config = ConfigDict(from_attributes=True)` |
| `allow_population_by_field_name` | For new v2.11+ configurations, `validate_by_name=True`, `validate_by_alias=True` |
| `dict()` / `json()` | `model_dump()` / `model_dump_json()` |
| `parse_obj()` / `parse_raw()` for JSON | `model_validate()` / `model_validate_json()` |
| `validator` / `root_validator` | `field_validator` / `model_validator`, with revised ordering and arguments |
| `BaseSettings` in pydantic | `pydantic_settings.BaseSettings` |

The compatibility namespace is `pydantic.v1`.
It needs no separate `pydantic-v1` package.
Use `bump-pydantic` to automate migration.
Run it on a separate branch.
Review the diff and run tests to check that behavior is preserved.
Mix v1 and v2 models within one structure only through explicitly tested conversion.
On Python 3.14, check the old v1 release series' limitations before relying on it.

For measurements, compare the same data and operations with `timeit.repeat`.
Measure `TypeAdapter` construction separately from repeated validation.
Record versions and repetition counts.
`model_validate_json` often avoids an intermediate `json.loads`.
The benefit depends on validators and data.
Measure `model_construct()` as well. It skips checks.
For example, `UserView.model_construct(id="wrong", name="Alice")` preserves an invalid ID.
This explanatory snippet refers to `demo_types.py`.
Use validation at input boundaries.

See [custom types](https://docs.pydantic.dev/latest/concepts/types/), [TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/), [generics and create_model](https://docs.pydantic.dev/latest/concepts/models/), [migration guide and bump-pydantic](https://docs.pydantic.dev/latest/migration/), and [performance](https://docs.pydantic.dev/latest/concepts/performance/).
