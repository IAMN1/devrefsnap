# Контекст задач и HTTP-запросов

Откройте страницу, если несколько функций или конкурентных задач должны писать общий идентификатор запроса.
Контекст должен очищаться на границе работы, включая ошибочный выход.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Добавить временные поля | `bound_contextvars` | [Задачи и проверки изоляции](#локальный-и-контекстный-bind) |
| Связать события HTTP-запроса | ASGI middleware и `request_id` | [FastAPI](#fastapi-граница-запроса) |
| Подключить sync Django | Middleware после аутентификации | [Фрагмент и ограничения](#django-подключение-middleware) |

[Справочник](README.md) · [Конфигурация](configuration.md)

**Уровень:** средний → продвинутый.
Предпосылки: bind, contextvars, async и middleware.
Окружение: Python 3.14.7, structlog 26.1.0, FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0, pytest 9.2.0, pytest-asyncio 1.4.1.post1.
Все файлы используют `demo_logging.py` с соседней страницы.

- [Локальный и контекстный bind](#локальный-и-контекстный-bind)
- [FastAPI: граница запроса](#fastapi-граница-запроса)
- [Django: подключение middleware](#django-подключение-middleware)

## Локальный и контекстный bind

`log.bind()` возвращает новый logger.
Для временного общего контекста используйте `bound_contextvars`.
Контекстный менеджер восстанавливает прежние значения.
На границе новой работы вызывайте `clear_contextvars()`.
Этот вызов предотвращает наследование полей прошлого запроса.

Ниже приведён полный пример `demo_context.py`.
Зависимость: `structlog`.
Для тестов нужны `pytest` и `pytest-asyncio`.

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

Внутри задач ожидаются независимые item_id и общий request_id.
Снаружи ожидается отсутствие обоих полей.
Порядок событий **между** задачами не фиксируется.
Прежний `structlog.threadlocal` устарел.
Для новых примеров используйте contextvars.
В гибридном sync/async приложении контексты могут быть изолированы.
Изменение из синхронной зависимости не обязано вернуться в async middleware.
Проверяйте фактический путь.
Не обещайте автоматическое распространение во все потоки.

## FastAPI: граница запроса

Ниже приведён полный пример `demo_web.py`.
Зависимости: `fastapi`, `httpx2`, `structlog`.
Пример использует ASGI middleware, чтобы не добавлять ограничения распространения contextvars от BaseHTTPMiddleware.

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

Запустите все тесты темы: `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`.
Для ручного сервера настройте логирование перед запуском приложения через `configure_logging()` из `demo_logging`.
Не повторяйте настройку для каждого запроса.
`response_started` означает отправку заголовков.
`request_completed` означает возврат ASGI-приложения.
При streaming смысл этих событий различается.
Необработанная ошибка может получить ответ `500` от внешнего ServerErrorMiddleware после очистки этого контекста.

## Django: подключение middleware

Подключите стандартную интеграцию через `LOGGING`/`ProcessorFormatter` и цепочку `wrap_for_formatter`, как в [рецепте stdlib](configuration.md#интеграция-со-stdlib-logging).
Не вызывайте настройку logging на каждый запрос.

Ниже приведён фрагмент модуля middleware для синхронного Django-приложения.
Если нужен `request.user`, поставьте middleware в `MIDDLEWARE` после AuthenticationMiddleware.
Остальные settings/URL проекта здесь не определяются.

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

Не рассчитывайте перехватить все ошибки Django одним `except` вокруг get_response.
Framework может преобразовать исключение в HTTP-ответ раньше.
Для traceback настройте обработку исключений/framework logging отдельно.
Для async middleware реализуйте соответствующий протокол.
Не вызывайте этот синхронный класс напрямую из event loop.

Источники: [structlog contextvars](https://www.structlog.org/en/stable/contextvars.html), [async logging API](https://www.structlog.org/en/stable/api.html), [Starlette ASGI middleware и ограничения BaseHTTPMiddleware](https://starlette.dev/middleware/), [Django middleware](https://docs.djangoproject.com/en/6.0/topics/http/middleware/).
