<a id="тестирование-flask-без-сетевого-сервера"></a>
# Test Flask without a network server

[Русский](../../../../ru/python/web/flask/testing.md)

Use this page to check Flask responses, invalid input, and independent configurations without a network server.
The client executes WSGI requests in process.

| Task | Technique | Example / details |
| --- | --- | --- |
| Check JSON and request errors | `app.test_client`, `response.json` | [Complete test_flask_app.py](#complete-check-suite) |
| Check HTTP headers and HTML | 405 Allow, Jinja escaping | [Complete suite](#complete-check-suite) |
| Choose a context or separate database | `app_context`, a path per test | [Test boundaries](#test-context-and-configuration) |

Intermediate level. Requires [flask_app.py](application.md), Flask, and pytest in the environment.
[Flask reference](README.md).

<a id="полный-набор-проверок"></a>
## Complete check suite

Save the complete example next to the application as `test_flask_app.py`.
Run `python -m pytest -q test_flask_app.py`.
All data is synthetic.
The tests do not open a network port.

[`flask/test_flask_app.py`](../../../../../examples/python/web/flask/test_flask_app.py)

Expect **13 passed**.
The tests check successful responses, invalid data, and routing.
The tests check media types, body limits, and HTTP header preservation.
The tests check HTML escaping and configuration independence.
A route with authorization requires separate tests for missing or insufficient roles.
This practice app has no authentication.

<a id="контекст-и-конфигурация-тестов"></a>
## Test context and configuration

`app.test_client()` calls the WSGI application in process.
This client does not check reverse proxies, TLS, actual WSGI workers, network timeouts, or multiprocess state.
Use `app.test_cli_runner()` for CLI tests.
`TESTING=True` helps expose unexpected exceptions in tests.
The application still converts expected HTTPExceptions into HTTP responses.

To access app resources outside a request, use `with app.app_context():` in setup or CLI code.
To check routing, methods, or bodies, send an actual request through the client.
If a test uses a database, give the test its own path or transaction.
Check test-data cleanup.
[SQLite lifecycle](configuration-and-deployment.md#connection-lifecycle) contains a separate resource-closure test.

<a id="источники"></a>
## Sources

[Testing Flask](https://flask.palletsprojects.com/en/stable/testing/).
