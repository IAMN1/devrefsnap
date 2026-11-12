<a id="создать-http-api-с-проверкой-данных"></a>
# Create an HTTP API with data validation

[Русский](../../../../ru/python/web/fastapi/http-api.md)

Use this page to perform complete CRUD operations and check consistency between input and output models.
Practice items are stored in one process's memory.

| Task | Technique | Example |
| --- | --- | --- |
| Reproduce CRUD | Path/query/body, models, controlled errors | [Complete main.py](#http-api-with-validation) |
| Understand a PATCH update | Merge fields and validate the model again | [Short card](recipes.md#http-api-with-validation) |
| Check errors and password omission | `TestClient` and independent expected values | [Complete tests](testing-lab.md#synchronous-testclient) |

[HTTP cards](recipes.md) · [FastAPI reference](README.md) · [Checks](testing.md)

Beginner to intermediate level.
Running the example requires Python 3.14, FastAPI 0.162.0, and Pydantic 2.14.3.

<a id="http-api-с-валидацией"></a>
## HTTP API with validation

**Prerequisites** — functions, types, and HTTP methods.

In a separate environment, run `python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]' 'pydantic[email]==2.14.3'`.
Create the complete `main.py` file.

[`main.py`](../../../../../examples/python/web/fastapi/main.py)

Start the server and send requests from another terminal.

```bash
uvicorn main:app --reload
```

```bash
curl -i -X POST http://127.0.0.1:8000/items -H 'Content-Type: application/json' -d '{"name":"Book","price":25,"tags":["python"]}'
curl 'http://127.0.0.1:8000/items?q=Book&tags=python&limit=5'
curl -i -X PATCH http://127.0.0.1:8000/items/1 -H 'Content-Type: application/json' -d '{"price":30}'
curl -i http://127.0.0.1:8000/items/999
```

See how to read the status, headers, and body in the [`curl` and `jq` example](../../../tools/http-json.md#inspect-the-http-response).

Creation returns `201` with `id=1`.
The list query returns one item.
PATCH changes the price to `30`.
Requesting a missing item returns `404`.
A negative price or a `premium` item cheaper than `100` returns `422`.
`DELETE` returns `204` without a body.
The `/user-preview` route demonstrates output-model password filtering.
The route neither saves the user nor registers an account.

The data lasts until restart within one process.
This store provides neither persistence nor concurrent-access handling.
The example uses `float` for simplicity.
Exact monetary calculations require a separately chosen number model.
PATCH first merges fields.
Then PATCH validates the complete model again.
`model_copy(update=...)` alone does not perform this validation.
Explicit `null` is accepted only for final-model fields that allow `None`.

Price and tax must be finite numbers.
`allow_inf_nan=False` rejects infinity and NaN.
`1e999` can become `inf` during JSON parsing.
The error handler therefore returns only `loc`, `msg`, and `type`.
The handler excludes the original `input` and `ctx`.
Those values can themselves be impossible to serialize as JSON.
PATCH revalidation uses the same format.

Sources include [parameter constraints](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [Pydantic v2 validators](https://docs.pydantic.dev/latest/concepts/validators/), [Field constraints](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field), [body updates](https://fastapi.tiangolo.com/tutorial/body-updates/), [output models](https://fastapi.tiangolo.com/tutorial/response-model/), and [error handling](https://fastapi.tiangolo.com/tutorial/handling-errors/).
