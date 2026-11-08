# Выполнить полные проверки FastAPI

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
Используйте [точные зависимости](testing.md#среда-примеров) и [подготовку учебных файлов](testing.md#подготовка).
Полные файлы приложений: [main.py](http-api.md), [uploads.py](uploads.md), [middleware_app.py](middleware.md), [БД](database.md), [JWT](authentication.md).
Сохраните нужное приложение и соответствующий тест рядом.
Запустите `python -m pytest -q -o asyncio_default_fixture_loop_scope=function`.

## Синхронный TestClient

Полный файл `test_main.py` использует `main.py` из HTTP-рецепта.
Фикстура очищает учебный словарь до и после каждого теста.
Поэтому тесты не зависят от порядка запуска.

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

Полный файл `test_database.py`.
Каждый тест получает свой файл SQLite в `tmp_path`.
До запуска lifespan тест подменяет движок и фабрику.
Основные учебные БД не меняются.

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

Полный файл `test_auth.py`.
До импорта приложения тесты назначают фиксированный учебный ключ в своём процессе.
Назначение не зависит от переменной окружения родительского процесса.
Для реального запуска выполните [подготовку ключа](authentication.md#подготовка).

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

Эти тесты проверяют учебные контракты.
Нагрузку, реальный прокси, HTTPS и интеграцию с внешним провайдером входа эти тесты не проверяют.
Положительный HTTP-ответ не подтверждает защищённость всей системы.

## Источники

- [FastAPI: TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette: текущие зависимости TestClient и async-клиент](https://starlette.dev/testclient/).
- [FastAPI: async-тесты и lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0: удаление app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio: маркер asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
