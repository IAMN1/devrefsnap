<a id="http-api-параметры-и-файлы"></a>
# HTTP APIs, parameters, and files

[Русский](../../../../ru/python/web/fastapi/recipes.md)

Use this page to review HTTP input, dependencies, multipart handling, and CORS.
Each card shows one change. Complete applications are separated by task.

| Task | Technique | Card / complete example |
| --- | --- | --- |
| Partially update an item and validate the result | Merge fields, then call `model_validate` | [PATCH](#http-api-with-validation) · [Complete CRUD](http-api.md) |
| Reuse parameters or object lookup | `Depends` and sub-dependencies | [Dependencies](#how-dependencies-work) |
| Check a header before the handler | `dependencies=[Depends(...)]` | [One standalone file](#check-a-header-before-the-handler) |
| Accept a file with a limit on content read | Read in chunks with `UploadFile.read` | [Card](#forms-and-file-uploads) · [Complete application](uploads.md) |
| Allow a browser origin and time processing | CORS and middleware | [Card](#middleware-and-cors) · [Complete application](middleware.md) |

[Quick reference](README.md) · [Tests](testing.md)

Beginner to intermediate level.
Prerequisites include functions, type annotations, and HTTP methods.
Environment includes Python 3.14, FastAPI 0.162.0, and Pydantic 2.14.3.
Setup and complete code are on each application's page. Each task needs only its own packages.

<a id="http-api-с-валидацией"></a>
## HTTP API with validation

**Situation** — the Book item costs `25`. PATCH supplies only a new price of `30`.
Preserve the other fields and validate the final model.
**Change** — merge stored and supplied fields, then call `model_validate`.
The `patch_item` handler snippet comes from the [complete `main.py`](http-api.md#http-api-with-validation).

```python
current = existing_item(item_id)
data = {**current.model_dump(exclude={"id"}), **patch.model_dump(exclude_unset=True)}
try:
    validated = ItemCreate.model_validate(data)
except ValidationError as exc:
    raise HTTPException(422, validation_details(exc)) from exc
items[item_id] = ItemOut(id=item_id, **validated.model_dump())
```

Here, `patch` is a validated `ItemPatch`, and `items` is the complete application's item dictionary.
**Result** — the price changes to `30`, and the name remains `Book`.
An invalid result returns `422` before the dictionary changes.
`model_copy(update=...)` itself does not validate updates.
The in-memory store provides neither persistence nor concurrent-access handling.
[Complete CRUD, models, responses, and startup](http-api.md) · [PATCH checks](testing-lab.md#synchronous-testclient).

<a id="как-устроены-зависимости"></a>
## How dependencies work

**Level** — intermediate. The [complete `main.py`](http-api.md#http-api-with-validation) includes the following dependencies.

- `search_query` is a dependency function. `effective_query` is a dependency with a sub-dependency and an actual `Cookie` parameter.
- `Pagination` is a dependency class. FastAPI reads its constructor parameters.
- `existing_item` centralizes lookup and `404`. The read handler receives the object already found.

<a id="проверка-заголовка-перед-обработчиком"></a>
### Check a header before the handler

Here, a dependency is a function that FastAPI calls through `Depends` before the handler.
If the handler does not need the check's result, put the check in `dependencies`.
The standalone `header_dependency.py` file follows.
Its dependencies are the same as for `minimal.py`.

[`header_dependency.py`](../../../../../examples/python/web/fastapi/header_dependency.py)

`Header()` sets the parameter source to the `X-Client` HTTP header.
`Annotated` associates the `str` type with the `Header()` configuration.
`Depends(verify_client)` passes the function object to FastAPI without calling it.
FastAPI first validates the required header, then calls `verify_client`.
If the dependency completes without an error, FastAPI calls `checked`.
The decorator uses the check without passing its result into `checked`.

Run `uvicorn header_dependency:app --reload`.
The request `curl -H 'X-Client: training-client' http://127.0.0.1:8000/checked` returns `200`.
An incorrect header value returns `400`.
A missing required header returns `422`.
The example demonstrates header validation.
This header cannot serve as a secret API key or replace [authentication](authentication.md).
[Override this check in a test](testing.md#dependency-override) if the test should exercise only the handler.

Sources include [Depends](https://fastapi.tiangolo.com/tutorial/dependencies/), [sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/), and [decorator-level checks](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).

<a id="формы-и-загрузка-файлов"></a>
## Forms and file uploads

**Situation** — read one uploaded file in chunks, rejecting content over 1 MiB.
**Change** — track the accumulated size and stop reading with `413`.
The `measure(file)` snippet comes from the [complete `uploads.py`](uploads.md#forms-and-file-uploads).

```python
async def measure(file: UploadFile):
    size = 0
    try:
        while chunk := await file.read(64 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                raise HTTPException(413, "Файл больше 1 MiB")
        return {"filename": file.filename, "size": size}
    finally:
        await file.close()
```

`file` is an `UploadFile`, and `MAX_BYTES = 1024 * 1024`.
Import `UploadFile` and `HTTPException` from FastAPI, as in the complete application.
**Result** — a file containing `b"abc"` has size `3`. A file over the limit returns `413`.
The limit is checked after multipart parsing and does not limit the complete HTTP request.
Set a total body limit and file-count limit on the server or proxy.
[Forms, one or several files, and startup](uploads.md) · [Complete checks](testing-lab.md#files-and-middleware).

<a id="middleware-и-cors"></a>
## Middleware and CORS

**Situation** — a browser at `http://localhost:3000` must read the API with credentials.
**Change** — list the origin explicitly.
The snippet comes from the [complete `middleware_app.py`](middleware.md#middleware-and-cors).

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Process-Time"],
)
```

`app` is a `FastAPI` instance, and `CORSMiddleware` is imported from `fastapi.middleware.cors`.
**Result** — the allowed origin receives CORS headers. Other origins do not receive permission for browser access.
An origin includes scheme, host, and port. `127.0.0.1` differs from `localhost`.
CORS does not verify the user.
[Complete application with a timer](middleware.md) · [Preflight and rejection checks](testing-lab.md#files-and-middleware).
