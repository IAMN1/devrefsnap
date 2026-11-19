
<a name="русский-каталог-двуязычных-материалов"></a>
# Шпаргалки по разработке

[English](../en/README.md) · [Участие в проекте](../../CONTRIBUTING.md#русский)

Справочник по Python, Go, C, C#, C++, TypeScript, алгоритмам, базам данных, Linux, инструментам и архитектуре.
Найдите действие через [указатель задач и синонимов](tasks/README.md) или выберите знакомый инструмент в каталоге.


## Быстрый вход

| Задача | Пример |
| --- | --- |
| Запустить первую программу | [Цена трёх билетов на Python](python/language/first-program.md) · [Первая программа на C](c/README.md#первый-запуск) |
| Посмотреть статус HTTP и извлечь поле из JSON | [HTTP и JSON в терминале](tools/http-json.md) |
| Найти причину падения теста в CI | [Разбор журнала GitHub Actions](tools/compose-and-github-actions.md#найти-причину-падения-в-журнале) |
| Выбрать загрузку связанных данных | [Таблица стратегий SQLAlchemy](python/databases/sqlalchemy/relationship-loading.md#выбрать-стратегию) |
| Вспомнить синтаксис знакомого языка | [Коллекции C#](csharp/syntax.md#collections) |


## Разделы

- [Python](python/README.md) — язык, проектирование, библиотеки, FastAPI, Flask и Django.
- [Go](go/README.md) — язык, стандартная библиотека, конкурентность и тестирование.
- [C](c/README.md) — синтаксис C17, память, сборка и тесты, паттерны и области применения.
- [C#](csharp/README.md) — C# 14 и .NET 10, NuGet, тесты и выбор фреймворка по задаче.
- [C++](cpp/README.md) — C++20, стандартная библиотека, управление ресурсами, зависимости и тесты.
- [TypeScript](typescript/README.md) — типизация HTTP-клиента и проверка JSON.
- [Алгоритмы](algorithms/README.md) — оценка числа операций через Big O.
- [Базы данных](databases/README.md) — SQL, PostgreSQL, SQLite и Redis.
- [Операционные системы](systems/README.md) — Linux, оболочка и эксплуатационные команды.
- [Архитектура](architecture/README.md) — выбор по задаче, карточки SOLID, схемы и структуры пакетов.
- [Инструменты разработки](tools/README.md) — HTTP из терминала, Docker Compose, Git и GitHub.


## Каталог материалов

| Тема | Где искать |
| --- | --- |
| Прочитать большой файл по одной строке | [Построчное чтение в Python](python/language/read-lines.md) |
| Типы Python | [Типы и операции](python/language/types/README.md) |
| asyncio | [Первые корутины и конкурентное ожидание](python/language/asyncio.md) |
| Проектирование Python-проекта | [Решения, рабочий пакет и поставка](python/architecture/project-design/README.md) |
| Pydantic | [Валидация данных](python/validation/pydantic/README.md) |
| SQLAlchemy | [Справочник](python/databases/sqlalchemy/README.md), [простой пример N+1](python/databases/sqlalchemy/n-plus-one.md), [выбор загрузки по данным и ограничениям](python/databases/sqlalchemy/relationship-loading.md#выбрать-стратегию) |
| pytest | [Тестирование](python/testing/pytest/README.md) |
| structlog | [Структурированные логи](python/logging/structlog/README.md) |
| uv | [Окружения и зависимости Python](python/tooling/uv/README.md) |
| FastAPI | [Веб-приложения и API](python/web/fastapi/README.md), [полное API](python/web/fastapi/http-api.md), [подмена зависимости в тесте](python/web/fastapi/testing.md#подмена-зависимости) |
| Django | [Модель, миграция, админка и тесты](python/web/django/README.md) |
| Flask | [WSGI-приложения, factory и тесты](python/web/flask/README.md) |
| Go | [Язык, конкурентность и HTTP](go/README.md), [тайм-аут и отмена HTTP-запроса](go/context.md), [полный модуль](go/examples/language.md) |
| C | [Первый запуск](c/README.md), [синтаксис](c/syntax.md), [сборка, библиотеки и тесты](c/tooling-and-testing.md), [практики и области применения](c/practice.md) |
| C# | [Первый запуск](csharp/README.md), [синтаксис](csharp/syntax.md), [NuGet и тесты](csharp/tooling-and-testing.md), [практики и области применения](csharp/practice.md) · [первый HTTP-сервис](csharp/first-http-service.md) |
| C++ | [Первый запуск](cpp/README.md), [синтаксис](cpp/syntax.md), [сборка, библиотеки и тесты](cpp/tooling-and-testing.md), [практики и области применения](cpp/practice.md) |
| SQL | [Общий справочник SQL](databases/sql/README.md) · [повторяющиеся адреса почты](databases/sql/queries.md#duplicate-emails) |
| PostgreSQL | [Справочник](databases/relational/postgresql/README.md), [копия и восстановление](databases/relational/postgresql/backup-and-restore.md) |
| SQLite | [Справочник](databases/relational/sqlite/README.md), [копия и восстановление](databases/relational/sqlite/backup-and-restore.md) |
| Redis | [Структуры, кэш и обмен сообщениями](databases/non-relational/redis/README.md), [RDB-копия](databases/non-relational/redis/backup-and-restore.md), [AOF-копия и восстановление](databases/non-relational/redis/aof-backup-and-restore.md) |
| curl и jq | [Запрос и разбор HTTP-ответа](tools/http-json.md) |
| Docker Compose и GitHub Actions | [Приложение с PostgreSQL и тесты в CI](tools/compose-and-github-actions.md) |
| Контракт HTTP API | [FastAPI, PostgreSQL и TypeScript в Compose и CI](tools/api-contract-lab.md) |
| Git | [Выбор команд по рабочим задачам](tools/git/README.md) |
| GitHub Pull Requests | [Создание, ревью и слияние PR](tools/github-pull-requests/README.md) |
| Linux | [Оболочка, файлы, процессы и службы](systems/linux/README.md), [процесс по порту](systems/linux/process-by-port.md) |
| Архитектурные принципы | [Карточки границ и компромиссов](architecture/principles.md), [проверки контрактов](architecture/contracts.md) |
| SOLID | [Пять принципов: до / после](architecture/solid.md) |
| Паттерны | [Выбор по задаче](architecture/patterns/README.md), [полные примеры](architecture/patterns/code-examples.md), [данные и отказы](architecture/patterns/distributed-systems.md), [проверка Outbox](architecture/patterns/outbox-example.md) |
| TypeScript | [Типизированный клиент к FastAPI](typescript/README.md) |
| Big O | [Линейный и квадратичный рост](algorithms/README.md#big-o) |


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
[Языковые версии](../README.md) · [Шаблоны материалов](../../templates/README.md) · [Правила для авторов](../../AGENTS.md) · [Сопровождение](../../maintenance/README.md) · [Статические проверки и ревью PR](../../scripts/README.md)
