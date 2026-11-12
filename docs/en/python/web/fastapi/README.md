
# FastAPI

[Русский](../../../../ru/python/web/fastapi/README.md)

FastAPI builds HTTP APIs from Python annotations and Pydantic models.
Use this reference for requests, databases, testing, authentication, and startup.
Detailed examples are provided in standalone recipes.

[Python catalog](../../README.md)

<a id="быстрый-поиск"></a>
## Quick lookup

| Task | API / command | Details |
| --- | --- | --- |
| Start an API | `uvicorn minimal:app --reload` | [First run](#first-run) |
| CRUD, path/query/body, validation | `Path`, `Query`, `BaseModel`, `Field` | [Complete CRUD](http-api.md#http-api-with-validation) |
| Responses, errors, output model | `response_model`, `HTTPException`, `JSONResponse` | [Models and responses](http-api.md#http-api-with-validation) |
| Inspect an HTTP response from the terminal | `curl -i`, `jq` | [HTTP and JSON](../../../tools/http-json.md) |
| Function, class, sub-dependency | `Annotated[T, Depends(...)]` | [Dependencies](recipes.md#how-dependencies-work) |
| Form, one or several files | `Form`, `UploadFile`, `File` | [Complete application](uploads.md#forms-and-file-uploads) |
| Request timing and CORS | `@app.middleware`, `CORSMiddleware` | [Complete application](middleware.md#middleware-and-cors) |
| Session per request, startup/shutdown | `yield`, `lifespan`, SQLAlchemy | [Database](database.md) |
| Test the API synchronously or asynchronously | `TestClient`, `ASGITransport` | [Testing](testing.md) |
| Test a handler without calling the real dependency | `app.dependency_overrides` | [Selection card](testing.md#dependency-override) · [Standalone program](dependency-overrides.md#minimal-standalone-example) |
| Restore dependencies after a test or error | `try` / `finally` | [Complete restoration checks](dependency-overrides.md#complete-test-file) |
| Verify a password and JWT | `pwdlib`, `PyJWT`, `OAuth2PasswordBearer` | [Authentication](authentication.md) |
| Workers, containers, OpenAPI | Uvicorn, Docker, `app.openapi()` | [Startup and deployment](deployment.md) |

| Parameter | Value |
| --- | --- |
| Target API | FastAPI 0.162.0, Pydantic v2. Example syntax requires Python 3.10+ |
| Prerequisites | Functions, type annotations, HTTP/JSON. Advanced tasks require `async` and context managers |

<a id="навигация"></a>

<a id="базовый-уровень"></a>

<a id="первый-запуск"></a>
## First run

Use Python 3.14, FastAPI 0.162.0, and Uvicorn 0.54.0 to reproduce the example.

Create a virtual environment in a separate practice directory.
Install the dependencies in that environment.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]'
```

Save the complete example as `minimal.py` in this directory.

[`minimal.py`](../../../../../examples/python/web/fastapi/minimal.py)

```bash
uvicorn minimal:app --reload
curl http://127.0.0.1:8000/
```

The result is `200` and `{"message":"Привет"}`.
Swagger UI is available at [localhost:8000/docs](http://localhost:8000/docs).
ReDoc is available at [localhost:8000/redoc](http://localhost:8000/redoc).
The schema is available at [localhost:8000/openapi.json](http://localhost:8000/openapi.json).
Here, `version` denotes your API's version.

Call the same route from a [TypeScript HTTP client](../../../typescript/README.md) to validate the response fields in code.
Use the [end-to-end lab](../../../tools/api-contract-lab.md) to run FastAPI with PostgreSQL and check its responses in CI.

<a id="откуда-берётся-параметр"></a>
## Parameter sources

| Declaration | Source |
| --- | --- |
| `item_id: int` with path `/items/{item_id}` | URL segment |
| `q: str \| None = None` | Optional query parameter |
| `tags: Annotated[list[str] \| None, Query()] = None` | Repeated query parameter `?tags=a&tags=b` |
| `item: ItemCreate` | JSON body validated by Pydantic |
| `x_token: Annotated[str, Header()]` | `X-Token` header |
| `last_query: Annotated[str \| None, Cookie()] = None` | `last_query` cookie |

These are signature fragments.
Complete imports and handlers are in the [recipes](recipes.md).
Specify `Query` explicitly for a list of query parameters.
`str | None` permits `null`/`None`.
The default value determines whether a parameter is required.

<a id="методы-и-модели"></a>
## Methods and models

`GET` reads data.
`POST` creates data.
`PUT` replaces data completely.
`PATCH` updates the supplied fields.
`DELETE` deletes data.
The handler implements these semantics.
The decorator alone does not enforce them.

Use `BaseModel` for input data.
Define constraints with `Field`.
Define custom rules with `field_validator` and `model_validator`.
Declare a separate output model that omits the password.
Specify the output model in `response_model`.
[Consistent CRUD and models](recipes.md#http-api-with-validation).

<a id="средний-уровень"></a>

<a id="отдать-публичную-модель-без-пароля"></a>
## Return a public model without a password

**Situation** — `/user-preview` accepts a password, but the HTTP response must omit it.
**Change** — set a separate `UserOut` model through `response_model`.
The snippet comes from the [complete HTTP application](recipes.md#http-api-with-validation), where both models are already defined.

```python
@app.post("/user-preview", response_model=UserOut)
async def preview_user(user: UserIn):
    return user
```

**Result** — a request with `username`, `email`, and `password` returns public fields with `password` omitted.
A prebuilt `Response` bypasses normal response-model filtering.
[Complete application](recipes.md#http-api-with-validation) · [Password-omission check](testing.md#synchronous-testclient).


| Task | What to remember |
| --- | --- |
| Reuse parameters | `Depends` calls a function or class. Sub-dependencies form a tree |
| Run a check without a return value | Set `dependencies=[Depends(check)]` on the route |
| Return a controlled error | `raise HTTPException(status_code=404, detail="...")` |
| Change the success status code | Set `status_code=201` on the decorator |
| Return HTML, a redirect, or special headers | Use a specialized `Response`. Its body bypasses normal `response_model` filtering |
| Accept a file | If the whole file is not needed in memory, read `UploadFile` in chunks |
| Test a route | Check the useful result. Check invalid input. Check a missing object |

Use the [recipes](recipes.md) for custom exception handlers, forms, and middleware.
To change a dependency's result in tests, use [dependency overrides](testing.md#dependency-override).

<a id="продвинутый-уровень"></a>

<a id="закрывать-сессию-после-запроса"></a>
## Close the session after the request

**Situation** — each synchronous handler must receive its own SQLAlchemy Session.
**Change** — provide the session through a dependency with `yield`.
The snippet comes from the [complete `db_app.py`](database.md#synchronous-sqlalchemy), where `SessionLocal` is a session factory.

```python
def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

**Result** — exiting the dependency closes the session. The handler receives it through `Depends(get_session)`.
The Session context does not commit by itself.
In the complete example, the handler explicitly commits or rolls back the transaction.
[Sync/async applications](database.md) · [Database and lifespan checks](testing.md#database-sessions-and-lifespan).


- **Lifecycle and databases** — create shared resources in `lifespan`. Close shared resources in `lifespan`. Provide a session per request through `yield`. Use synchronous SQLAlchemy in `def` handlers. `async def` requires a nonblocking client. [Sync and async variants](database.md).
- **Authentication** — extracting a bearer string alone does not verify the user. Verify the password before issuing a token. When reading a token, verify its signature, algorithm, expiration, and user. [Complete practice recipe](authentication.md).
- **Operations** — use `--reload` for development. Choose the worker count for the workload. Process memory cannot serve as a shared database. [Workers and container](deployment.md).
- **Migrating older examples** — for Pydantic v1, migrate `dict()` → `model_dump()`, `validator` → `field_validator`, and `root_validator` → `model_validator`. For events, migrate `on_event` → `lifespan`. For HTTPX, migrate `AsyncClient(app=...)` → `ASGITransport(app=...)`. Check behavior after migration. Renaming alone is insufficient.

<a id="частые-ошибки"></a>
## Common errors

| Symptom | Cause | Correction |
| --- | --- | --- |
| `422 Unprocessable Entity` | Input does not match the schema | Read `detail`. Check the parameter source. Check required fields |
| Response contains an extra field | No suitable output model, or a prebuilt `Response` was returned | Set `response_model`. Test that the field is absent |
| Server stalls on I/O | A blocking call inside `async def` | Use an async driver or a synchronous `def` handler |
| Startup did not run in a test | The client did not start lifespan | Use `with TestClient(app)` or `LifespanManager` for an async client |
| Data disappeared after restart | The practice store lives in memory | Move to a [database](database.md) |
| CORS blocks the browser | The allowed origin's scheme, host, or port differs | Configure the exact origin. Check preflight |

<a id="источники"></a>
## Sources

- [FastAPI release notes 0.162.0](https://fastapi.tiangolo.com/release-notes/#01620-2026-10-23).
- [Query parameters](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [response models](https://fastapi.tiangolo.com/tutorial/response-model/).
- [When to use async or def](https://fastapi.tiangolo.com/async/), [lifespan](https://fastapi.tiangolo.com/advanced/events/).
- [Pydantic v2 migration](https://docs.pydantic.dev/latest/migration/).
- [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/).
