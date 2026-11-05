# structlog

structlog собирает событие как словарь: поля контекста и вызова проходят цепочку процессоров и renderer. Здесь — короткий справочник, воспроизводимые конфигурации и контекст запросов.

[Каталог Python](../../README.md) · [FastAPI](../../web/fastapi/README.md)

| Параметр | Значение |
| --- | --- |
| API | structlog 26.1 |
| Предпосылки | Python, словари, logging; для contextvars — конкурентные задачи |
| Сверено с документацией | 2026-11-06, structlog stable 26.1.0 |
| Выполнено | 2026-11-06: 8 Python-блоков скомпилированы, 7 тестов прошли, включая сохранённый exc_info вне except для JSON/console. Python 3.14.7, structlog 26.1.0, pytest 9.2.0; HTTP-интеграция — FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0 |

## Навигация

- [Быстрый поиск](#быстрый-поиск)
- [Базовый уровень](#базовый-уровень)
- [Средний уровень](#средний-уровень)
- [Продвинутый уровень](#продвинутый-уровень)
- [Частые ошибки](#частые-ошибки)
- [Источники](#источники)

## Быстрый поиск

| Задача | API | Рецепт |
| --- | --- | --- |
| JSON / console / key-value | `JSONRenderer`, `ConsoleRenderer`, `KeyValueRenderer` | [Конфигурация](configuration.md#самостоятельная-конфигурация) |
| Добавить/убрать поля логгера | `bind`, `unbind`, `try_unbind` | [Контекст](context-and-web.md#локальный-и-контекстный-bind) |
| Поля для всех логов запроса | `merge_contextvars`, `bound_contextvars` | [Contextvars](context-and-web.md) |
| Сохранить traceback | `exception` либо `exc_info=True` | [Конфигурация и тесты](configuration.md) |
| Обработать stdlib и structlog одинаково | `ProcessorFormatter` | [Stdlib](configuration.md#интеграция-со-stdlib-logging) |
| Контекст async/FastAPI/Django | Изоляция задач и middleware | [Контекст и веб](context-and-web.md) |
| Фильтровать/маскировать/профилировать | Процессоры, проверка уровня | [Порядок и стоимость](configuration.md#порядок-и-стоимость) |

## Базовый уровень

Установка: `python -m pip install 'structlog==26.1.0' pytest` в отдельное окружение. Минимальная конструкция — `structlog.get_logger().info("user_logged_in", user_id=123)` после `import structlog`; это фрагмент для знакомства, полная настройка находится [отдельно](configuration.md).

| Приём | Поведение |
| --- | --- |
| `log.info("event_name", key=value)` | Структурированное событие; `event` уже занят сообщением |
| `child = log.bind(user_id=1)` | Новый логгер с полем; исходный не меняется |
| `child = child.unbind("user_id")` | Новый логгер без ключа; отсутствующий ключ вызывает KeyError |
| `try_unbind("key")` | Удаляет ключ, если он существует |
| `debug/info/warning/error/critical` | Уровни, фильтрация зависит от конфигурации |
| `exception("failed")` внутри except | Добавляет traceback при подходящем processor/renderer |

## Средний уровень

Сначала сливай `contextvars`, затем добавляй уровень/время/метаданные, обрабатывай исключение и маскируй поля, renderer ставь последним. Для stdlib нужен согласованный `ProcessorFormatter`, а не смесь разных финальных renderer.

```mermaid
flowchart LR
    A[Поля bind] -->|копировать контекст| D[Словарь события]
    B[Поля вызова и event] -->|добавить или переопределить| D
    C[Contextvars запроса] -->|добавить отсутствующие ключи| E[merge_contextvars]
    D -->|передать событие| E
    E -->|обогатить поля| F[Метаданные и исключение]
    F -->|передать обогащённое событие| G[Маскирование известных полей]
    G -->|передать маскированное событие| H[Renderer]
    H -->|передать готовый формат| I[Вывод или logging handler]
```

Повторный ключ вызова имеет приоритет над полем bound logger; `merge_contextvars` добавляет отсутствующие ключи. Передавай стабильное имя события и отдельные поля, чтобы их можно было искать без разбора строки.

## Продвинутый уровень

[Contextvars и middleware](context-and-web.md) обеспечивают границу запроса и очистку. Они не означают автоматическое перенесение всех изменений между sync/async/потоками. Для асинхронного приложения обычный `.info()` остаётся синхронной работой; `await log.ainfo()` доступен у показанного filtering logger и переносит работу в пул потоков.

`cache_logger_on_first_use=True` полезен при стабильной конфигурации, но уже созданные логгеры не перенастраиваются автоматически. Фиксированный filtering logger от `make_filtering_bound_logger` рассчитан на неизменяемый минимум уровня; при динамических уровнях stdlib выбери его BoundLogger и `filter_by_level`. Не обещай ускорение без замера реального процессорного пути.

## Частые ошибки

| Ошибка | Исправление |
| --- | --- |
| `with logger.bind(...)` | Используй новый logger либо `with bound_contextvars(...)` |
| `JSONRenderer(serializer=str)` | serializer должен кодировать весь event dict в JSON; оставь default или JSON-совместимый encoder |
| `structlog.dev.lazy(...)` | Такого публичного API в проверенной ветке нет; проверь уровень до дорогого вычисления |
| `StackInfoRenderer` считают только ERROR+ | Он реагирует на `stack_info=True`, не на уровень сам по себе |
| `get_logger("name")` считают stdlib logger | Возвращается structlog proxy; stdlib-интеграцию определяет LoggerFactory |
| Повторяют configure/handlers в middleware | Настрой один раз при старте, иначе возможны дубли и несовместимые цепочки |
| Пишут только `str(exception)` | Для traceback используй `exception`/`exc_info` |

## Источники

- [Bound loggers](https://www.structlog.org/en/stable/bound-loggers.html), [processors](https://www.structlog.org/en/stable/processors.html), [API](https://www.structlog.org/en/stable/api.html).
- [Contextvars](https://www.structlog.org/en/stable/contextvars.html), [stdlib logging](https://www.structlog.org/en/stable/standard-library.html), [performance](https://www.structlog.org/en/stable/performance.html).
