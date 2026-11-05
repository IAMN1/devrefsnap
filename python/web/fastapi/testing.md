# Проверить API и отказ доступа

[Краткий справочник](README.md) · [Приложения для тестов](recipes.md) · [База данных](database.md) · [JWT](authentication.md)

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; async-клиент и изоляция БД — продвинутый |
| Предпосылки | pytest, HTTP, контекстные менеджеры; для async — `async`/`await` |
| Сверено с документацией | 2026-11-06: FastAPI 0.162.0, Starlette TestClient, HTTPX/HTTPX2 |
| Выполнено | 2026-11-06: 14 Python-блоков скомпилированы; 45 тестов прошли без предупреждений приведённой ниже командой |

## Навигация

- [Синхронный TestClient](#синхронный-testclient)
- [Подмена зависимости](#подмена-зависимости)
- [Асинхронный клиент](#асинхронный-клиент)
- [Файлы и middleware](#файлы-и-middleware)
- [Сессии БД и lifespan](#сессии-бд-и-lifespan)
- [Аутентификация](#аутентификация)

## Проверенное окружение

| Компонент | Версия успешного запуска |
| --- | --- |
| Python / FastAPI / Pydantic | 3.14.7 / 0.162.0 / 2.14.3 |
| Starlette / HTTPX2 | 1.10.0 / 2.16.0 |
| pytest / pytest-asyncio | 9.2.0 / 1.4.1.post1 |
| python-multipart / email-validator | 0.0.33 / 2.3.0 |
| SQLAlchemy / aiosqlite | 2.1.8 / 0.22.1 |
| PyJWT / pwdlib | 2.15.1 / 0.3.1 с Argon2 |

Это конкретное проверенное сочетание, а не обещание совместимости со всеми версиями. Docker/Gunicorn и настоящий сетевой сервер этими тестами не запускались; статус этих сценариев указан на [странице деплоя](deployment.md).

## Подготовка

Сохрани приложения из связанных страниц в одной учебной папке: `main.py`, `header_dependency.py`, `uploads.py`, `middleware_app.py`, `db_app.py`, `async_db_app.py`, `auth_app.py`. Файлы тестов ниже находятся рядом. Дополнительно к зависимостям приложений установи:

```bash
python -m pip install pytest pytest-asyncio httpx2
```

Текущий Starlette рекомендует `httpx2`; прежний `httpx` ещё поддерживается, но его использование в TestClient устаревает. В старых окружениях пример async-клиента можно адаптировать импортом из `httpx`, сохраняя `ASGITransport`. Прямой `AsyncClient(app=app)` не используй: этот аргумент удалён из HTTPX в 0.28.0.

Запуск из учебной папки: `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`. Опция явно задаёт область event loop для async-фикстур. Тесты выполняют запросы внутри процесса; сервер Uvicorn и внешняя сеть не нужны.

## Синхронный TestClient

Полный файл `test_main.py`; использует `main.py` из HTTP-рецепта. Фикстура очищает учебный словарь до и после каждого теста, чтобы тесты не зависели от порядка запуска.

<!-- example: test_main.py -->
```python
import pytest
from fastapi.testclient import TestClient

from main import app, items


@pytest.fixture
def client():
    items.clear()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    items.clear()


def test_crud(client):
    created = client.post("/items", json={"name": "Book", "price": 25, "tags": ["python"]})
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert client.get(f"/items/{item_id}").json()["name"] == "Book"
    listed = client.get("/items", params={"q": "Book", "tags": "python"})
    assert len(listed.json()) == 1
    changed = client.patch(f"/items/{item_id}", json={"price": 30})
    assert changed.status_code == 200
    assert changed.json()["name"] == "Book"
    assert changed.json()["price"] == 30
    replaced = client.put(f"/items/{item_id}", json={"name": "New", "price": 40})
    assert replaced.status_code == 200
    assert replaced.json()["tags"] == []
    deleted = client.delete(f"/items/{item_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/items/{item_id}").status_code == 404


def test_invalid_input(client):
    assert client.post("/items", json={"name": "Book", "price": -1}).status_code == 422
    assert client.post("/items", json={"name": "premium", "price": 1}).status_code == 422
    assert client.get("/items/not-an-integer").status_code == 422
    assert client.get("/items", params={"limit": 0}).status_code == 422


@pytest.mark.parametrize("method", ["POST", "PATCH"])
@pytest.mark.parametrize("field", ["price", "tax"])
@pytest.mark.parametrize("raw_value", ["1e999", "-1e999", '"Infinity"', '"-Infinity"', '"NaN"'])
def test_nonfinite_numbers_are_rejected_without_state_change(client, method, field, raw_value):
    original = client.post("/items", json={"name": "Book", "price": 25, "tax": 2}).json()
    if field == "price":
        raw = f'{{"name":"Book","price":{raw_value},"tax":2}}'
    else:
        raw = f'{{"name":"Book","price":25,"tax":{raw_value}}}'
    path = "/items" if method == "POST" else f'/items/{original["id"]}'
    response = client.request(method, path, content=raw, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["detail"]
    assert client.get("/items").json() == [original]


def test_patch_revalidates_whole_model(client):
    item_id = client.post("/items", json={"name": "premium", "price": 100}).json()["id"]
    assert client.patch(f"/items/{item_id}", json={"price": 1}).status_code == 422
    assert client.patch(f"/items/{item_id}", json={"name": None}).status_code == 422
    assert client.get(f"/items/{item_id}").json()["price"] == 100


def test_query_cookie_and_nested_path(client):
    client.post("/items", json={"name": "Book", "price": 25, "tags": ["python", "web"]})
    client.cookies.set("last_query", "Book")
    assert len(client.get("/items").json()) == 1
    assert client.get("/items", params={"q": "Other"}).json() == []
    repeated = client.get("/items", params=[("tags", "python"), ("tags", "web")])
    assert len(repeated.json()) == 1
    nested = client.get("/users/2/items/3", params={"short": "true"})
    assert nested.json() == {"user_id": 2, "item_id": 3, "short": True}


def test_output_does_not_expose_password(client):
    response = client.post("/user-preview", json={
        "username": "alice", "email": "alice@example.com", "password": "secret123",
    })
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "password" not in response.json()


def test_custom_responses(client):
    assert client.get("/stock/6").status_code == 409
    assert client.get("/custom").headers["X-Custom"] == "demo"
    assert "text/html" in client.get("/html").headers["content-type"]
    redirect = client.get("/redirect", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "/docs"
```

Контекст `with TestClient(app)` запускает lifespan. Фикстура задаёт `raise_server_exceptions=False`, чтобы ошибка сервера превратилась в ответ `500` и провалила проверку статуса. По умолчанию необработанное исключение пробрасывается в тест. Числовой тест отправляет сырой JSON: преобразование `1e999` в бесконечность не должно приводить ни к сохранению неверного товара, ни к ошибке сериализации ответа.

## Подмена зависимости

Полный `test_dependencies.py`. Подмена действует на объект исходной функции, а не на её строковое имя. В `finally` восстанавливается прежняя подмена, если она была.

<!-- example: test_dependencies.py -->
```python
from fastapi.testclient import TestClient

from header_dependency import app, verify_client


def test_real_header_check():
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        assert client.get("/checked", headers={"X-Client": "wrong"}).status_code == 400
        assert client.get("/checked", headers={"X-Client": "training-client"}).status_code == 200


def test_override():
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[verify_client] = lambda: None
    try:
        with TestClient(app) as client:
            assert client.get("/checked").json() == {"checked": True}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

## Асинхронный клиент

Полный `test_async.py`, использует `pytest-asyncio` и тот же `main.py`.

<!-- example: test_async.py -->
```python
import pytest
from httpx2 import ASGITransport, AsyncClient

from main import app, items


@pytest.mark.asyncio
async def test_async_request():
    items.clear()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/items", json={"name": "Async book", "price": 20})
            assert response.status_code == 201
            item_id = response.json()["id"]
            assert (await client.get(f"/items/{item_id}")).json()["name"] == "Async book"
    finally:
        items.clear()
```

`ASGITransport` сам не запускает lifespan. У `main.py` нет startup-ресурсов; для приложения с ними установи `asgi-lifespan` и оберни работу клиента в `async with LifespanManager(app)` из `asgi_lifespan`. Для клиентов БД особенно важно создать и использовать ресурсы в корректном event loop. Не запускай тесты общего in-memory-словаря параллельно в одном процессе.

## Файлы и middleware

Полный `test_integrations.py`. Содержимое файлов синтетическое; реальные пользовательские файлы не читаются.

<!-- example: test_integrations.py -->
```python
from fastapi.testclient import TestClient

from middleware_app import app as middleware_app
from uploads import MAX_BYTES, app as uploads_app


def test_form_and_files():
    with TestClient(uploads_app) as client:
        assert client.post("/form", data={"username": "alice"}).json() == {"username": "alice"}
        response = client.post("/upload", files={"file": ("demo.txt", b"abc", "text/plain")})
        assert response.status_code == 200
        assert response.json() == {"filename": "demo.txt", "size": 3}
        multiple = client.post("/uploads", files=[
            ("files", ("a.txt", b"a", "text/plain")),
            ("files", ("b.txt", b"bb", "text/plain")),
        ])
        assert [item["size"] for item in multiple.json()] == [1, 2]
        assert client.post("/upload").status_code == 422
        too_big = client.post("/upload", files={"file": ("large.txt", b"x" * (MAX_BYTES + 1))})
        assert too_big.status_code == 413


def test_cors_and_timing():
    with TestClient(middleware_app) as client:
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert float(response.headers["X-Process-Time"]) >= 0
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        preflight = client.options("/", headers={
            "Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET",
        })
        assert preflight.status_code == 200
        denied = client.get("/", headers={"Origin": "http://untrusted.example"})
        assert "Access-Control-Allow-Origin" not in denied.headers
```

## Сессии БД и lifespan

Полный `test_database.py`. Каждому тесту выделяется свой файл SQLite в `tmp_path`; движок и фабрика подменяются до запуска lifespan. Основные учебные БД не меняются.

<!-- example: test_database.py -->
```python
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

import async_db_app
import db_app


def test_sync_database(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'users.db'}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(db_app, "engine", engine)
    monkeypatch.setattr(db_app, "SessionLocal", sessionmaker(engine))
    with TestClient(db_app.app) as client:
        body = {"username": "alice", "email": "alice@example.com"}
        created = client.post("/users", json=body)
        assert created.status_code == 201
        assert created.json()["id"] == 1
        assert client.post("/users", json=body).status_code == 409
        assert len(client.get("/users").json()) == 1


def test_async_database(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'notes.db'}")
    monkeypatch.setattr(async_db_app, "engine", engine)
    monkeypatch.setattr(async_db_app, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    with TestClient(async_db_app.app) as client:
        created = client.post("/notes", json={"text": "Учебная заметка"})
        assert created.status_code == 201
        assert client.get("/notes").json() == [{"id": 1, "text": "Учебная заметка"}]
        assert client.post("/notes", json={"text": ""}).status_code == 422
```

## Аутентификация

Полный `test_auth.py`. Фиксированный учебный ключ назначается в процессе тестов до импорта приложения, независимо от переменной окружения родительского процесса. Для реального запуска следуй [подготовке ключа](authentication.md#подготовка).

<!-- example: test_auth.py -->
```python
import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = "testing-only-secret-key-never-use-in-production-1234567890"
from auth_app import ALGORITHM, SECRET_KEY, app, issue_token, users


def test_login_and_protected_route():
    with TestClient(app) as client:
        response = client.post("/token", data={"username": "alice", "password": "training-password-123"})
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        token = response.json()["access_token"]
        me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json() == {"username": "alice"}


@pytest.mark.parametrize("username,password", [
    ("alice", "wrong-password"), ("unknown", "training-password-123"),
])
def test_invalid_credentials(username, password):
    with TestClient(app) as client:
        response = client.post("/token", data={"username": username, "password": password})
        assert response.status_code == 401
        assert "access_token" not in response.json()


def test_missing_token():
    with TestClient(app) as client:
        response = client.get("/users/me")
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("kind", ["malformed", "expired", "wrong-key", "wrong-algorithm", "no-exp", "no-sub", "unknown-user"])
def test_invalid_tokens(kind):
    claims = {"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    key, algorithm = SECRET_KEY, ALGORITHM
    if kind == "expired":
        claims["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    elif kind == "no-exp":
        del claims["exp"]
    elif kind == "no-sub":
        del claims["sub"]
    elif kind == "unknown-user":
        claims["sub"] = "unknown"
    elif kind == "wrong-key":
        key = "different-test-key-1234567890123456789012345678901234567890"
    elif kind == "wrong-algorithm":
        algorithm = "HS384"
    token = "not.a.valid-token" if kind == "malformed" else jwt.encode(claims, key, algorithm=algorithm)
    with TestClient(app) as client:
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


def test_disabled_user(monkeypatch):
    monkeypatch.setitem(users["alice"], "disabled", True)
    with TestClient(app) as client:
        token = issue_token("alice")
        assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
```

Эти тесты проверяют учебные контракты, но не нагрузку, реальный прокси, HTTPS и интеграцию с внешним провайдером входа. Положительный HTTP-ответ не подтверждает защищённость всей системы.

## Источники

- [FastAPI: TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette: текущие зависимости TestClient и async-клиент](https://starlette.dev/testclient/).
- [FastAPI: async-тесты и lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0: удаление app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio: маркер asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
