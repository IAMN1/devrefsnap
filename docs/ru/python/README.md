
# Python

[English](../../en/python/README.md)

[Найти пример по задаче или синониму](../tasks/README.md) — типы, окружение, валидация, тесты, логи, API и доступ к БД.

Раздел содержит материалы о языке Python, проектировании приложений, библиотеках и инструментах экосистемы Python.
SQL и особенности СУБД находятся в [разделе баз данных](../databases/README.md).
Git и GitHub находятся в [общих инструментах](../tools/README.md).


## Материалы

| Тема | Содержание |
| --- | --- |
| [Типы Python](language/types/README.md) | Типы, операции, копирование и хешируемость |
| [Проектирование проекта](architecture/project-design/README.md) | Решения, структура, рабочий пакет и поставка |
| [Pydantic](validation/pydantic/README.md) | Модели, валидация, сериализация и настройки |
| [SQLAlchemy](databases/sqlalchemy/README.md) | Модели, [N+1 и загрузка](databases/sqlalchemy/relationship-loading.md), запросы, транзакции, async и миграции |
| [pytest](testing/pytest/README.md) | Тесты, фикстуры, параметризация, mock и плагины |
| [structlog](logging/structlog/README.md) | Процессоры, контекст и интеграции |
| [uv](tooling/uv/README.md) | Окружения, зависимости, lock и автоматизация |
| [FastAPI](web/fastapi/README.md) | HTTP API, зависимости, БД, JWT и тесты |
| [Flask](web/flask/README.md) | Factory, Blueprint, конфигурация и WSGI |
| [Django](web/django/README.md) | Модель, миграция SQLite, админка и тестирование |

Версии API, зависимости и условия применения указаны в соответствующих темах.
Общие принципы и паттерны находятся в [архитектуре](../architecture/README.md).
Руководство по проектированию в этом разделе показывает применение принципов и паттернов к Python-проекту.


## Связанные темы

- SQLAlchemy использует [SQL](../databases/sql/README.md) и конкретную СУБД:
  [PostgreSQL](../databases/relational/postgresql/README.md) или [SQLite](../databases/relational/sqlite/README.md).
- Для управления зависимостями pytest используйте [uv](tooling/uv/README.md).
  Написание тестов разобрано в [pytest](testing/pytest/README.md).
- Модели данных FastAPI связаны с [Pydantic](validation/pydantic/README.md).

[Все материалы](../README.md)
