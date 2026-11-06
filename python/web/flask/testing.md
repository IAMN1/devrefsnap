# Тестирование Flask без сетевого сервера

Уровень: средний. Предпосылки: [flask_app.py](application.md), Flask и pytest в окружении.
[К справочнику Flask](README.md).

## Полный набор проверок

Сохраните полный пример рядом с приложением как `test_flask_app.py`.
Запустите `python -m pytest -q test_flask_app.py`.
Все данные синтетические.
Тесты не открывают сетевой порт.

<!-- example: flask/test_flask_app.py -->
```python
import pytest

from flask_app import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True, "MAX_CONTENT_LENGTH": 1024})


@pytest.fixture
def client(app):
    return app.test_client()


def test_item(client):
    response = client.get("/api/items/1")
    assert response.status_code == 200
    assert response.is_json
    assert response.json == {"id": 1, "name": "apple"}


def test_greet(client):
    response = client.post("/api/greet", json={"name": " Alice "})
    assert response.status_code == 200
    assert response.json == {"greeting": "Hello, Alice"}


@pytest.mark.parametrize("payload", [{}, {"name": " "}, {"name": 12}, []])
def test_invalid_name(client, payload):
    response = client.post("/api/greet", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Bad Request"


def test_media_type(client):
    response = client.post("/api/greet", data="name=Alice")
    assert response.status_code == 415


def test_malformed_json(client):
    response = client.post("/api/greet", data="{", content_type="application/json")
    assert response.status_code == 400


def test_unknown_item(client):
    response = client.get("/api/items/99")
    assert response.status_code == 404
    assert response.json["message"] == "item not found"


def test_method_not_allowed_preserves_header(client):
    response = client.post("/api/items/1")
    assert response.status_code == 405
    assert "GET" in response.headers["Allow"]


def test_template_escapes_input(client):
    response = client.get("/", query_string={"name": "<b>Alice</b>"})
    assert response.status_code == 200
    assert "&lt;b&gt;Alice&lt;/b&gt;" in response.text
    assert "<b>Alice</b>" not in response.text


def test_body_limit(client):
    response = client.post("/api/greet", json={"name": "x" * 2048})
    assert response.status_code == 413


def test_factory_instances_do_not_share_config():
    first = create_app({"TESTING": True, "DEMO_VALUE": "first"})
    second = create_app({"TESTING": True, "DEMO_VALUE": "second"})
    assert first.config["DEMO_VALUE"] == "first"
    assert second.config["DEMO_VALUE"] == "second"
```

Ожидается **13 passed**.
Тесты проверяют успешные ответы, ошибочные данные и маршрутизацию.
Тесты проверяют media type, лимит тела и сохранность HTTP-заголовка.
Тесты проверяют HTML-экранирование и независимость config.
Для route с авторизацией нужны отдельные проверки отсутствующей/недостаточной роли.
В этом учебном app аутентификации нет.

## Контекст и конфигурация тестов

`app.test_client()` вызывает WSGI-приложение внутри процесса.
Этот клиент не проверяет reverse proxy, TLS, настоящий WSGI worker, сетевые тайм-ауты и многопроцессное состояние.
Для тестов CLI существует `app.test_cli_runner()`.
`TESTING=True` помогает раскрывать неожиданные исключения в тестах.
Ожидаемые HTTPException приложение по-прежнему превращает в HTTP-ответ.

Для доступа к ресурсам app вне запроса используйте `with app.app_context():` в setup/CLI.
Если нужно проверить маршрутизацию, method или body, не подменяйте реальный запрос этим контекстом.
Если тест использует БД, выделите тесту собственный путь/транзакцию.
Проверьте очистку данных теста.
[SQLite lifecycle](configuration-and-deployment.md#жизненный-цикл-соединения) содержит отдельный тест закрытия ресурса.

## Источник и границы проверки

[Testing Flask](https://flask.palletsprojects.com/en/stable/testing/).
Выполнено 2026-11-06: Python 3.14.7, Flask 3.1.3, Werkzeug 3.1.9, pytest 9.2.0.
Реальный WSGI-сервер, browser JavaScript, CSRF и production-деплой этим набором не проверялись.
