# Настроить вывод и процессоры

[Справочник](README.md) · [Контекст и веб](context-and-web.md)

**Уровень:** базовый → продвинутый. Предпосылки: словари, logging, обработка исключений. Сверено 2026-11-06 со structlog 26.1.0. Выполнено 2026-11-06: 5 тестов страницы прошли на Python 3.14.7, structlog 26.1.0, pytest 9.2.0, включая сохранённый exc_info вне except. Установи `structlog` и `pytest` в отдельное окружение; сохраняй все файлы темы рядом. Производительность под нагрузкой не измерялась.

- [Самостоятельная конфигурация](#самостоятельная-конфигурация)
- [Интеграция со stdlib logging](#интеграция-со-stdlib-logging)
- [Порядок и стоимость](#порядок-и-стоимость)

## Самостоятельная конфигурация

Полный `demo_logging.py`. Renderer выбирается один раз; чувствительные поля маскируются рекурсивно по заданным именам.

<!-- example: structlog/demo_logging.py -->
```python
import logging
import sys

import structlog

SENSITIVE_KEYS = {"password", "token", "api_key"}


def redact_value(value):
    if isinstance(value, dict):
        return {key: "***" if str(key).lower() in SENSITIVE_KEYS else redact_value(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    return value


def redact(logger, method_name, event_dict):
    return redact_value(event_dict)


def service(logger, method_name, event_dict):
    event_dict.setdefault("service", "training")
    return event_dict


def configure_logging(stream=None, *, output="json", level=logging.INFO):
    if stream is None:
        stream = sys.stdout
    processors = [structlog.contextvars.merge_contextvars, structlog.processors.add_log_level,
                  structlog.processors.TimeStamper(fmt="iso", utc=True), service,
                  structlog.processors.StackInfoRenderer()]
    if output == "json":
        processors += [structlog.processors.format_exc_info, redact, structlog.processors.JSONRenderer()]
    elif output == "console":
        processors += [redact, structlog.dev.ConsoleRenderer(colors=False)]
    elif output == "keyvalue":
        processors += [structlog.processors.format_exc_info, redact,
                       structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"], drop_missing=True)]
    else:
        raise ValueError("output должен быть json, console или keyvalue")
    structlog.configure(processors=processors, context_class=dict,
                        wrapper_class=structlog.make_filtering_bound_logger(level),
                        logger_factory=structlog.WriteLoggerFactory(file=stream),
                        cache_logger_on_first_use=True)
    return structlog.get_logger()


if __name__ == "__main__":
    log = configure_logging().bind(user_id=123)
    log.info("user_logged_in", credentials={"password": "training-password"})
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("calculation_failed")
```

Запуск: `python demo_logging.py`. Результат — две JSON-строки; пароль заменён на `***`, во второй есть `exception` с traceback. Маскирование действует только на перечисленные **ключи**, не на произвольные строки, traceback или неизвестные контейнеры: не помещай секрет в `event`/текст исключения, ожидая автоматического обнаружения.

Маскирование сохраняет тип tuple: служебный `exc_info`, сохранённый через `sys.exc_info()`, должен остаться кортежем, чтобы ConsoleRenderer восстановил traceback даже за пределами `except`.

Полный `test_logging.py`:

<!-- example: structlog/test_logging.py -->
```python
import io
import json
import logging
import sys

import pytest

from demo_logging import configure_logging


def test_json_bind_redaction_and_exception():
    stream = io.StringIO()
    parent = configure_logging(stream)
    child = parent.bind(user_id=1)
    child.info("login", payload=[{"password": "secret"}], token="secret-token")
    parent.info("parent")
    child.unbind("user_id").info("unbound")
    try:
        1 / 0
    except ZeroDivisionError:
        child.exception("failed")
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert events[0]["user_id"] == 1
    assert events[0]["payload"] == [{"password": "***"}]
    assert events[0]["token"] == "***"
    assert "user_id" not in events[1]
    assert "user_id" not in events[2]
    assert "ZeroDivisionError" in events[3]["exception"]
    with pytest.raises(KeyError):
        child.unbind("missing")


def test_level_guard_and_output_modes():
    stream = io.StringIO()
    log = configure_logging(stream, level=logging.INFO)
    evaluated = []
    if log.is_enabled_for(logging.DEBUG):
        evaluated.append("expensive")
        log.debug("debug", value=evaluated)
    assert evaluated == []
    assert stream.getvalue() == ""
    for output in ("console", "keyvalue"):
        stream = io.StringIO()
        configure_logging(stream, output=output).info("visible", answer=42)
        assert "visible" in stream.getvalue()
        assert "42" in stream.getvalue()
    with pytest.raises(ValueError):
        configure_logging(stream, output="unknown")


@pytest.mark.parametrize("output", ["json", "console"])
def test_saved_exception_tuple_outside_except(output):
    stream = io.StringIO()
    log = configure_logging(stream, output=output)
    try:
        1 / 0
    except ZeroDivisionError:
        saved = sys.exc_info()
    log.error("saved_failure", exc_info=saved)
    assert "ZeroDivisionError" in stream.getvalue()
    if output == "json":
        assert "Traceback" in json.loads(stream.getvalue())["exception"]
    else:
        assert "Traceback" in stream.getvalue()
```

## Интеграция со stdlib logging

Полный `demo_stdlib.py` настраивает только учебное имя logger. В приложении встрой такую конфигурацию в его штатную настройку, не очищай чужие handlers библиотечным импортом.

<!-- example: structlog/demo_stdlib.py -->
```python
import logging

import structlog

from demo_logging import redact, service


def configure_stdlib(stream):
    shared = [structlog.contextvars.merge_contextvars, structlog.stdlib.add_log_level,
              structlog.stdlib.add_logger_name, structlog.processors.TimeStamper(fmt="iso"), service]
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.format_exc_info, redact, structlog.processors.JSONRenderer()],
    )
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger = logging.getLogger("training")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    structlog.configure(
        processors=[structlog.stdlib.filter_by_level, *shared,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict, logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger, cache_logger_on_first_use=True,
    )
    return structlog.get_logger("training.structured"), logging.getLogger("training.plain")
```

Полный `test_stdlib.py` проверяет обе стороны одной цепочки:

<!-- example: structlog/test_stdlib.py -->
```python
import io
import json
import logging

from demo_stdlib import configure_stdlib


def test_foreign_and_structlog_share_json_format():
    stream = io.StringIO()
    structured, plain = configure_stdlib(stream)
    try:
        structured.info("structured_event", count=2)
        plain.info("plain %s", "event")
        events = [json.loads(line) for line in stream.getvalue().splitlines()]
        assert [item["event"] for item in events] == ["structured_event", "plain event"]
        assert events[0]["count"] == 2
        assert events[1]["logger"] == "training.plain"
        assert all("_record" not in item and "_from_structlog" not in item for item in events)
    finally:
        logging.getLogger("training").handlers.clear()
```

Запуск: `python -m pytest -q test_logging.py test_stdlib.py`. В этой схеме финальный renderer находится в `ProcessorFormatter`; цепочка structlog заканчивается `wrap_for_formatter`. `foreign_pre_chain` обогащает обычные logging-записи, `remove_processors_meta` убирает служебные поля перед JSON. `get_logger`/`wrap_logger` возвращают structlog bound logger, даже если внутри лежит `logging.Logger`.

## Порядок и стоимость

| Процессор / приём | Когда нужен |
| --- | --- |
| `merge_contextvars` | В начале, если нужен контекст запроса |
| `filter_by_level` | Ранний фильтр для stdlib logger; не подмена проверки аргументов Python |
| `TimeStamper`, `add_log_level`, `add_logger_name` | Метаданные; logger name требует подходящего stdlib-контекста |
| `PositionalArgumentsFormatter` | `%s`-аргументы stdlib-style вызовов |
| `StackInfoRenderer` | `stack_info=True`; это не тот же traceback, что у `exc_info` |
| `format_exc_info` | Преобразование исключения для текстового/JSON-вывода; ConsoleRenderer умеет собственное оформление |
| `UnicodeDecoder` | Если в event dict реально приходят bytes |
| `CallsiteParameterAdder` | FILENAME/FUNC_NAME/LINENO, когда оправдана дополнительная стоимость |
| `JSONRenderer` / `KeyValueRenderer` / свой renderer | Последний шаг; возвращай формат, который принимает нижележащий logger |

Для своего renderer сигнатура — `(logger, method_name, event_dict)`; он должен осознанно сохранить нужные поля. Сборка строки только из event/level теряет остальные данные. Для другого JSON-encoder передай совместимый `serializer`, например `orjson.dumps` после установки orjson; это не `serializer=str`.

Аргументы вычисляются **до** фильтра логгера: `log.debug("event", value=expensive())` уже вызовет expensive. В показанном filtering logger сначала проверь `log.is_enabled_for(logging.DEBUG)`. У stdlib BoundLogger доступен `isEnabledFor`; не переноси методы между wrapper-классами без проверки API. `cache_logger_on_first_use` задаётся один раз: повторяющийся keyword в одном вызове — синтаксическая ошибка. В тестах бери свежий логгер после перенастройки.

Источники: [конфигурация](https://www.structlog.org/en/stable/configuration.html), [processors/API](https://www.structlog.org/en/stable/api.html), [stdlib](https://www.structlog.org/en/stable/standard-library.html), [exceptions](https://www.structlog.org/en/stable/exceptions.html), [performance](https://www.structlog.org/en/stable/performance.html).
