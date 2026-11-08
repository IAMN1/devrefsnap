# Python: формат для быстрого повторения — 2026-11-08

Область: `python/**`, кроме `python/README.md` и `python/architecture/**`.
Проверены 34 исходных файла.
Добавлены четыре предметные страницы FastAPI.
Итог: 38 файлов; 29 исходных изменены, пять сохранены, четыре добавлены.
Общую навигацию и указатель задач обновляет координатор.

## Изменения и сохранённое покрытие

- Обзор задач перемещён перед параметрами и длинной навигацией в справочниках uv, pytest, structlog, Pydantic и Flask.
- Справочник типов получил третий столбец с прямыми ссылками.
- Справочники получили короткие карточки с данными, изменением, кодом, результатом и ограничением.
- Подробные страницы получили назначение, условие применения и таблицу выбора на первом экране.
- Полные программы остаются учебными задачами с подготовкой, версиями и запуском.
- FastAPI `recipes.md` теперь содержит карточки PATCH, зависимостей, файлов и CORS.
- Полный CRUD перенесён в `http-api.md`; независимые приложения файлов и middleware — в `uploads.md` и `middleware.md`.
- Полные тестовые модули FastAPI перенесены в `testing-lab.md`.
- Прежние якоря `recipes.md` и `testing.md` сохранены как карточки с прямыми ссылками на полные файлы.
- Пример заголовка, карточка подмены и `dependency-overrides.md` сохранены по существу.
- SQLAlchemy loading, N+1 и streaming сохранены без редактирования.
- Две Mermaid-схемы получили смысл представления и подписи отношений.
- Источники SQLAlchemy на странице FastAPI БД приведены к ветке 2.1, используемой окружением примеров.

Сравнение исходных и итоговых fenced blocks не обнаружило удалённых или изменённых блоков программ, команд и конфигураций.
Из 120 исходных блоков 118 сохранены дословно; изменены только две Mermaid-схемы pytest и Flask.
Сохранены типы, коллекции, ошибки преобразования, изменяемость, группы uv, lock, CI, Docker, Pydantic validators/settings/generics/migration, pytest fixtures/mocks/async, structlog processors/context/stdlib, SQLAlchemy schema/CRUD/queries/loading/async/Alembic и HTTP-задачи обоих фреймворков.

## Пофайловый итог

| Путь | Итог | Конкретное основание |
| --- | --- | --- |
| `python/language/types/README.md` | Изменён | Ссылки выбора типа; короткие примеры Decimal, set, None и глубины копии; уровни и исходные таблицы сохранены |
| `python/language/types/recipes.md` | Изменён | Обзор ведёт к полной программе и результату; программа сохранена |
| `python/tooling/uv/README.md` | Изменён | Выбор до навигации; карточки нового проекта, dev-зависимости и locked CI |
| `python/tooling/uv/projects.md` | Изменён | Первый экран различает offline-сценарий, изменение зависимостей, режимы lock и экспорт |
| `python/tooling/uv/automation.md` | Изменён | Выбор CI, контейнера, pre-commit и диагностики до конфигураций |
| `python/validation/pydantic/README.md` | Изменён | Обзор до настроек; карточки преобразования, согласования скидки и списка через TypeAdapter |
| `python/validation/pydantic/models.md` | Изменён | Быстрый выбор проверки входа, публичной модели и чтения атрибутов; полные файлы сохранены |
| `python/validation/pydantic/advanced.md` | Изменён | Обзор разделяет generic/adapter, settings, query и миграцию |
| `python/testing/pytest/README.md` | Изменён | Обзор поднят; короткие тесты результата, отказа, изоляции fixture и адаптера; схема подписана |
| `python/testing/pytest/configuration.md` | Изменён | Обзор различает конфигурацию, выбор тестов, плагины и среду |
| `python/testing/pytest/fixtures.md` | Изменён | Обзор полного набора, scope, фабрик и параметризации до программы |
| `python/testing/pytest/mocking-and-async.md` | Изменён | Явный выбор адаптера, async-теста и веб-клиента; полный модуль сохранён |
| `python/logging/structlog/README.md` | Изменён | Обзор поднят; карточки bind, contextvars и проверки уровня; смысл схемы указан |
| `python/logging/structlog/configuration.md` | Изменён | Первый экран выбирает renderer, маскирование, stdlib и раннюю проверку DEBUG |
| `python/logging/structlog/context-and-web.md` | Изменён | Первый экран выбирает временный контекст, ASGI и sync Django |
| `python/databases/sqlalchemy/README.md` | Изменён | Короткие карточки транзакции, нескольких колонок и select-in; полная схема остаётся отдельно |
| `python/databases/sqlalchemy/models-and-transactions.md` | Изменён | Обзор схемы, CRUD и savepoint; полный код сохранён |
| `python/databases/sqlalchemy/queries.md` | Изменён | Названы применение и граница PostgreSQL-компиляции; существующий выбор и код сохранены |
| `python/databases/sqlalchemy/async-and-operations.md` | Изменён | Первый экран выбирает async-чтение, события и отдельную миграцию |
| `python/databases/sqlalchemy/relationship-loading.md` | Сохранён | Уже есть обзор, таблица решений, самодостаточные карточки, ограничения и прямые ссылки на лабораторную |
| `python/databases/sqlalchemy/n-plus-one.md` | Сохранён | Уже есть самостоятельный вход, термины, короткое изменение, полная программа, вывод и ограничения |
| `python/databases/sqlalchemy/loading-lab.md` | Сохранён | Отдельная подробная лабораторная уже имеет первый экран, подготовку, тесты и условия численного сравнения |
| `python/databases/sqlalchemy/streaming.md` | Сохранён | Уже есть карточка пакетного чтения, результаты, таблица несовместимости и полные тесты |
| `python/web/fastapi/README.md` | Изменён | Сохранён первый запуск; добавлены карточки публичного ответа и сессии с yield |
| `python/web/fastapi/recipes.md` | Изменён | Полные независимые программы вынесены; прежние якоря стали короткими карточками; заголовок сохранён |
| `python/web/fastapi/http-api.md` | Добавлен | Полный CRUD с моделями, PATCH, ошибками и фильтрацией пароля перенесён дословно |
| `python/web/fastapi/uploads.md` | Добавлен | Самостоятельная задача multipart: полный код, зависимости, запуск, результаты и ограничения |
| `python/web/fastapi/middleware.md` | Добавлен | Самостоятельная задача CORS/таймера с полным кодом и ограничениями |
| `python/web/fastapi/testing.md` | Изменён | Длинные комплекты отделены от карточек; override сохранён; прежние якоря ведут к полным тестам |
| `python/web/fastapi/testing-lab.md` | Добавлен | Полные синхронные, async, multipart, CORS, DB и JWT-тесты перенесены без изменения кода |
| `python/web/fastapi/dependency-overrides.md` | Сохранён | Недавняя страница уже содержит самостоятельный вход, выбор, проверки восстановления и ограничения |
| `python/web/fastapi/database.md` | Изменён | Обзор sync/async и проверок; официальные SQLAlchemy-ссылки соответствуют ветке окружения |
| `python/web/fastapi/authentication.md` | Изменён | Первый экран выбирает подготовку, приложение, проверку отказа и границы JWT-рецепта |
| `python/web/fastapi/deployment.md` | Изменён | Первый экран разделяет reload, workers, Gunicorn, контейнер и OpenAPI |
| `python/web/flask/README.md` | Изменён | Обзор поднят; карточки HTTP-ответа, независимости config и SQLite lifecycle; схема подписана |
| `python/web/flask/application.md` | Изменён | Обзор factory, JSON/ошибок, запуска и других ответов до полного приложения |
| `python/web/flask/testing.md` | Изменён | Обзор проверок JSON, заголовков, HTML и контекстов до полного тестового модуля |
| `python/web/flask/configuration-and-deployment.md` | Изменён | Обзор config, границы соединения и WSGI до подробностей |

## Выполненные проверки

Временная папка: `/private/tmp/python-format-refresh`.
Зависимости размещены в отдельном `.venv`; зависимости репозитория не менялись.
Полные файлы извлечены из блоков `<!-- example: ... -->` с сохранением исходных имён.
Экспортировано 56 файлов программ и конфигураций.
Группы запускались отдельно, чтобы одинаковые имена учебных модулей не пересекались.

### Поведенческие запуски полных комплектов

Среда полного прогона: CPython 3.14.6, SQLite 3.53.1, macOS arm64.
uv выбрал этот managed-интерпретатор при запросе `--python python3`.
Это отличается от исторической среды примеров CPython 3.14.7 / SQLite 3.53.4.
Версии пакетов ниже установлены фактически.

Команда каждой группы: `/private/tmp/python-format-refresh/.venv/bin/python -m pytest -q -o asyncio_default_fixture_loop_scope=function`.
Рабочий каталог: `/private/tmp/python-format-refresh/examples/<группа>`.

| Группа | Основные фактические пакеты | Результат |
| --- | --- | --- |
| `pytest` | pytest 9.2.0, pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1 | 17 passed |
| `pydantic` | Pydantic 2.14.3, pydantic-settings 2.16.2, email-validator 2.3.0 | 20 passed |
| `structlog` | structlog 26.1.0, FastAPI 0.162.0 | 7 passed |
| `sqlalchemy` | SQLAlchemy 2.1.8, greenlet 3.5.6, aiosqlite 0.22.1 | 35 passed |
| `fastapi` | FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0, python-multipart 0.0.33, PyJWT 2.15.1, pwdlib 0.3.1 | 53 passed |
| `flask` | Flask 3.1.3, Werkzeug 3.1.9 | 14 passed |

Итого: **146 passed**.
Проверены допустимые входы, ошибки валидации, отказ доступа, откат, изоляция данных и очистка контекста.
Успешный полный набор после переноса также подтверждает работоспособность имён файлов и импортов учебных модулей.

Дополнительный запуск: `python /private/tmp/python-format-refresh/examples/types/demo_types.py`.
Результат: `types: numbers, collections, conversion errors and copies OK`.

Полный Bash-сценарий: `bash /private/tmp/python-format-refresh/examples/uv/project.sh`.
Среда: uv 0.12.13 и явно найденный системный CPython 3.14.7.
Результат: `venv OK`, ожидаемый отказ несогласованного lock и `uv project OK`.
Сценарий работает offline и удаляет только собственную временную папку.

### Короткие карточки и статическая проверка

После выявления выбора managed Python временное окружение пересоздано с явным системным Python 3.14.7.
Полный набор 146 тестов повторно не запускался.
Новые короткие карточки проверены отдельно в этой среде.

- Выполнены 24 блока карточек README и FastAPI testing с указанным контекстом импортов и подготовки.
- Там, где фрагмент продолжает программу, использованы исходные `demo_models.py`, `seed()`, factory и зависимости.
- Четыре теста карточек pytest выполнены отдельно: `4 passed`.
- Проверены реальные JSON-события bind/contextvars и отсутствие DEBUG-вывода.
- Проверены `200/400/401/422`, multipart-размер и восстановление override в карточках тестирования.
- Блок подготовки движка через `tmp_path` не запускался отдельно; соответствующий полный DB-тест входит в 53 passed.
- Скомпилированы все **100 Python-блоков** области на CPython 3.14.7; синтаксических ошибок нет.
- Проверены **556 относительных ссылок**, включая якоря; отсутствующих целей нет.
- Проверены языки и парность всех 152 ограждённых блоков области; ошибок нет.
- Сравнены исходные fenced blocks; потеря программ, команд и конфигураций не обнаружена.

Разовые скрипты проверки находятся только в `/private/tmp/python-format-refresh`.
Постоянная инфраструктура проверок в репозиторий не добавлялась.

## Сверка официальной документации

Сверка выполнена 2026-11-08.
Она подтверждает назначение API и ограничения; сама по себе она не означает выполнение примера.
Версии в материалах обозначают среду примера и не объявляются последними доступными версиями.

| Тема | Официальные страницы | Что сверено |
| --- | --- | --- |
| Python 3.14 | [Типы](https://docs.python.org/3.14/library/stdtypes.html), [copy](https://docs.python.org/3.14/library/copy.html), [изменения 3.14](https://docs.python.org/3.14/whatsnew/3.14.html) | Множества, None, десятичные значения и границы копирования |
| uv 0.12.13 | [Lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/), [release 0.12.13](https://github.com/astral-sh/uv/releases/tag/0.12.13) | `--locked`, `--frozen`, обновление зависимостей |
| Pydantic v2 | [Модели](https://docs.pydantic.dev/latest/concepts/models/), [validators](https://docs.pydantic.dev/latest/concepts/validators/), [changelog](https://docs.pydantic.dev/latest/changelog/) | Преобразование, ошибка модели, validator after, TypeAdapter и версия 2.14.3 |
| pytest 9 | [Fixture](https://docs.pytest.org/en/stable/how-to/fixtures.html), [changelog 9.2.0](https://docs.pytest.org/en/stable/changelog.html#pytest-9-2-0-2026-10-27) | Время жизни fixture, очистка и ветка pytest |
| structlog 26.1 | [Contextvars](https://www.structlog.org/en/stable/contextvars.html), [официальный changelog](https://github.com/hynek/structlog/blob/main/CHANGELOG.md) | Временный контекст и ограничения переноса между sync/async |
| SQLAlchemy 2.1 | [Транзакции](https://docs.sqlalchemy.org/en/21/orm/session_transaction.html), [release notes 2.1](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html) | Session/транзакция, savepoint; сохранённая версия 2.1.8 |
| FastAPI 0.162 | [Выходная модель](https://fastapi.tiangolo.com/tutorial/response-model/), [release notes](https://fastapi.tiangolo.com/release-notes/) | Фильтрация ответа; новые docs/internal releases 0.162.1–0.162.2 не требуют обновления учебного кода |
| Flask 3.1 | [Factory](https://flask.palletsprojects.com/en/stable/patterns/appfactories/), [changes](https://flask.palletsprojects.com/en/stable/changes/) | Независимые приложения, существующая ветка 3.1.3 |

## Непроверенные сценарии и границы

- Редакторская проверка маршрутов не является исследованием с читателями.
- Полные комплекты выполнены на Python 3.14.6 / SQLite 3.53.1; совпадение с каждым историческим patch-релизом не подтверждено.
- Новые карточки и синтаксис проверены на Python 3.14.7; это не повторный полный прогон.
- PostgreSQL-сервер, другие диалекты, SQL-планы, production-миграции и восстановление БД не запускались.
- Alembic upgrade/downgrade, Docker build, Gunicorn, CI и сетевые загрузки uv не выполнялись в этой редакторской задаче.
- HTTPS, reverse proxy, браузерный CORS, реальные OAuth-провайдеры, многопроцессность и нагрузка не проверялись.
- Django-фрагмент остаётся интеграционным фрагментом; полноценный Django-проект не запускался.
- Синтетические JWT-проверки не доказывают защищённость готовой системы.
- Новые темы, инфраструктура тестирования и внешняя публикация не добавлялись.
