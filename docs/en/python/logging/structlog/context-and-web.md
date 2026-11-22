<a id="контекст-задач-и-http-запросов"></a>
# Task and HTTP request context

[Русский](../../../../ru/python/logging/structlog/context-and-web.md)

Use this page when several functions or concurrent tasks need to log the same request identifier.
Clear context at the operation boundary, including when the operation fails.

| Task | Technique | Example or details |
| --- | --- | --- |
| Add temporary fields | `bound_contextvars` | [Tasks and isolation checks](#local-and-contextual-binding) |
| Associate HTTP request events | ASGI middleware and `request_id` | [FastAPI](#fastapi-request-boundary) |
| Integrate synchronous Django | Middleware after authentication | [Snippet and limitations](#django-middleware-integration) |

[Reference](README.md) · [Configuration](configuration.md)

The level is intermediate to advanced.
Prerequisites include bind, contextvars, async, and middleware.
Use Python 3.14 and [demo_logging.py](configuration.md#standalone-configuration) for logger setup.
The task and web examples list dependencies separately.

- [Local and contextual binding](#local-and-contextual-binding)
- [FastAPI request boundary](#fastapi-request-boundary)
- [Django middleware integration](#django-middleware-integration)

<a id="локальный-и-контекстный-bind"></a>
## Local and contextual binding

`log.bind()` returns a new logger.
Use `bound_contextvars` for temporary shared context.
The context manager restores previous values.
Call `clear_contextvars()` at the start of a new operation to clear fields inherited from a previous request.

The complete `demo_context.py` follows.
In the practice environment, run `python -m pip install 'structlog==26.1.0' 'pytest==9.2.0' 'pytest-asyncio==1.5.0'`.

[`structlog/demo_context.py`](../../../../../examples/python/logging/structlog/demo_context.py)

Complete `test_context.py` follows.

[`structlog/test_context.py`](../../../../../examples/python/logging/structlog/test_context.py)

Run `python -m pytest -q test_context.py -o asyncio_default_fixture_loop_scope=function`.
Inside the tasks, expect separate item_id values and a shared request_id.
Outside, both fields should be absent.
Event order **between** tasks is unspecified.
`structlog.threadlocal` is deprecated.
Use contextvars for new code.
In a hybrid sync and async application, contexts can be isolated.
A change in a synchronous dependency may stay invisible to async middleware.
Test the actual execution path.
Check context propagation into each thread explicitly.

<a id="fastapi-граница-запроса"></a>
## FastAPI request boundary

The complete `demo_web.py` follows.
In a separate environment, run `python -m pip install 'structlog==26.1.0' 'fastapi==0.165.0' 'starlette==1.10.0' 'httpx2==2.16.2' 'pytest==9.2.0'`.
The example uses ASGI middleware to avoid BaseHTTPMiddleware's additional contextvars propagation limits.

[`structlog/demo_web.py`](../../../../../examples/python/logging/structlog/demo_web.py)

Complete `test_web.py` follows.

[`structlog/test_web.py`](../../../../../examples/python/logging/structlog/test_web.py)

Run `python -m pytest -q test_web.py`.
For a manual server run, configure logging before starting the application with `configure_logging()` from `demo_logging`.
Keep configuration outside per-request handling.
`response_started` records the `http.response.start` message before the middleware forwards it.
`request_completed` means the ASGI application has returned.
These events can occur at different times during streaming.
For an unhandled error, an outer ServerErrorMiddleware can send a `500` response after this context has been cleared.

<a id="django-подключение-middleware"></a>
## Django middleware integration

Set up standard logging integration through `LOGGING`, `ProcessorFormatter`, and a `wrap_for_formatter` chain, as in the [stdlib recipe](configuration.md#integrate-with-standard-library-logging).
Configure logging once at startup.

This middleware module snippet is for a synchronous Django application.
If you need `request.user`, put the middleware after AuthenticationMiddleware in `MIDDLEWARE`.
Configure the rest of the project's settings and URLs separately.

```python
from uuid import uuid4

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars


class StructlogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_contextvars()
        user = getattr(request, "user", None)
        bind_contextvars(request_id=uuid4().hex, path=request.path, method=request.method,
                         user_id=user.pk if user is not None and user.is_authenticated else None)
        log = structlog.get_logger()
        try:
            response = self.get_response(request)
            log.info("request_completed", status_code=response.status_code)
            return response
        finally:
            clear_contextvars()
```

Django can turn exceptions into HTTP responses before they reach an `except` around get_response.
Configure framework logging or exception handling separately to preserve tracebacks.
For async middleware, implement the async protocol.
Keep this synchronous class outside the event loop.

See [structlog contextvars](https://www.structlog.org/en/stable/contextvars.html), [async logging API](https://www.structlog.org/en/stable/api.html), [Starlette ASGI middleware and BaseHTTPMiddleware limitations](https://starlette.dev/middleware/), and [Django middleware](https://docs.djangoproject.com/en/6.0/topics/http/middleware/).
