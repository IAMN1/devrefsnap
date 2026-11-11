
# Выполнить полные проверки FastAPI

[English](../../../../en/python/web/fastapi/testing-lab.md)

Откройте страницу, чтобы воспроизвести полный тестовый модуль для конкретного учебного приложения.
Выберите одну задачу; TestClient и ASGITransport выполняют запросы внутри процесса.

| Задача | Приём | Полный модуль |
| --- | --- | --- |
| Проверить CRUD, PATCH и неверный ввод | `TestClient` и изоляция словаря | [test_main.py](#синхронный-testclient) |
| Проверить async-запрос | `ASGITransport` и pytest-asyncio | [test_async.py](#асинхронный-клиент) |
| Проверить multipart и CORS | Синтетические bytes и preflight | [test_integrations.py](#файлы-и-middleware) |
| Проверить БД и lifespan | Отдельная SQLite на тест | [test_database.py](#сессии-бд-и-lifespan) |
| Проверить пароль, JWT и отказ | Реальная учебная проверка токена | [test_auth.py](#аутентификация) |

[Короткие карточки](testing.md) · [Приложения](recipes.md) · [Подмена зависимости](dependency-overrides.md)

Уровень: средний; async и БД — продвинутый.
Предпосылки: pytest, HTTP; для async — `async`/`await`.
Установите [пакеты выбранного приложения](testing.md#среда-примеров) и [подготовьте нужные файлы](testing.md#подготовка).
Полные файлы приложений: [main.py](http-api.md), [uploads.py](uploads.md), [middleware_app.py](middleware.md), [БД](database.md), [JWT](authentication.md).
Сохраните нужное приложение и соответствующий тест рядом.
Запустите `python -m pytest -q ИМЯ_ТЕСТОВОГО_ФАЙЛА.py`.
Для async-тестов добавьте `-o asyncio_default_fixture_loop_scope=function`.


## Синхронный TestClient

Полный файл `test_main.py` использует `main.py` из HTTP-рецепта.
Фикстура очищает учебный словарь до и после каждого теста.
Поэтому тесты не зависят от порядка запуска.

[`test_main.py`](../../../../../examples/python/web/fastapi/test_main.py)

Контекст `with TestClient(app)` запускает lifespan.
Фикстура задаёт `raise_server_exceptions=False`.
При этой настройке ошибка сервера превращается в ответ `500`.
Такой ответ проваливает проверку статуса.
По умолчанию необработанное исключение пробрасывается в тест.
Числовой тест отправляет сырой JSON.
Преобразование `1e999` в бесконечность не должно приводить к сохранению неверного товара.
Это преобразование также не должно вызывать ошибку сериализации ответа.


## Асинхронный клиент

Полный файл `test_async.py` использует `pytest-asyncio` и тот же `main.py`.

[`test_async.py`](../../../../../examples/python/web/fastapi/test_async.py)

`ASGITransport` сам не запускает lifespan.
У `main.py` нет startup-ресурсов.
Если приложение имеет startup-ресурсы, установите `asgi-lifespan`.
При наличии startup-ресурсов оберните работу клиента в `async with LifespanManager(app)` из `asgi_lifespan`.
Для клиентов БД особенно важно создать и использовать ресурсы в корректном event loop.
Не запускайте тесты общего in-memory-словаря параллельно в одном процессе.


## Файлы и middleware

Полный файл `test_integrations.py`.
Содержимое файлов синтетическое.
Тесты не читают реальные пользовательские файлы.

[`test_integrations.py`](../../../../../examples/python/web/fastapi/test_integrations.py)


## Сессии БД и lifespan

Полный файл `test_database.py`.
Каждый тест получает свой файл SQLite в `tmp_path`.
До запуска lifespan тест подменяет движок и фабрику.
Основные учебные БД не меняются.

[`test_database.py`](../../../../../examples/python/web/fastapi/test_database.py)


## Аутентификация

Полный файл `test_auth.py`.
До импорта приложения тесты назначают фиксированный учебный ключ в своём процессе.
Назначение не зависит от переменной окружения родительского процесса.
Для реального запуска выполните [подготовку ключа](authentication.md#подготовка).

[`test_auth.py`](../../../../../examples/python/web/fastapi/test_auth.py)

Эти тесты проверяют учебные контракты.
Нагрузку, реальный прокси, HTTPS и интеграцию с внешним провайдером входа эти тесты не проверяют.
Положительный HTTP-ответ не подтверждает защищённость всей системы.


## Источники

- [FastAPI: TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette: текущие зависимости TestClient и async-клиент](https://starlette.dev/testclient/).
- [FastAPI: async-тесты и lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0: удаление app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio: маркер asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
