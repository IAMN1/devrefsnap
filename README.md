# Шпаргалки по разработке

Русскоязычный справочник по Python, Go, базам данных, Linux, инструментам и архитектуре.
Найдите действие через [указатель задач и синонимов](tasks/README.md) или выберите знакомый инструмент в каталоге.

## Быстрый вход

| Ситуация | Как искать | Пример |
| --- | --- | --- |
| Помните задачу, но забыли название приёма | Найдите действие или синоним | [Указатель задач](tasks/README.md) |
| Выбрали инструмент и хотите повторить синтаксис | Откройте быстрый поиск темы | [Каталог материалов](#каталог-материалов) |
| Нужно выбрать между подходами | Сравните условия и ограничения в карточке | [Загрузка связанных данных](python/databases/sqlalchemy/relationship-loading.md#выбрать-стратегию) |
| Нужен первый самостоятельный запуск | Перейдите к полному примеру из карточки | [Python-пакет с тестами](python/architecture/project-design/example.md) |

## Разделы

- [Python](python/README.md) — язык, проектирование, библиотеки, FastAPI и Flask.
- [Go](go/README.md) — язык, стандартная библиотека, конкурентность и тестирование.
- [Базы данных](databases/README.md) — SQL, PostgreSQL, SQLite и Redis.
- [Операционные системы](systems/README.md) — Linux, оболочка и эксплуатационные команды.
- [Архитектура](architecture/README.md) — выбор по задаче, карточки SOLID, схемы и структуры пакетов.
- [Инструменты разработки](tools/README.md) — Git и работа с Pull Requests на GitHub.

## Каталог материалов

| Тема | Где искать |
| --- | --- |
| Типы Python | [Типы и операции](python/language/types/README.md) |
| Проектирование Python-проекта | [Решения, рабочий пакет и поставка](python/architecture/project-design/README.md) |
| Pydantic | [Валидация данных](python/validation/pydantic/README.md) |
| SQLAlchemy | [Справочник](python/databases/sqlalchemy/README.md), [простой пример N+1](python/databases/sqlalchemy/n-plus-one.md), [выбор загрузки по данным и ограничениям](python/databases/sqlalchemy/relationship-loading.md#выбрать-стратегию) |
| pytest | [Тестирование](python/testing/pytest/README.md) |
| structlog | [Структурированные логи](python/logging/structlog/README.md) |
| uv | [Окружения и зависимости Python](python/tooling/uv/README.md) |
| FastAPI | [Веб-приложения и API](python/web/fastapi/README.md), [полное API](python/web/fastapi/http-api.md), [подмена зависимости в тесте](python/web/fastapi/testing.md#подмена-зависимости) |
| Flask | [WSGI-приложения, factory и тесты](python/web/flask/README.md) |
| Go | [Язык, конкурентность и HTTP](go/README.md), [полный модуль](go/examples/language.md) |
| SQL | [Общий справочник SQL](databases/sql/README.md) |
| PostgreSQL | [Справочник](databases/relational/postgresql/README.md), [копия и восстановление](databases/relational/postgresql/backup-and-restore.md) |
| SQLite | [Справочник](databases/relational/sqlite/README.md), [копия и восстановление](databases/relational/sqlite/backup-and-restore.md) |
| Redis | [Структуры, кэш и обмен сообщениями](databases/non-relational/redis/README.md), [RDB-копия](databases/non-relational/redis/backup-and-restore.md), [AOF-копия и восстановление](databases/non-relational/redis/aof-backup-and-restore.md) |
| Git | [Выбор команд по рабочим задачам](tools/git/README.md) |
| GitHub Pull Requests | [Создание, ревью и слияние PR](tools/github-pull-requests/README.md) |
| Linux | [Оболочка, файлы, процессы и службы](systems/linux/README.md), [процесс по порту](systems/linux/process-by-port.md) |
| Архитектурные принципы | [Карточки границ и компромиссов](architecture/principles.md), [проверки контрактов](architecture/contracts.md) |
| SOLID | [Пять принципов: до / после](architecture/solid.md) |
| Паттерны | [Выбор по задаче](architecture/patterns/README.md), [полные примеры](architecture/patterns/code-examples.md), [данные и отказы](architecture/patterns/distributed-systems.md), [проверка Outbox](architecture/patterns/outbox-example.md) |

## Как пользоваться материалами

Начните с быстрого поиска в README выбранной темы.
Для повторения используйте короткие карточки.
Для первого запуска перейдите к полному примеру с зависимостями и подготовкой.
Условия применения и ограничения находятся рядом с примером.
Уровни помогают выбрать материал там, где различие задач существенно.

| Уровень | Что в нём искать |
| --- | --- |
| Базовый | Первые рабочие операции, основные команды и понятия |
| Средний | Типовые рабочие сценарии и сочетание нескольких возможностей |
| Продвинутый | Сложные случаи, конкурентность, оптимизация и эксплуатация |

Схемы Mermaid показывают взаимодействия и зависимости.
GitHub отображает схемы прямо в Markdown.
Подробнее: [диаграммы в GitHub Markdown](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams).
В редакторе без поддержки Mermaid виден исходный текст схемы.
[Шаблоны материалов](templates/README.md) · [Правила для авторов](AGENTS.md) · [Сопровождение](maintenance/README.md)
