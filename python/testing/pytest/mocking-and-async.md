# Моки и асинхронные тесты

Уровень: продвинутый.
Предпосылки: [demo_service.py](fixtures.md#полный-учебный-пример),
pytest, pytest-mock и pytest-asyncio в одном окружении.
[К справочнику pytest](README.md).

## Проверить внешний контракт без сети

Сохраните файл рядом с `demo_service.py`.
Запустите `python -m pytest -q test_async_mock.py --asyncio-mode=strict`.
Ниже приведён полный пример.
Пример не выполняет HTTP-запросы.
Пример заменяет адаптер в модуле, который использует этот адаптер.

<!-- example: pytest/test_async_mock.py -->
```python
import asyncio

import pytest
import pytest_asyncio

import demo_service


def test_status_label(mocker):
    adapter = mocker.patch(
        "demo_service.read_remote", autospec=True, return_value={"status": "ready"}
    )
    assert demo_service.status_label(7) == "order 7: ready"
    adapter.assert_called_once_with(7)


def test_remote_error_is_not_hidden(mocker):
    mocker.patch("demo_service.read_remote", side_effect=TimeoutError("slow"))
    with pytest.raises(TimeoutError, match="slow"):
        demo_service.status_label(7)


def test_environment_isolated(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "test")
    import os
    assert os.environ["DEMO_MODE"] == "test"


@pytest_asyncio.fixture
async def inbox():
    queue = asyncio.Queue()
    await queue.put("hello")
    yield queue
    assert queue.empty()


@pytest.mark.asyncio
async def test_async_result(inbox):
    value = await inbox.get()
    assert await demo_service.uppercase(value) == "HELLO"
```

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

## Источники и проверка

[pytest-mock](https://pytest-mock.readthedocs.io/en/latest/usage.html),
[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html),
[pytest-asyncio concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html),
[pytest-django helpers](https://pytest-django.readthedocs.io/en/latest/helpers.html).
Выполнено 2026-11-06: pytest 9.2.0, pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1.
Реальные Django-приложение, БД Django и внешние HTTP-интеграции не запускались.
