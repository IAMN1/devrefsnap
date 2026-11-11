
# Контекст задач и HTTP-запросов

[English](../../../../en/python/logging/structlog/context-and-web.md)

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
Используйте Python 3.14 и [demo_logging.py](configuration.md#самостоятельная-конфигурация) для настройки логгера.
Зависимости задач и веб-примера указаны отдельно ниже.

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
В учебном окружении выполните `python -m pip install 'structlog==26.1.0' 'pytest==9.2.0' 'pytest-asyncio==1.4.1.post1'`.

[`structlog/demo_context.py`](../../../../../examples/python/logging/structlog/demo_context.py)

Полный `test_context.py`:

[`structlog/test_context.py`](../../../../../examples/python/logging/structlog/test_context.py)

Запустите `python -m pytest -q test_context.py -o asyncio_default_fixture_loop_scope=function`.
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
В отдельном окружении выполните `python -m pip install 'structlog==26.1.0' 'fastapi==0.162.0' 'starlette==1.10.0' 'httpx2==2.16.0' 'pytest==9.2.0'`.
Пример использует ASGI middleware, чтобы не добавлять ограничения распространения contextvars от BaseHTTPMiddleware.

[`structlog/demo_web.py`](../../../../../examples/python/logging/structlog/demo_web.py)

Полный `test_web.py`:

[`structlog/test_web.py`](../../../../../examples/python/logging/structlog/test_web.py)

Запустите `python -m pytest -q test_web.py`.
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
