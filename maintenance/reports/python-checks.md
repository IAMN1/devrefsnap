# История проверок материалов Python

Служебные записи перенесены из читательских страниц.
Записи описывают проверки прежних редакций и не подтверждают повторный запуск после переноса.

## [python/README.md](../../python/README.md)

Версии, результаты выполнения и границы проверки указаны в паспорте каждой темы.

- Flask — Добавлено.

- [Типы Python](../../python/language/types/README.md) — Типы, операции, копирование и хешируемость — Актуализировано

- [Проектирование проекта](../../python/architecture/project-design/README.md) — Решения, структура, рабочий пакет и поставка — Актуализировано

- [Pydantic](../../python/validation/pydantic/README.md) — Модели, валидация, сериализация и настройки — Актуализировано

- [SQLAlchemy](../../python/databases/sqlalchemy/README.md) — Модели, [N+1 и загрузка](../../python/databases/sqlalchemy/relationship-loading.md), запросы, транзакции, async и миграции — Актуализировано

- [pytest](../../python/testing/pytest/README.md) — Тесты, фикстуры, параметризация, mock и плагины — Актуализировано

- [structlog](../../python/logging/structlog/README.md) — Процессоры, контекст и интеграции — Актуализировано

- [uv](../../python/tooling/uv/README.md) — Окружения, зависимости, lock и автоматизация — Актуализировано

- [FastAPI](../../python/web/fastapi/README.md) — HTTP API, зависимости, БД, JWT и тесты — Актуализировано

## [python/architecture/project-design/README.md](../../python/architecture/project-design/README.md)

- Сверено — 2026-11-06: PyPA, Python 3.14, Pydantic Settings, первичные архитектурные источники

- Выполнено — 2026-11-06: пакет собран и установлен. `uv sync`, CLI и 9 тестов прошли. Версии: Python 3.14.7, uv 0.12.13, Pydantic 2.14.3, Settings 2.16.2, pytest 9.2.0. Таблицы решений оцениваются содержательно, а не исполнением

## [python/architecture/project-design/delivery-and-evolution.md](../../python/architecture/project-design/delivery-and-evolution.md)

Сверено с источниками 2026-11-06.

Сценарий изменения БД ниже иллюстративен и не выполнялся на рабочем сервере.

## [python/architecture/project-design/example.md](../../python/architecture/project-design/example.md)

- Сверено — 2026-11-06, PyPA, Pydantic Settings, Python sqlite3

- Выполнено — 2026-11-06: editable-пакет собран, `uv sync --group dev`, CLI и 9 тестов прошли в отдельном окружении; Python 3.14.7, uv 0.12.13, Pydantic 2.14.3, Settings 2.16.2, pytest 9.2.0

## [python/architecture/project-design/structure-and-decisions.md](../../python/architecture/project-design/structure-and-decisions.md)

Сверено с первичными источниками 2026-11-06.

## [python/databases/sqlalchemy/README.md](../../python/databases/sqlalchemy/README.md)

- Сверено с документацией — 2026-11-06, SQLAlchemy 2.1 и Alembic

- Исходные проверки — 2026-11-06: в прежней редакции 10 Python-блоков скомпилированы, 9 тестов прошли, включая async FK/rollback; отдельный цикл Alembic upgrade/backfill/downgrade проверен на SQLite. Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, aiosqlite 0.22.1, Alembic 1.20.1, pytest 9.2.0

- Запросы и загрузка выполнены — 2026-11-06: 21 тест запросов, загрузки и пакетной обработки; Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0, greenlet 3.5.6. [Условия сравнения](../../python/databases/sqlalchemy/loading-lab.md)

Примеры проверяются на SQLAlchemy 2.1.

## [python/databases/sqlalchemy/async-and-operations.md](../../python/databases/sqlalchemy/async-and-operations.md)

Сверено 2026-11-06 с SQLAlchemy 2.1 и Alembic.

Выполнено 2026-11-06: async roundtrip/отношения, отказ при неверном FK с rollback и события проверены тремя тестами.

Миграция с backfill/NOT NULL/откатом проверена отдельно на временном файле SQLite.

Профилирование нагрузки и подбор параметров пула не выполнялись.

Последовательность проверена 2026-11-06 на отдельной SQLite с синтетическим пользователем.

Проверка охватила init/autogenerate/upgrade/current/history.

Затем проверены добавление verified, backfill, NOT NULL и downgrade с сохранением остальных полей.

## [python/databases/sqlalchemy/loading-lab.md](../../python/databases/sqlalchemy/loading-lab.md)

- Сверено с документацией — 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8

- Выполнено — 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0, greenlet 3.5.6; 15 проверок полного файла ниже

- Не измерялось — Время, память, сетевые задержки и планы запросов рабочей БД

В проверенном окружении использовался greenlet 3.5.6.

## [python/databases/sqlalchemy/models-and-transactions.md](../../python/databases/sqlalchemy/models-and-transactions.md)

Сверено 2026-11-06 с SQLAlchemy 2.1.

Выполнено 2026-11-06: 4 теста страницы прошли на Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0.

## [python/databases/sqlalchemy/n-plus-one.md](../../python/databases/sqlalchemy/n-plus-one.md)

- Сверено с документацией — 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8 от 2026-11-03

- Выполнено — 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4; программа ниже

Другие версии и СУБД не запускались.

## [python/databases/sqlalchemy/queries.md](../../python/databases/sqlalchemy/queries.md)

Сверено 2026-11-06 с SQLAlchemy 2.1.

Выполнено 2026-11-06: один тест результатов SQLite и компиляция четырёх выражений PostgreSQL.

Загрузка отношений и пакетная обработка проверены на связанных страницах.

PostgreSQL не запускался.

PostgreSQL здесь не запускался.

## [python/databases/sqlalchemy/relationship-loading.md](../../python/databases/sqlalchemy/relationship-loading.md)

- Сверено с документацией — 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8

- Выполнено — 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0; [проверки загрузки](../../python/databases/sqlalchemy/loading-lab.md)

- Границы — Синхронная ORM и SQLite в памяти; другие драйверы, async и время выполнения здесь не проверялись

## [python/databases/sqlalchemy/streaming.md](../../python/databases/sqlalchemy/streaming.md)

- Сверено с документацией — 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8

- Выполнено — 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0, greenlet 3.5.6; пять проверок полного файла ниже

- Границы — Проверена обработка и ожидаемые ошибки на SQLite; память, server-side cursors других драйверов и большие объёмы не измерялись

## [python/language/types/README.md](../../python/language/types/README.md)

- Сверено — 2026-11-06, документация Python 3.14

- Выполнено — 2026-11-06: полный пример чисел, коллекций, отказов преобразования и копирования прошёл на Python 3.14.7

## [python/language/types/recipes.md](../../python/language/types/recipes.md)

Сверено с документацией 2026-11-06.

Полный пример выполнен 2026-11-06 на Python 3.14.7.

Все проверки завершились успешно.

## [python/logging/structlog/README.md](../../python/logging/structlog/README.md)

- Сверено с документацией — 2026-11-06, structlog stable 26.1.0

- Выполнено — 2026-11-06: 8 Python-блоков скомпилированы, 7 тестов прошли, включая сохранённый exc_info вне except для JSON/console. Python 3.14.7, structlog 26.1.0, pytest 9.2.0; HTTP-интеграция — FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0

Такого публичного API в проверенной ветке нет.

## [python/logging/structlog/configuration.md](../../python/logging/structlog/configuration.md)

Сверено 2026-11-06 со structlog 26.1.0.

Выполнено 2026-11-06: 5 тестов страницы прошли на Python 3.14.7, structlog 26.1.0, pytest 9.2.0, включая сохранённый exc_info вне except.

Производительность под нагрузкой не измерялась.

## [python/logging/structlog/context-and-web.md](../../python/logging/structlog/context-and-web.md)

Сверено 2026-11-06 со structlog 26.1.0.

Выполнено 2026-11-06: async-изоляция и FastAPI success/error проверены двумя тестами.

Django-проект не запускался.

Этот вариант **сверен с документацией, но Django-проект не запускался**.

[проверенном stdlib-рецепте]

## [python/testing/pytest/README.md](../../python/testing/pytest/README.md)

- Сверено с документацией — 2026-11-06, pytest stable и официальные руководства используемых плагинов

- Выполнено — 2026-11-06, CPython 3.14.7, pytest 9.2.0; версии плагинов и сценарии — [в проверках](../../python/testing/pytest/configuration.md#среда-примеров)

- Проверенная ветка — pytest 9; отдельные возможности предоставляют плагины

## [python/testing/pytest/configuration.md](../../python/testing/pytest/configuration.md)

Здесь JSON-плагин не устанавливался и не выполнялся.

**Что проверено**

2026-11-06, macOS, CPython 3.14.7:

- pytest 9.2.0: 13 основных + 4 mock/async сценария в отдельном временном каталоге.
- pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1: подмена адаптера, передача ошибки, async fixture/result.
- pytest-cov 7.1.0: сформирован терминальный отчёт по `demo_service` и HTML.
- pytest-xdist 3.8.0: тот же набор запущен с двумя workers.
- Создан JUnit XML.
- Проверена сборка тестов.
- Проверен выбор тестов.

Production CI, JSON-плагин и Django-стек не выполнялись.

## [python/testing/pytest/fixtures.md](../../python/testing/pytest/fixtures.md)

Выполнено 2026-11-06: Python 3.14.7 / pytest 9.2.0, временный каталог и SQLite in-memory.

## [python/testing/pytest/mocking-and-async.md](../../python/testing/pytest/mocking-and-async.md)

Выполнено 2026-11-06: pytest 9.2.0, pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1.

Реальные Django-приложение, БД Django и внешние HTTP-интеграции не запускались.

## [python/tooling/uv/README.md](../../python/tooling/uv/README.md)

- Сверено с документацией — 2026-11-06, официальная документация Astral; сайт может описывать более новую версию

- Выполнено — 2026-11-06, uv 0.12.13, CPython 3.14.7, macOS; offline init/lock/sync/run/export и отказ при устаревшем lock

- Проверенная версия — uv 0.12.13; команды сверены также с установленным `uv help`

## [python/tooling/uv/automation.md](../../python/tooling/uv/automation.md)

Сверка: 2026-11-06.

YAML сверён с документацией.

Workflow не запускался.

Docker build/runtime **не выполнялись**.

Хук **не запускался**.

В CI, Docker, pre-commit и внешних индексах выполнение не проводилось.

Локально сверены help uv 0.12.13 и [offline-проект](../../python/tooling/uv/projects.md).

`UV_SSL_VERIFY=0` и `UV_LOG_LEVEL` не являются рецептами из проверенного help.

## [python/tooling/uv/projects.md](../../python/tooling/uv/projects.md)

Сверка: 2026-11-06. Выполнен только приведённый offline-сценарий, uv 0.12.13 / Python 3.14.7.

## [python/validation/pydantic/README.md](../../python/validation/pydantic/README.md)

- Сверено с документацией — 2026-11-06, Pydantic v2, pydantic-settings и pydantic-extra-types

- Выполнено — 2026-11-06: 10 Python-блоков скомпилированы, 20 тестов прошли, включая timezone-aware ввод и UTC-сериализацию. Python 3.14.7, Pydantic 2.14.3, pytest 9.2.0; settings 2.16.2 и FastAPI 0.162.0 проверены в интеграциях

## [python/validation/pydantic/advanced.md](../../python/validation/pydantic/advanced.md)

Сверено 2026-11-06 с документацией Pydantic v2.

Выполнено 2026-11-06: 4 теста страницы прошли на Python 3.14.7, Pydantic 2.14.3, pydantic-settings 2.16.2, FastAPI 0.162.0, HTTPX2 2.16.0, pytest 9.2.0.

PaymentCardNumber, автоматическая миграция и численный benchmark не запускались.

Измерения производительности и автоматическая миграция здесь не выполнялись.

Численные обещания исходника удалены как неподкреплённые.

## [python/validation/pydantic/models.md](../../python/validation/pydantic/models.md)

Сверено 2026-11-06 с Pydantic v2.

Выполнено 2026-11-06: 16 тестов страницы прошли на Python 3.14.7, Pydantic 2.14.3, email-validator 2.3.0, pytest 9.2.0.

Timestamp-тесты также прошли при TZ=UTC и Europe/Moscow.

## [python/web/fastapi/README.md](../../python/web/fastapi/README.md)

- Сверено с документацией — 2026-11-06: FastAPI, release notes 0.162.0 от 2026-10-23, Pydantic v2, SQLAlchemy 2.0

- Выполнено ранее — 2026-11-06: 14 Python-блоков скомпилированы; 45 тестов прошли, включая CRUD, ввод, файлы, JWT и SQLite. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3; [остальные версии](../../python/web/fastapi/testing.md#среда-примеров)

- Проверка после переработки подмены — [Отдельные тесты и версии](../../python/web/fastapi/dependency-overrides.md#среда-примеров); остальные сценарии повторно не запускались

## [python/web/fastapi/authentication.md](../../python/web/fastapi/authentication.md)

- Сверено с документацией — 2026-11-06: FastAPI 0.162.0, PyJWT и pwdlib

- Выполнено — 2026-11-06: вход, защищённый маршрут и отказы доступа проверены тестами. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, PyJWT 2.15.1, pwdlib 0.3.1 с Argon2, python-multipart 0.0.33

## [python/web/fastapi/database.md](../../python/web/fastapi/database.md)

- Сверено с документацией — 2026-11-06, FastAPI 0.162.0, SQLAlchemy API 2.0, Pydantic v2

- Выполнено — 2026-11-06: lifespan, запись/чтение sync/async SQLite, duplicate email → 409. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, SQLAlchemy 2.1.8, aiosqlite 0.22.1; тесты использовали временные файлы

## [python/web/fastapi/dependency-overrides.md](../../python/web/fastapi/dependency-overrides.md)

- Сверено с документацией — 2026-11-06: FastAPI 0.162.0, release notes 0.162.0 от 2026-10-23; Starlette TestClient

- Выполнено — 2026-11-06: Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0, pytest 9.2.0; два теста самостоятельной программы и шесть расширенных тестов ниже

**Проверенное окружение**

Проверено указанное сочетание версий.
Другие версии не запускались.
Для повторения используйте Python 3.14.7.

## [python/web/fastapi/deployment.md](../../python/web/fastapi/deployment.md)

- Сверено с документацией — 2026-11-06: FastAPI 0.162.0, Uvicorn deployment и FastAPI Docker

- Выполнено — 2026-11-06: локальный Uvicorn 0.54.0 с `--reload` и `--workers 2` вернул `200` и ожидаемое приветствие; Python 3.14.7, FastAPI 0.162.0. Docker build/run и Gunicorn не выполнялись

## [python/web/fastapi/recipes.md](../../python/web/fastapi/recipes.md)

- Сверено с документацией — 2026-11-06, FastAPI 0.162.0 и Pydantic v2

- Выполнено — 2026-11-06: CRUD, валидация, фильтрация ответа, зависимости, формы/файлы и CORS проверены через TestClient. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0, python-multipart 0.0.33

## [python/web/fastapi/testing.md](../../python/web/fastapi/testing.md)

- Сверено с документацией — 2026-11-06: FastAPI 0.162.0, Starlette TestClient, HTTPX/HTTPX2

- Выполнено ранее — 2026-11-06: 14 Python-блоков скомпилированы; 45 тестов прошли без предупреждений до выделения примера подмены

- Проверка после переработки подмены — [Отдельное окружение, сценарии и версии](../../python/web/fastapi/dependency-overrides.md#среда-примеров); остальные тесты повторно не запускались

**Проверенное окружение**

- Компонент — Версия успешного запуска
- Python / FastAPI / Pydantic — 3.14.7 / 0.162.0 / 2.14.3
- Starlette / HTTPX2 — 1.10.0 / 2.16.0
- pytest / pytest-asyncio — 9.2.0 / 1.4.1.post1
- python-multipart / email-validator — 0.0.33 / 2.3.0
- SQLAlchemy / aiosqlite — 2.1.8 / 0.22.1
- PyJWT / pwdlib — 2.15.1 / 0.3.1 с Argon2

Проверено конкретное сочетание версий из таблицы.
Совместимость со всеми версиями не подтверждена.
Эти тесты не запускали Docker/Gunicorn и настоящий сетевой сервер.
Статус этих сценариев в прежней редакции был указан на [странице деплоя](../../python/web/fastapi/deployment.md).

## [python/web/flask/README.md](../../python/web/flask/README.md)

- Сверено с документацией — 2026-11-06, официальная документация Flask 3.1.x

- Выполнено — 2026-11-06, Python 3.14.7, Flask 3.1.3, Werkzeug 3.1.9, pytest 9.2.0; test client и SQLite lifecycle в temp-каталоге

## [python/web/flask/application.md](../../python/web/flask/application.md)

2026-11-06: приложение скомпилировано и проверено HTTP test client на Flask 3.1.3 / Werkzeug 3.1.9.

В этой проверке использован test client.
Открытый HTTP-сервер не использовался.

Сетевой запуск приведён как инструкция.

## [python/web/flask/configuration-and-deployment.md](../../python/web/flask/configuration-and-deployment.md)

2026-11-06: SQLite lifecycle выполнен на Python 3.14.7 / Flask 3.1.3.

Производительность и число workers здесь не измерялись.

Production WSGI, TLS, proxy, migrations, сессии браузера и многопроцессная БД не запускались.

Команда **не выполнялась**:

## [python/web/flask/testing.md](../../python/web/flask/testing.md)

Выполнено 2026-11-06: Python 3.14.7, Flask 3.1.3, Werkzeug 3.1.9, pytest 9.2.0.

Реальный WSGI-сервер, browser JavaScript, CSRF и production-деплой этим набором не проверялись.

**Источник и границы проверки**
