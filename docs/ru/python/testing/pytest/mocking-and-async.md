
# Моки и асинхронные тесты

[English](../../../../en/python/testing/pytest/mocking-and-async.md)

Откройте страницу, если тесту нужен ответ внешнего адаптера без сети или проверка `async def`.
Пример подменяет адаптер в модуле, который вызывает адаптер.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Проверить ответ и отказ адаптера | `mocker.patch`, `side_effect` | [Полный тестовый модуль](#проверить-внешний-контракт-без-сети) |
| Проверить async-функцию | `pytest.mark.asyncio`, async fixture | [Полный модуль](#проверить-внешний-контракт-без-сети) · [Event loop](#async-фикстуры-и-event-loop) |
| Выбрать клиент веб-приложения | Flask, Django или ASGI | [Границы интеграции](#тестирование-веб-приложений) |

Уровень: продвинутый.
Предпосылки: [demo_service.py](fixtures.md#полный-учебный-пример),
pytest, pytest-mock и pytest-asyncio в одном окружении.
Для асинхронного теста пригодятся [основы `asyncio`](../../language/asyncio.md).
[К справочнику pytest](README.md).
Точные версии пакетов указаны в [среде примеров](configuration.md#среда-примеров).


## Проверить внешний контракт без сети

Сохраните файл рядом с `demo_service.py`.
Запустите `python -m pytest -q test_async_mock.py --asyncio-mode=strict`.
Ниже приведён полный пример.
Пример не выполняет HTTP-запросы.
Пример заменяет адаптер в модуле, который использует этот адаптер.

[`pytest/test_async_mock.py`](../../../../../examples/python/testing/pytest/test_async_mock.py)

Ожидается **4 passed**.
После теста fixture проверяет, что очередь пуста.
Проверка выполняется также при исключении в тесте.
`mocker` автоматически снимает подмены.
`monkeypatch` восстанавливает изменённое окружение после теста.
Проверка конкретного вызова уместна на границе адаптера, где аргумент является частью контракта.
Подмена каждого внутреннего метода делает тест хрупким и скрывает реальные интеграционные ошибки.


## Async-фикстуры и event loop

В strict mode `@pytest.mark.asyncio` обозначает тест.
Оформляйте async fixture через `@pytest_asyncio.fixture`.
В auto mode плагин сам принимает asyncio-тесты и фикстуры.
При нескольких async-плагинах явный strict mode помогает разделить владение.
Не переиспользуйте объект, привязанный к закрытому loop.
Выбирайте scope fixture и `loop_scope` согласованно.
Для простых изолированных тестов оставляйте function.
`asyncio.run()` внутри уже работающего async-теста не нужен.
Вызов приведёт к ошибке.


## Тестирование веб-приложений

- Flask: создайте отдельные fixture `app` и `client = app.test_client()`. [Полный пример](../../web/flask/testing.md).
- Django: используйте `pytest-django`, настройки проекта и его fixture `client`/`db`.
  Один импорт `django.test.Client` не настраивает Django.
  Этот импорт также не даёт безопасную тестовую БД.
- Асинхронный HTTP-клиент не превращает синхронное WSGI-приложение в ASGI.


## Источники

[pytest-mock](https://pytest-mock.readthedocs.io/en/latest/usage.html),
[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html),
[pytest-asyncio concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html),
[pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html).
