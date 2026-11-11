
# Настроить вывод и процессоры

[English](../../../../en/python/logging/structlog/configuration.md)

Откройте страницу, чтобы получить JSON-события, сохранить traceback или объединить structlog со стандартным logging.
Настройка выполняется один раз до обработки событий.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Выбрать JSON, console или key-value | Один финальный renderer | [Самостоятельная конфигурация](#самостоятельная-конфигурация) |
| Маскировать известные поля | Процессор перед renderer | [Код и проверки](#самостоятельная-конфигурация) |
| Объединить два источника логов | `ProcessorFormatter` | [Stdlib logging](#интеграция-со-stdlib-logging) |
| Не вычислять дорогой DEBUG-аргумент | Проверка уровня до вызова | [Порядок и стоимость](#порядок-и-стоимость) |

[Справочник](README.md) · [Контекст и веб](context-and-web.md)

**Уровень:** базовый → продвинутый.
Предпосылки: словари, logging, обработка исключений.
Используйте Python 3.14.
Выполните `python -m pip install 'structlog==26.1.0' 'pytest==9.2.0'` в отдельном окружении.
Сохраняйте все файлы темы рядом.

- [Самостоятельная конфигурация](#самостоятельная-конфигурация)
- [Интеграция со stdlib logging](#интеграция-со-stdlib-logging)
- [Порядок и стоимость](#порядок-и-стоимость)


## Самостоятельная конфигурация

Ниже приведён полный пример `demo_logging.py`.
Пример выбирает renderer один раз.
Пример рекурсивно маскирует чувствительные поля по заданным именам.

[`structlog/demo_logging.py`](../../../../../examples/python/logging/structlog/demo_logging.py)

Запустите `python demo_logging.py`.
Результат — две JSON-строки.
Пароль заменён на `***`.
Во второй строке есть `exception` с traceback.
Маскирование действует только на перечисленные **ключи**.
Маскирование не обрабатывает произвольные строки, traceback или неизвестные контейнеры.
Не помещайте секрет в `event` или текст исключения в расчёте на автоматическое обнаружение.

Маскирование сохраняет тип tuple.
Служебный `exc_info`, сохранённый через `sys.exc_info()`, должен остаться кортежем.
Тогда ConsoleRenderer восстановит traceback даже за пределами `except`.

Полный `test_logging.py`:

[`structlog/test_logging.py`](../../../../../examples/python/logging/structlog/test_logging.py)


## Интеграция со stdlib logging

Полный пример `demo_stdlib.py` настраивает только учебное имя logger.
Встройте конфигурацию в штатную настройку приложения.
Не очищайте чужие handlers библиотечным импортом.

[`structlog/demo_stdlib.py`](../../../../../examples/python/logging/structlog/demo_stdlib.py)

Полный `test_stdlib.py` проверяет обе стороны одной цепочки:

[`structlog/test_stdlib.py`](../../../../../examples/python/logging/structlog/test_stdlib.py)

Запустите `python -m pytest -q test_logging.py test_stdlib.py`.
В этой схеме финальный renderer находится в `ProcessorFormatter`.
Цепочка structlog заканчивается `wrap_for_formatter`.
`foreign_pre_chain` обогащает обычные logging-записи.
`remove_processors_meta` убирает служебные поля перед JSON.
`get_logger`/`wrap_logger` возвращают structlog bound logger, даже если внутри лежит `logging.Logger`.


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
| `JSONRenderer` / `KeyValueRenderer` / свой renderer | Последний шаг. Возвращайте формат, который принимает нижележащий logger |

Сигнатура своего renderer — `(logger, method_name, event_dict)`.
Сохраните в renderer нужные поля.
Сборка строки только из event/level теряет остальные данные.
Для другого JSON-encoder передайте совместимый `serializer`.
Например, после установки orjson можно передать `orjson.dumps`.
Значение `serializer=str` для этого не подходит.

Аргументы вычисляются **до** фильтра логгера.
Поэтому `log.debug("event", value=expensive())` уже вызовет expensive.
В показанном filtering logger сначала проверьте `log.is_enabled_for(logging.DEBUG)`.
У stdlib BoundLogger доступен `isEnabledFor`.
Не переносите методы между wrapper-классами без проверки API.
Задавайте `cache_logger_on_first_use` один раз.
Повторяющийся keyword в одном вызове — синтаксическая ошибка.
После перенастройки берите в тестах свежий логгер.

Источники: [конфигурация](https://www.structlog.org/en/stable/configuration.html), [processors/API](https://www.structlog.org/en/stable/api.html), [stdlib](https://www.structlog.org/en/stable/standard-library.html), [exceptions](https://www.structlog.org/en/stable/exceptions.html), [performance](https://www.structlog.org/en/stable/performance.html).
