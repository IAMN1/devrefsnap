# Python

[Найти пример по задаче или синониму](../tasks/README.md) — типы, окружение, валидация, тесты, логи, API и доступ к БД.

Раздел содержит материалы о языке Python, проектировании приложений, библиотеках и инструментах экосистемы Python.
SQL и особенности СУБД находятся в [разделе баз данных](../databases/README.md).
Git и GitHub находятся в [общих инструментах](../tools/README.md).

## Материалы

| Тема | Содержание | Статус |
| --- | --- | --- |
| [Типы Python](language/types/README.md) | Типы, операции, копирование и хешируемость | Актуализировано |
| [Проектирование проекта](architecture/project-design/README.md) | Решения, структура, рабочий пакет и поставка | Актуализировано |
| [Pydantic](validation/pydantic/README.md) | Модели, валидация, сериализация и настройки | Актуализировано |
| [SQLAlchemy](databases/sqlalchemy/README.md) | Модели, [N+1 и загрузка](databases/sqlalchemy/relationship-loading.md), запросы, транзакции, async и миграции | Актуализировано |
| [pytest](testing/pytest/README.md) | Тесты, фикстуры, параметризация, mock и плагины | Актуализировано |
| [structlog](logging/structlog/README.md) | Процессоры, контекст и интеграции | Актуализировано |
| [uv](tooling/uv/README.md) | Окружения, зависимости, lock и автоматизация | Актуализировано |
| [FastAPI](web/fastapi/README.md) | HTTP API, зависимости, БД, JWT и тесты | Актуализировано |
| [Flask](web/flask/README.md) | Factory, Blueprint, конфигурация и WSGI | Добавлено |

Материалы оформлены по [общему шаблону](../templates/cheat-sheet.md).
Версии, результаты выполнения и границы проверки указаны в паспорте каждой темы.
Общие принципы и паттерны находятся в [архитектуре](../architecture/README.md).
Руководство по проектированию в этом разделе показывает применение принципов и паттернов к Python-проекту.

## Связанные темы

- SQLAlchemy использует [SQL](../databases/sql/README.md) и конкретную СУБД:
  [PostgreSQL](../databases/relational/postgresql/README.md) или [SQLite](../databases/relational/sqlite/README.md).
- Для управления зависимостями pytest используйте [uv](tooling/uv/README.md).
  Написание тестов разобрано в [pytest](testing/pytest/README.md).
- Модели данных FastAPI связаны с [Pydantic](validation/pydantic/README.md).

[Все материалы](../README.md)
