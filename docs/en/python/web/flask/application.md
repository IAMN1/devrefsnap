<a id="factory-blueprint-запрос-и-ответ-flask"></a>
# Flask factories, Blueprints, requests, and responses

[Русский](../../../../ru/python/web/flask/application.md)

Use this page to create an independent Flask instance and handle a JSON request.
The complete application uses fixed practice data without a database or authentication.

| Task | Technique | Example / details |
| --- | --- | --- |
| Create an app and attach routes | Factory and Blueprint | [Complete flask_app.py](#complete-application) |
| Validate JSON and return an HTTP error | `request.get_json`, `abort` | [Application](#complete-application) · [Tests](testing.md) |
| Start a local server | `flask --app ... run --debug` | [Running](#run-and-check) |
| Choose a response form | Query, HTML, cookie, redirect | [API table](#other-request-and-response-forms) |

Beginner and intermediate levels. Requires Flask 3.1.x and Python.
[Flask reference](README.md).

<a id="полное-приложение"></a>
## Complete application

Save the complete example as `flask_app.py` in a separate practice directory.
The example intentionally uses no storage.
The item route returns one fixed response.
The greet route transforms input.
The example demonstrates the API.
The example implements no user system or authentication mechanism.

[`flask/flask_app.py`](../../../../../examples/python/web/flask/flask_app.py)

`GET /api/items/1` returns 200 and `{"id":1,"name":"apple"}`.
An unknown ID returns 404.
`POST /api/greet` with `{"name":" Alice "}` returns 200 and `Hello, Alice`.
An unsuitable media type returns 415.
Invalid JSON or an empty name returns 400.

The HTTPException handler preserves the original response and its headers, including `Allow` for 405.
Avoid converting every exception into a successful JSON response.
Unexpected errors should be logged and return 500.
The client should not receive the traceback.
A global HTTPException handler also affects router errors.
A Blueprint-specific 404 handler cannot catch an unknown URL before a Blueprint is selected.

<a id="запуск-и-проверка"></a>
## Run and check

Run these shell command snippets in the file's directory.

```bash
python -m flask --app flask_app:create_app routes
python -m flask --app flask_app:create_app run --debug
```

`run --debug` starts a local development server.
Keep the debugger inaccessible from outside.
After starting the server manually, run these commands in a separate terminal.

```bash
curl --fail-with-body http://127.0.0.1:5000/api/items/1
curl --fail-with-body -H 'Content-Type: application/json' \
  -d '{"name":"Alice"}' http://127.0.0.1:5000/api/greet
```

Automated checks are on the [next page](testing.md).

<a id="другие-формы-запроса-и-ответа"></a>
## Other request and response forms

| Task | API | Limitation |
| --- | --- | --- |
| Query string | `request.args.get("page", default=1, type=int)` | Returns the default on conversion failure. Implement strict validation separately |
| HTML form | `request.form` | Browser mutations require CSRF protection |
| Uploaded file | `request.files` | Limit the size. Treat client-provided names and types as untrusted |
| URL by endpoint | `url_for("api.get_item", item_id=1)` | Requires a suitable app/request context |
| Redirect | `redirect(url_for(...))` | Prevent arbitrary external redirects from user-provided URLs |
| HTML | `render_template("page.html", name=name)` | Keep Jinja autoescape enabled. Avoid `safe` for untrusted text |
| JSON | `jsonify(...)` or a dict/list | Values must be JSON-serializable. A tuple can include the status code |
| Cookie/session | `session["key"] = value` | Requires SECRET_KEY. The cookie is signed, but its contents are readable by the client |

The example uses `render_template_string` to fit the code in one file.
Applications usually store templates in `templates/`.
The application then loads templates through `render_template`.
Here, `templates/` means the application's directory. The repository's templates serve a separate purpose.

<a id="источники"></a>
## Sources

[Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/),
[Blueprint](https://flask.palletsprojects.com/en/stable/blueprints/),
[factory](https://flask.palletsprojects.com/en/stable/patterns/appfactories/),
[error handling](https://flask.palletsprojects.com/en/stable/errorhandling/).
