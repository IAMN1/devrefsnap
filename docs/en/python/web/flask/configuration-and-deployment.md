<a id="конфигурация-бд-и-развёртывание-flask"></a>
# Flask configuration, databases, and deployment

[Русский](../../../../ru/python/web/flask/configuration-and-deployment.md)

Use this page to load configuration, close SQLite connections, and choose a WSGI startup method.
The database example creates data only in the test's temporary directory.

| Task | Technique | Example / details |
| --- | --- | --- |
| Define configuration precedence | Defaults → environment → test | [Settings](#configure-before-startup) |
| Scope a connection to a context | `g` and `teardown_appcontext` | [Module and test](#connection-lifecycle) |
| Choose production startup | WSGI server and trusted proxy | [Deployment](#development-and-production) |

Advanced level. Requires factories, Flask contexts, and SQL transactions.
[Flask reference](README.md).

<a id="конфигурация-до-запуска"></a>
## Configure before startup

The [factory](application.md) loads defaults first.
Then `from_prefixed_env()` loads `FLASK_...` variables.
Explicit test configuration is loaded last.
Provide environment variables through the startup system or secret store.
Keep production keys out of Git.
`SECRET_KEY` signs the session cookie.
Avoid storing sensitive data in the cookie under the assumption that its contents are encrypted.

| Setting | When needed |
| --- | --- |
| `TESTING` | Needed in tests. Production requires its own configuration |
| `MAX_CONTENT_LENGTH` | Limits the request body. Coordinate the limit with the proxy |
| `SECRET_KEY` | Signed sessions require an unpredictable key. Manage rotation |
| `SESSION_COOKIE_SECURE` | Send the cookie only over HTTPS |
| `SESSION_COOKIE_HTTPONLY` | Restrict browser JavaScript access to the cookie |
| `SESSION_COOKIE_SAMESITE` | Choose a cross-site policy. Additional CSRF protection may be required |
| `TRUSTED_HOSTS` | Restrict accepted Host values where suitable for the architecture |

For extensions, create the object without an app.
After loading configuration, call `extension.init_app(app)` within the factory.
Avoid creating one global connection for all requests and workers.

<a id="жизненный-цикл-соединения"></a>
## Connection lifecycle

The complete additional module `flask_db.py` follows.
Schema creation is separate from opening a connection.
The application sets the database path.
Parameterize queries containing user data.
Commit explicitly.
Resource closure should not accidentally commit successful or failed HTTP requests.

[`flask/flask_db.py`](../../../../../examples/python/web/flask/flask_db.py)

After loading configuration, call `flask_db.init_app(app)` in the factory.
This application uses SQLite through the standard `sqlite3` module.
SQLAlchemy requires its own Session and transaction boundaries.
`g` belongs to the current app context.
`g` provides no shared storage between processes.

Save the complete runnable `test_flask_db.py` next to `flask_app.py` and `flask_db.py`.

[`flask/test_flask_db.py`](../../../../../examples/python/web/flask/test_flask_db.py)

Run `python -m pytest -q test_flask_db.py`.
Expect **1 passed**.
The test checks connection reuse within a context.
The test checks connection closure.
The test checks rollback of an uncommitted insert.
The test checks the next context's independence.
Only a SQLite file in pytest's temporary directory is created.
Teardown closes the resource regardless of request success.
Define the business transaction separately.
Migrations and production backups fall outside this example's scope.
Use [SQLAlchemy](../../databases/sqlalchemy/README.md) and [SQLite](../../../databases/relational/sqlite/README.md) for those tasks.

<a id="разработка-и-production"></a>
## Development and production

`flask run --debug` starts the built-in development server, reloader, and debugger.
Keep these components confined to development.
Flask is a WSGI application.
Choose the server and hosting separately.
For example, Gunicorn can run on supported Unix systems.
Waitress is another option when its model and platform support suit the application.
Server installation and worker/thread parameters require separate checks.
The following reference command assumes Gunicorn is installed.

```text
gunicorn --bind 127.0.0.1:8000 'flask_app:create_app()'
```

The command requires an installed Gunicorn and an importable `flask_app`.
A reverse proxy can provide TLS and limit requests.
Health checks, timeouts, graceful shutdown, and log collection are required.
Enable `ProxyFix` only behind a trusted proxy with the exact number of hops.
Otherwise, a client can spoof forwarded headers.
Complete setup and route registration before requests arrive.
Every worker should start with the same app.

Async views require the appropriate Flask installation and retain WSGI worker behavior.
Avoid starting durable background tasks with `asyncio.create_task()` inside a view.
Use a separate worker or queue with defined retries and task state.

<a id="источники"></a>
## Sources

[Configuration](https://flask.palletsprojects.com/en/stable/config/),
[database tutorial](https://flask.palletsprojects.com/en/stable/tutorial/database/),
[deploying](https://flask.palletsprojects.com/en/stable/deploying/),
[Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/),
[proxy](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/),
[async](https://flask.palletsprojects.com/en/stable/async-await/).
