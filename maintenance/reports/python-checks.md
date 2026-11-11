# Проверки Python-примеров

Ниже сохранены результаты запусков с исходными датами и версиями.
Сверка документации учитывалась отдельно от выполнения кода.
Результаты относятся к указанным версиям и сценариям; остальные версии не проверены.

## Двуязычный пилот N+1

11 ноября 2026 года проверены зеркальные пути, переходы между языками и ссылки на общий файл.
[Русская страница](../../docs/ru/python/databases/sqlalchemy/n-plus-one.md) · [English page](../../docs/en/python/databases/sqlalchemy/n-plus-one.md).
Прежний адрес сохраняет якоря и ведёт к тем же разделам русской страницы.
Полный [файл Python](../../examples/python/databases/sqlalchemy/n_plus_one.py) совпадает с исходным блоком.

Сверены описание [select-in loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#select-in-loading) и [release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
Среда запуска: macOS arm64, Python 3.14.7, SQLite 3.53.4, SQLAlchemy 2.1.8, typing-extensions 4.16.0.
В отдельное временное окружение установлена зависимость SQLAlchemy через `uv pip install --offline`.
Из временной папки запущен `python -B n_plus_one.py`. Проверки данных прошли, вывод совпал с обеими страницами.
Lazy loading выполнил 3 SELECT, `selectinload` выполнил 2 SELECT для тех же пользователей и постов.

Локально прошли `scripts/check_materials.py`, 26 тестов checker и `git diff --check`.
Тесты подтвердили отказ для верхнеуровневого `await` в самостоятельном файле и отсутствие исполнения примеров.
Этот прогон проверяет последовательное чтение двух пользователей в SQLite в памяти.
GitHub Actions проверяется при публикации PR.

## SQLAlchemy и Alembic — 6 ноября

Среда: macOS arm64, Python 3.14.7, SQLite 3.53.4, SQLAlchemy 2.1.8, pytest 9.2.0, greenlet 3.5.6.
Для async использован aiosqlite 0.22.1; для миграций — Alembic 1.20.1.
Файлы извлечены из Markdown и выполнены в отдельных временных окружениях.

| Сценарий | Выполнение и результат |
| --- | --- |
| [Общая схема и транзакции](../../docs/ru/python/databases/sqlalchemy/models-and-transactions.md) | `test_models.py`: 4 теста прошли |
| [Async и события](../../docs/ru/python/databases/sqlalchemy/async-and-operations.md) | 3 теста: roundtrip/отношения, неверный FK с rollback, наблюдение SQL |
| [Запросы](../../docs/ru/python/databases/sqlalchemy/queries.md) | 1 тест результатов SQLite; 4 PostgreSQL-выражения скомпилированы без сервера |
| [Потоковое чтение](../../docs/ru/python/databases/sqlalchemy/streaming.md) | `test_streaming.py`: 5 проверок обработки и ожидаемых ошибок на SQLite |
| [Миграция](../../docs/ru/python/databases/sqlalchemy/async-and-operations.md#alembic-отдельный-учебный-проект) | init/autogenerate/upgrade/current/history; добавление `verified`, backfill, NOT NULL и downgrade сохранили остальные поля |

Миграция выполнена на отдельном файле SQLite с синтетическим пользователем.
PostgreSQL-сервер, пул под нагрузкой и server-side cursors других драйверов не проверялись.

### Самостоятельный N+1

[Один файл](../../docs/ru/python/databases/sqlalchemy/n-plus-one.md) выполнен с SQLAlchemy 2.1.8 и typing_extensions 4.16.0.
Отсутствие greenlet и pytest проверено; общая схема с `AsyncAttrs` не импортируется.
`python n_plus_one.py` дал точный ожидаемый вывод.
Семь временных проверок `unittest` прошли с `-W error`; независимый рецензент повторил все семь.

Проверены пользователи, посты, пустые коллекции и пустая выборка родителей.
Для двух пользователей lazy/select-in дали 3/2 SELECT; для пяти — 6/2; для пустой выборки — 1/1.
Каждое сравнение использовало новую Session и одинаковые данные; подготовка не входила в счётчик.
Обработчик счётчика удалялся после успеха и исключения; посторонний обработчик сохранялся.
Время, память, сеть и другие СУБД не измерялись.

### Расширенная лабораторная загрузки

После уточнения [выбора стратегии](../../docs/ru/python/databases/sqlalchemy/relationship-loading.md) итоговый `test_relationship_loading.py` прошёл 22 теста.
Проверены `demo_models.py`, `demo_queries.py` и четыре короткие карточки на той же среде.

| Условие | Фактический результат |
| --- | --- |
| Два пользователя, затем ещё три без постов | Lazy/select-in/joined: 3/2/1 и 6/2/1 SELECT; состав данных совпал |
| Два поста одного автора в новых Session | 2/2/1 SELECT; автор — общий ORM-объект |
| Joined collection без `unique()` | `InvalidRequestError` |
| Строки joinedload через Connection | Три строки Alice, Alice, Bob до сборки ORM-объектов |
| LIMIT 1 по родителям | Обе стратегии сохранили Alice и два её поста |
| Явный JOIN с LIMIT 2 | Без лимита два родителя; с лимитом одна Alice с полной коллекцией |
| Необязательная `User.manager` | Alice с `None` и Bob с руководителем Alice сохранены обеими стратегиями |

Ревью выявило слабую проверку JOIN/LIMIT: у Bob первоначально не было постов.
После добавления поста Bob временное удаление `.limit(2)` вызвало ожидаемый `AssertionError`.
Восстановленный файл снова прошёл 22 теста; исправление принято повторным чтением рецензента.
Число SELECT и SQL-строк не является измерением ускорения, трафика или памяти.
SQL Server tuple IN, FOR UPDATE, конкуренция, async и другие драйверы не запускались.
API сверены 6 ноября с документацией SQLAlchemy 2.1 и release notes 2.1.8/2.1.7.

## FastAPI: восстановление подмен — 6 и 7 ноября

[Примеры подмены](../../docs/ru/python/web/fastapi/dependency-overrides.md) используют Python 3.14.7, FastAPI 0.162.0,
Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0 и pytest 9.2.0.
Каждый комплект извлечён из Markdown и запущен из своей папки.

6 ноября два минимальных, шесть расширенных тестов, карточка и восемь временных проб дали 17 прохождений с `-W error`.
Рецензент повторил 17 проверок; минимальная программа отдельно дала `2 passed`.
7 ноября после усиления восстановления получены следующие результаты:

| Команда | Файлы | Результат |
| --- | --- | --- |
| `python -m pytest -q test_dependency_override.py` | Один файл приложения и тестов | 2 passed |
| `python -m pytest -q test_dependencies.py` | `header_dependency.py` и тестовый модуль | 8 passed |
| `python -m pytest -q test_card.py` | Приложение и карточка | 1 passed |

Проверены исходные ответы 422/400/200, вызов подмены и ожидаемый JSON.
Восстановление проверено для пустого словаря, прежней подмены той же функции и посторонней записи.
Проверены обычный выход, ошибка assert и `RuntimeError` из зависимости.
После блока прежняя подмена снова дала 403; без прежней подмены исходная зависимость дала 422.
Проверки выполнялись до очистки autouse-фикстуры, поэтому фикстура не скрывала дефект восстановления.
Документация, исходники FastAPI 0.162.0 и release notes FastAPI/Starlette сверены 7 ноября.

Реальные БД, внешние провайдеры, конкурентное изменение app, async-клиенты и зависимости с `yield` не проверялись.
HTTP-запросы выполнялись внутри процесса; сеть и развёртывание эта проверка не подтверждает.

## Полные комплекты — 8 ноября

Среда: macOS arm64, CPython 3.14.6, SQLite 3.53.1.
uv выбрал managed-интерпретатор при запросе `--python python3`.
Это отдельный прогон, отличный от прежней среды Python 3.14.7 / SQLite 3.53.4.
56 файлов извлечены по маркерам `example:`; группы запускались отдельно из-за совпадающих имён модулей.
Команда каждой группы: `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`.

| Группа | Фактические основные пакеты | Результат |
| --- | --- | --- |
| [pytest](../../docs/ru/python/testing/pytest/README.md) | pytest 9.2.0, pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1 | 17 passed |
| [Pydantic](../../docs/ru/python/validation/pydantic/README.md) | Pydantic 2.14.3, pydantic-settings 2.16.2, email-validator 2.3.0 | 20 passed |
| [structlog](../../docs/ru/python/logging/structlog/README.md) | structlog 26.1.0, FastAPI 0.162.0 | 7 passed |
| [SQLAlchemy](../../docs/ru/python/databases/sqlalchemy/README.md) | SQLAlchemy 2.1.8, greenlet 3.5.6, aiosqlite 0.22.1 | 35 passed |
| [FastAPI](../../docs/ru/python/web/fastapi/README.md) | FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0, python-multipart 0.0.33, PyJWT 2.15.1, pwdlib 0.3.1 | 53 passed |
| [Flask](../../docs/ru/python/web/flask/README.md) | Flask 3.1.3, Werkzeug 3.1.9 | 14 passed |

Итого 146 тестов: допустимые входы, валидация, отказ доступа, rollback, изоляция данных и очистка контекста.
Типы дополнительно выполнены через `python demo_types.py`: проверки чисел, коллекций, ошибок преобразования и копий прошли.
Offline-сценарий `bash project.sh` прошёл на uv 0.12.13 / системном Python 3.14.7.
Получены `venv OK`, ожидаемый отказ несогласованного lock и `uv project OK`.

После пересоздания окружения с явным Python 3.14.7 отдельно выполнены 24 блока карточек и 4 pytest-карточки.
Проверены JSON-события, отсутствие DEBUG, HTTP 200/400/401/422, размер multipart и восстановление overrides.
Полный набор 146 тестов на этом интерпретаторе повторно не запускался.

## Самостоятельная подготовка — 10 ноября

Среда: macOS arm64, CPython 3.14.7, SQLite 3.53.4, uv 0.12.13.
Наборы `web`, `core`, `settings`, `logs`, `logweb`, `alembic` установлены в шесть отдельных venv.
Программы и тесты извлечены из Markdown без изменения Python-кода.

| Набор и прямые зависимости | Адресный запуск pytest | Результат |
| --- | --- | --- |
| web: FastAPI 0.162.0, Starlette 1.10.0, pytest 9.2.0, HTTPX2 2.16.0 | `test_cors_only.py test_query.py` | 2 passed |
| core: Pydantic 2.14.3, pytest 9.2.0 | `test_advanced.py` | 2 passed |
| settings: pydantic-settings 2.16.2, pytest 9.2.0 | `test_settings.py` | 1 passed |
| logs: structlog 26.1.0, pytest 9.2.0, pytest-asyncio 1.4.1.post1 | `test_context.py -o asyncio_default_fixture_loop_scope=function` | 1 passed |
| logweb: structlog 26.1.0, FastAPI 0.162.0, Starlette 1.10.0, HTTPX2 2.16.0, pytest 9.2.0 | `test_web.py` | 1 passed |
| web + python-multipart 0.0.33, uvicorn[standard] 0.54.0 | `test_integrations.py` | 2 passed |
| web + pydantic[email] 2.14.3, email-validator 2.3.0, sqlalchemy[asyncio] 2.1.8, aiosqlite 0.22.1 | `test_main.py::test_crud test_main.py::test_invalid_input test_database.py` | 4 passed |
| web: адресная проверка событий | `test_observe.py` | 1 passed |

Команды выполнялись через `python -m pytest -q` с указанным выбором.
Всего 14 прохождений; CORS повторён на двух этапах подготовки.
`test_cors_only.py` содержит неизменённый `test_cors_and_timing`, выделенный для запуска без multipart-приложения.
Первый web-набор не содержал БД, JWT, email-validator и multipart.
В core не было FastAPI/settings; в settings и logs не было FastAPI; в logweb не было pytest-asyncio.
Проверены сокращённые зависимости, а не только работа в прежнем полном окружении.

Ревью исправило два P2: зависимости общей модели в Alembic и общий pytest вместо выбранного файла событий.
В чистый venv миграции через `uv pip install` установлены только прямые зависимости `sqlalchemy[asyncio]==2.1.8` и `alembic==1.20.1`.
Транзитивные зависимости: greenlet 3.5.6, Mako 1.4.3, MarkupSafe 3.0.4, typing_extensions 4.16.0.
pytest, aiosqlite и веб-пакеты отсутствовали.

В новом учебном проекте выполнены `alembic init alembic`, `alembic revision --autogenerate`, `alembic upgrade head`, `alembic current`.
Использованы `sqlite:///training-migrations.db` и `Base.metadata` неизменённого `demo_models.py`.
В revision добавлен `import demo_models` для `demo_models.JSONDict()`.
Все команды дали код 0; current показал `87821fc84efd (head)`.
Inspector обнаружил семь таблиц модели и `alembic_version` с той же revision.
Рецензент проверил журнал, состав venv, revision и конечную БД в режиме read-only.
Последующие миграции, downgrade и восстановление в этом прогоне не выполнялись.

`test_observe.py` повторён рецензентом: 1 passed.
Этот тест запускался в расширенном web-окружении с aiosqlite и веб-пакетами.
Отдельный минимальный venv событий не проверялся; исправление подтверждает адресный выбор модуля.

## Другие уникальные проверки и границы

6 ноября на Python 3.14.7 дополнительно выполнены:

- pytest-cov 7.1.0: терминальный и HTML-отчёт; pytest-xdist 3.8.0: два workers; JUnit XML, сборка и выбор тестов.
- Pydantic 2.14.3: timezone-aware ввод и UTC-сериализация; timestamp-тесты при `TZ=UTC` и `Europe/Moscow`.
- structlog 26.1.0: сохранённый `exc_info` вне except для JSON/console; async-изоляция и FastAPI success/error.
- FastAPI 0.162.0: SQLite sync/async lifespan, запись/чтение и duplicate email → 409; JWT-вход и отказы доступа.
- Uvicorn 0.54.0: локальные `--reload` и `--workers 2` вернули 200 и ожидаемое приветствие.
- Flask 3.1.3 / Werkzeug 3.1.9: HTTP test client и SQLite lifecycle во временном каталоге.

Это результаты разных дат и объёмов; они не образуют единую матрицу совместимости.
Django-проект, JSON-плагин pytest, PaymentCardNumber, автоматическая миграция Pydantic и benchmarks не запускались.
Docker build/run, Gunicorn, TLS/reverse proxy, браузерный CORS и production WSGI не проверялись.
Иллюстрации изменения рабочей БД, реальные OAuth-провайдеры и нагрузка не выполнялись.
Сверка API/release notes 6 и 8 ноября не означает запуск всех описанных конфигураций.
Удобство материала с реальными читателями не измерялось.
