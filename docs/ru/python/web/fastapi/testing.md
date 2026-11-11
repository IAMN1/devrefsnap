
# Проверить API и отказ доступа

[English](../../../../en/python/web/fastapi/testing.md)

[Краткий справочник](README.md) · [Приложения для тестов](recipes.md) · [База данных](database.md) · [JWT](authentication.md)

Откройте страницу, чтобы проверить HTTP-ответ или временно заменить зависимость в тесте.
`TestClient` отправляет запросы в приложение внутри процесса, без сетевого сервера.
Здесь зависимость — функция, которую FastAPI вызывает через `Depends` перед обработчиком.

| Ситуация | Приём | Пример |
| --- | --- | --- |
| Проверить создание объекта и неверный ввод | Запросы через `TestClient` | [CRUD и валидация](#синхронный-testclient) |
| Проверить саму проверку заголовка | Оставить исходную зависимость; передать разные заголовки | [Исходная функция](recipes.md#проверка-заголовка-перед-обработчиком) · [Полный тест](dependency-overrides.md#полный-файл-тестов) |
| Проверить обработчик без проверки заголовка | Задать `app.dependency_overrides` | [Карточка подмены](#подмена-зависимости) |
| Проверить API из `async def` | Использовать `ASGITransport` | [Асинхронный клиент](#асинхронный-клиент) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; async-клиент и изоляция БД — продвинутый |
| Предпосылки | pytest, HTTP, контекстные менеджеры; для async — `async`/`await` |


## Навигация

- [Синхронный TestClient](#синхронный-testclient)
- [Подмена зависимости](#подмена-зависимости)
- [Асинхронный клиент](#асинхронный-клиент)
- [Файлы и middleware](#файлы-и-middleware)
- [Сессии БД и lifespan](#сессии-бд-и-lifespan)
- [Аутентификация](#аутентификация)

<a id="среда-примеров"></a>


## Зависимости по задаче

Для подмены используйте [самостоятельный пример с отдельной установкой](dependency-overrides.md#минимальный-самостоятельный-пример).
Для остальных тестов создайте учебное окружение на Python 3.14.
Установите общие пакеты: `python -m pip install 'fastapi==0.162.0' 'starlette==1.10.0' 'pytest==9.2.0' 'httpx2==2.16.0'`.
Затем добавьте только зависимости выбранного приложения:

| Тестируемое приложение | Дополнительная установка |
| --- | --- |
| [main.py: CRUD и валидация](http-api.md) | `python -m pip install 'pydantic[email]==2.14.3' 'email-validator==2.3.0'` |
| [uploads.py: multipart](uploads.md) | `python -m pip install 'python-multipart==0.0.33'` |
| [middleware_app.py: CORS](middleware.md) | Дополнительные пакеты не нужны |
| [db_app.py: sync-БД](database.md#синхронный-sqlalchemy) | `python -m pip install 'sqlalchemy==2.1.8' 'pydantic[email]==2.14.3' 'email-validator==2.3.0'` |
| [async_db_app.py: async-БД](database.md#async-sqlalchemy-и-lifespan) | `python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'aiosqlite==0.22.1'` |
| [auth_app.py: пароль и JWT](authentication.md) | `python -m pip install 'python-multipart==0.0.33' 'PyJWT==2.15.1' 'pwdlib[argon2]==0.3.1'` |


## Подготовка

Сохраните выбранное приложение и соответствующий [полный тестовый модуль](testing-lab.md) рядом в учебной папке.
Для файла `test_integrations.py` нужны оба приложения: `uploads.py` и `middleware_app.py`.
Для файла `test_database.py` нужны оба варианта БД и их зависимости.
Для async-теста добавьте `pytest-asyncio==1.4.1.post1`.
Отдельная команда установки инструментов async-теста:

```bash
python -m pip install pytest pytest-asyncio httpx2
```

В окружении Starlette 1.10.0 используйте `httpx2`.
Прежний `httpx` ещё поддерживается, но его использование в TestClient устаревает.
В старых окружениях пример async-клиента можно адаптировать импортом из `httpx`, сохраняя `ASGITransport`.
Не используйте прямой `AsyncClient(app=app)`.
Этот аргумент удалён из HTTPX в 0.28.0.

Из учебной папки запустите `python -m pytest -q ИМЯ_ТЕСТОВОГО_ФАЙЛА.py`.
Для async-тестов добавьте `-o asyncio_default_fixture_loop_scope=function`, чтобы явно задать область event loop.
Тесты выполняют запросы внутри процесса.
Сервер Uvicorn и внешняя сеть не нужны.


## Синхронный TestClient

**Ситуация:** POST `/items` должен создать Book с ценой `25`, а отрицательная цена должна дать отказ.
**Изменение:** проверьте код ответа и содержимое на настоящем обработчике.
Фрагмент теста для [полного `main.py`](http-api.md#http-api-с-валидацией):

```python
from fastapi.testclient import TestClient
from main import app, items

items.clear()
try:
    with TestClient(app) as client:
        created = client.post("/items", json={"name": "Book", "price": 25})
        assert created.status_code == 201
        assert created.json()["name"] == "Book"
        assert client.post("/items", json={"name": "Book", "price": -1}).status_code == 422
finally:
    items.clear()
```

**Результат:** валидный товар создаётся, неверный ввод отвергается.
Контекст `TestClient` запускает lifespan; словарь очищается даже при провале проверки.
Фрагмент рассчитан на отдельный тестовый процесс без параллельного изменения общего словаря.
[Полный модуль CRUD, PATCH, ошибок и выходной модели](testing-lab.md#синхронный-testclient).


## Подмена зависимости

**Ситуация:** нужно проверить ответ обработчика без вызова реальной зависимости.
В учебном примере `/checked` возвращает JSON, а функция `verify_client` проверяет заголовок `X-Client`.
Если нужно проверить сам заголовок, оставьте исходную зависимость.
Для первого запуска используйте [один файл с приложением, установкой и двумя тестами](dependency-overrides.md#минимальный-самостоятельный-пример).

**Изменение:** запишите соответствие «исходная функция → подмена» в `app.dependency_overrides`.
`Depends(verify_client)` связывает маршрут с исходной функцией.
Ключ словаря — этот объект функции; значение — функция подмены, без вызова и скобок.

**Пример — фрагмент теста для [полного `header_dependency.py`](recipes.md#проверка-заголовка-перед-обработчиком):**

```python
from fastapi.testclient import TestClient

from header_dependency import app, verify_client


def skip_client_check():
    return None


def test_override():
    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = skip_client_check
        with TestClient(app) as client:
            response = client.get("/checked")
            assert response.status_code == 200
            assert response.json() == {"checked": True}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

**Результат:** запрос без заголовка получает `200` и `{"checked": true}` вместо исходного `422`.
`finally` выполняется и при исключении; здесь блок возвращает весь прежний словарь подмен.

**Ограничения:** подмена принадлежит приложению, а не клиенту или одному запросу.
Выход из `TestClient` не очищает словарь.
Не изменяйте подмены одновременно для общего `app` внутри одного процесса.
`None` подходит для проверки в декораторе; зависимость, передающая данные обработчику, требует подходящего значения.

Для выбора функции прочитайте [пояснения о ключе словаря, возвращаемом значении и подзависимостях](dependency-overrides.md#выбрать-функцию-для-подмены).
Для проверки очистки выполните [тесты восстановления после ошибки теста и зависимости](dependency-overrides.md#полный-файл-тестов).
Источник: [FastAPI — подмена зависимостей](https://fastapi.tiangolo.com/advanced/testing-dependencies/).


## Асинхронный клиент

**Ситуация:** тест уже выполняется в `async def`; запрос нужен без отдельного сервера.
**Изменение:** используйте `ASGITransport` вместо удалённого аргумента `AsyncClient(app=...)`.
Фрагмент async-теста для [полного `main.py`](http-api.md):

```python
import pytest
from httpx2 import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.json() == {"message": "Каталог работает"}
```

**Результат:** запрос выполняется в процессе теста.
`ASGITransport` сам не запускает lifespan; для startup-ресурсов нужен отдельный LifespanManager.
[Полный async-тест и границы очистки](testing-lab.md#асинхронный-клиент).


## Файлы и middleware

**Ситуация:** `/upload` должен измерить синтетический файл, не читая пользовательские файлы с диска.
**Изменение:** передайте имя, байты и media type через `files`.
Фрагмент теста для [полного `uploads.py`](uploads.md):

```python
from fastapi.testclient import TestClient
from uploads import app

with TestClient(app) as client:
    response = client.post("/upload", files={"file": ("demo.txt", b"abc", "text/plain")})
    assert response.status_code == 200
    assert response.json() == {"filename": "demo.txt", "size": 3}
```

**Результат:** обработчик возвращает размер `3`.
Этот запрос не проверяет общий лимит HTTP-тела на прокси.
[Полные проверки нескольких файлов, 413, CORS и preflight](testing-lab.md#файлы-и-middleware).


## Сессии БД и lifespan

**Ситуация:** повторный email должен дать `409`, а тест не должен менять учебную БД приложения.
**Изменение:** до `TestClient` замените движок и фабрику на SQLite из `tmp_path`.
Фрагмент теста с фикстурами `tmp_path` и `monkeypatch` для [полного `db_app.py`](database.md#синхронный-sqlalchemy):

```python
import db_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(f"sqlite:///{tmp_path / 'users.db'}", connect_args={"check_same_thread": False})
monkeypatch.setattr(db_app, "engine", engine)
monkeypatch.setattr(db_app, "SessionLocal", sessionmaker(engine))
```

**Результат:** lifespan создаёт схему в отдельном файле; зависимость получает сессии из тестовой фабрики.
Сохраните подмену до выхода из контекста клиента, чтобы lifespan закрыл тестовый движок.
Фрагмент подготавливает ресурс; сам HTTP-отказ проверяет [полный sync/async-модуль](testing-lab.md#сессии-бд-и-lifespan).


## Аутентификация

**Ситуация:** маршрут `/users/me` должен отвергать запрос без bearer-токена.
**Изменение:** оставьте реальную зависимость аутентификации и проверьте HTTP-контракт.
Фрагмент для [полного `auth_app.py`](authentication.md#полный-пример) после [подготовки учебного ключа](authentication.md#подготовка):

```python
from fastapi.testclient import TestClient
from auth_app import app

with TestClient(app) as client:
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
```

**Результат:** клиент получает `401` и запрос bearer-аутентификации.
Подмена `current_user` скрыла бы эту проверку.
[Полный модуль с паролями, подписями, сроком и заблокированным пользователем](testing-lab.md#аутентификация).


## Источники

- [FastAPI: TestClient](https://fastapi.tiangolo.com/tutorial/testing/), [dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [Starlette: текущие зависимости TestClient и async-клиент](https://starlette.dev/testclient/).
- [FastAPI: async-тесты и lifespan](https://fastapi.tiangolo.com/advanced/async-tests/).
- [HTTPX 0.28.0: удаление app](https://github.com/encode/httpx/releases/tag/0.28.0).
- [pytest-asyncio: маркер asyncio](https://pytest-asyncio.readthedocs.io/en/stable/reference/markers/index.html).
