# Контекст задач и HTTP-запросов

[Справочник](README.md) · [Конфигурация](configuration.md)

**Уровень:** средний → продвинутый. Предпосылки: bind, contextvars, async и middleware. Сверено 2026-11-06 со structlog 26.1.0. Выполнено 2026-11-06: async-изоляция и FastAPI success/error проверены двумя тестами на Python 3.14.7, structlog 26.1.0, FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0, pytest 9.2.0, pytest-asyncio 1.4.1.post1. Django-проект не запускался. Все файлы используют `demo_logging.py` с соседней страницы.

- [Локальный и контекстный bind](#локальный-и-контекстный-bind)
- [FastAPI: граница запроса](#fastapi-граница-запроса)
- [Django: подключение middleware](#django-подключение-middleware)

## Локальный и контекстный bind

`log.bind()` возвращает новый logger. Для временного общего контекста используй `bound_contextvars`, который восстанавливает прежние значения. `clear_contextvars()` нужен на границе новой работы, чтобы не унаследовать поля прошлого запроса.

Полный `demo_context.py`; зависимости: `structlog`, для тестов `pytest`, `pytest-asyncio`.

<!-- example: structlog/demo_context.py -->
```python
import asyncio

import structlog
from structlog.contextvars import bound_contextvars, clear_contextvars


async def process_item(item_id):
    with bound_contextvars(item_id=item_id):
        log = structlog.get_logger()
        await log.ainfo("item_started")
        await asyncio.sleep(0)
        await log.ainfo("item_completed")


async def run_tasks():
    clear_contextvars()
    try:
        with bound_contextvars(request_id="training-request"):
            await asyncio.gather(process_item(1), process_item(2))
        structlog.get_logger().info("outside")
    finally:
        clear_contextvars()
```

Полный `test_context.py`:

<!-- example: structlog/test_context.py -->
```python
import io
import json

import pytest

from demo_context import run_tasks
from demo_logging import configure_logging


@pytest.mark.asyncio
async def test_task_context_isolation_and_cleanup():
    stream = io.StringIO()
    configure_logging(stream)
    await run_tasks()
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    for item_id in (1, 2):
        selected = [item for item in events if item.get("item_id") == item_id]
        assert [item["event"] for item in selected] == ["item_started", "item_completed"]
        assert all(item["request_id"] == "training-request" for item in selected)
    assert events[-1]["event"] == "outside"
    assert "item_id" not in events[-1]
    assert "request_id" not in events[-1]
```

Ожидаются независимые item_id, общий request_id внутри задач и отсутствие обоих полей снаружи. Порядок событий **между** задачами не фиксируется. Прежний `structlog.threadlocal` устарел; для новых примеров используй contextvars. В гибридном sync/async приложении контексты могут быть изолированы: изменение из синхронной зависимости не обязано вернуться в async middleware. Проверяй фактический путь, не обещай автоматическое распространение во все потоки.

## FastAPI: граница запроса

Полный `demo_web.py`; зависимости: `fastapi`, `httpx2`, `structlog`. Используется ASGI middleware, чтобы не добавлять ограничения распространения contextvars от BaseHTTPMiddleware.

<!-- example: structlog/demo_web.py -->
```python
from uuid import uuid4

import structlog
from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        clear_contextvars()
        request_id = uuid4().hex
        bind_contextvars(request_id=request_id, method=scope["method"], path=scope["path"])
        log = structlog.get_logger()
        log.info("request_started")

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message = {**message, "headers": headers}
                log.info("response_started", status_code=message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
            log.info("request_completed")
        except Exception:
            log.exception("request_failed")
            raise
        finally:
            clear_contextvars()


app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
async def root():
    structlog.get_logger().info("handler_executed")
    return {"ok": True}


@app.get("/fail")
async def fail():
    raise RuntimeError("training failure")
```

Полный `test_web.py`:

<!-- example: structlog/test_web.py -->
```python
import io
import json

from fastapi.testclient import TestClient

from demo_logging import configure_logging
from demo_web import app


def test_request_context_and_failure():
    stream = io.StringIO()
    configure_logging(stream)
    with TestClient(app, raise_server_exceptions=False) as client:
        first = client.get("/")
        assert first.status_code == 200
        assert client.get("/fail").status_code == 500
        second = client.get("/")
        assert second.status_code == 200
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    ids = [item["request_id"] for item in events if item["event"] == "request_started"]
    assert len(ids) == len(set(ids)) == 3
    assert first.headers["X-Request-ID"] == ids[0]
    assert second.headers["X-Request-ID"] == ids[2]
    failed = [item for item in events if item["event"] == "request_failed"]
    assert len(failed) == 1
    assert failed[0]["request_id"] == ids[1]
    assert "RuntimeError" in failed[0]["exception"]
```

Запуск всех тестов темы: `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`. Для ручного сервера создай конфигурацию логирования перед запуском приложения: `configure_logging()` из `demo_logging`; не делай это заново для каждого запроса. `response_started` означает отправку заголовков, `request_completed` — возврат ASGI-приложения; смысл этих событий различается для streaming. Необработанная ошибка может получить ответ `500` от внешнего ServerErrorMiddleware после очистки этого контекста.

## Django: подключение middleware

Этот вариант **сверен с документацией, но Django-проект не запускался**. Подключи стандартную интеграцию через `LOGGING`/`ProcessorFormatter` и цепочку `wrap_for_formatter`, как в [проверенном stdlib-рецепте](configuration.md#интеграция-со-stdlib-logging). Не вызывай настройку logging на каждый запрос.

Фрагмент модуля middleware для синхронного Django-приложения; в `MIDDLEWARE` ставится после AuthenticationMiddleware, если нужен `request.user`. Остальные settings/URL проекта здесь не определяются.

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

Не обещай ловить все ошибки Django одним `except` вокруг get_response: framework может преобразовать исключение в HTTP-ответ раньше. Для traceback настрой обработку исключений/framework logging отдельно. Для async middleware реализуй соответствующий протокол, а не вызывай этот синхронный класс напрямую из event loop.

Источники: [structlog contextvars](https://www.structlog.org/en/stable/contextvars.html), [async logging API](https://www.structlog.org/en/stable/api.html), [Starlette ASGI middleware и ограничения BaseHTTPMiddleware](https://starlette.dev/middleware/), [Django middleware](https://docs.djangoproject.com/en/6.0/topics/http/middleware/).
