# FastAPI

FastAPI строит HTTP API из аннотаций Python и моделей Pydantic. Здесь — краткий справочник и самостоятельные рецепты для запросов, БД, тестирования, аутентификации и запуска.

[Каталог Python](../../README.md)

| Параметр | Значение |
| --- | --- |
| Целевой API | FastAPI 0.162.0, Pydantic v2; синтаксис примеров Python 3.10+ |
| Предпосылки | Функции, аннотации типов, HTTP/JSON; для продвинутых задач — `async` и контекстные менеджеры |
| Сверено с документацией | 2026-11-06: FastAPI, release notes 0.162.0 от 2026-10-23, Pydantic v2, SQLAlchemy 2.0 |
| Выполнено | 2026-11-06: 14 Python-блоков скомпилированы; 45 тестов прошли, включая CRUD, ввод, файлы, JWT и SQLite. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3; [остальные версии](testing.md#проверенное-окружение) |

## Навигация

- [Быстрый поиск](#быстрый-поиск)
- [Базовый уровень](#базовый-уровень)
- [Средний уровень](#средний-уровень)
- [Продвинутый уровень](#продвинутый-уровень)
- [Частые ошибки](#частые-ошибки)
- [Источники](#источники)

## Быстрый поиск

| Задача | API / команда | Подробности |
| --- | --- | --- |
| Поднять API | `uvicorn minimal:app --reload` | [Первый запуск](#первый-запуск) |
| CRUD, path/query/body, валидация | `Path`, `Query`, `BaseModel`, `Field` | [HTTP-рецепт](recipes.md#http-api-с-валидацией) |
| Ответы, ошибки, выходная модель | `response_model`, `HTTPException`, `JSONResponse` | [HTTP-рецепт](recipes.md#http-api-с-валидацией) |
| Функция, класс, подзависимость | `Annotated[T, Depends(...)]` | [Зависимости](recipes.md#как-устроены-зависимости) |
| Форма, один или несколько файлов | `Form`, `UploadFile`, `File` | [Загрузка файлов](recipes.md#формы-и-загрузка-файлов) |
| Время запроса и CORS | `@app.middleware`, `CORSMiddleware` | [Middleware](recipes.md#middleware-и-cors) |
| Сессия на запрос, startup/shutdown | `yield`, `lifespan`, SQLAlchemy | [База данных](database.md) |
| Проверить API синхронно/асинхронно | `TestClient`, `ASGITransport` | [Тестирование](testing.md) |
| Проверить пароль и JWT | `pwdlib`, `PyJWT`, `OAuth2PasswordBearer` | [Аутентификация](authentication.md) |
| Workers, контейнер, OpenAPI | Uvicorn, Docker, `app.openapi()` | [Запуск и деплой](deployment.md) |

## Базовый уровень

### Первый запуск

В отдельной учебной папке создай виртуальное окружение и установи зависимости. Это установка для рецепта, а не изменение зависимостей репозитория.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]'
```

Полный пример: файл `minimal.py` в этой папке.

<!-- example: minimal.py -->
```python
from fastapi import FastAPI

app = FastAPI(title="Учебный API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Привет"}
```

```bash
uvicorn minimal:app --reload
curl http://127.0.0.1:8000/
```

Результат: `200` и `{"message":"Привет"}`. Swagger UI доступен на [localhost:8000/docs](http://localhost:8000/docs), ReDoc — на [localhost:8000/redoc](http://localhost:8000/redoc), схема — на [localhost:8000/openapi.json](http://localhost:8000/openapi.json). `version` здесь — версия твоего API.

### Откуда берётся параметр

| Объявление | Источник |
| --- | --- |
| `item_id: int` при пути `/items/{item_id}` | Сегмент URL |
| `q: str \| None = None` | Необязательный query-параметр |
| `tags: Annotated[list[str] \| None, Query()] = None` | Повторяющийся query: `?tags=a&tags=b` |
| `item: ItemCreate` | JSON body с проверкой Pydantic |
| `x_token: Annotated[str, Header()]` | Заголовок `X-Token` |
| `last_query: Annotated[str \| None, Cookie()] = None` | Cookie `last_query` |

Это сигнатуры-фрагменты; полные импорты и обработчики находятся в [рецептах](recipes.md). Для списка query-параметров указывай `Query` явно. `str | None` разрешает `null`/`None`, а значение по умолчанию определяет обязательность.

### Методы и модели

`GET` читает; `POST` создаёт; `PUT` полностью заменяет; `PATCH` меняет переданные поля; `DELETE` удаляет. Семантику реализует обработчик — декоратор её не обеспечивает.

Для входа используй `BaseModel`, ограничения — `Field`, пользовательские правила — `field_validator`/`model_validator`. Для выхода объявляй отдельную модель без пароля и указывай `response_model`. [Согласованный CRUD и модели](recipes.md#http-api-с-валидацией).

## Средний уровень

| Задача | Что помнить |
| --- | --- |
| Переиспользовать параметры | `Depends` вызывает функцию/класс; подзависимости формируют дерево |
| Выполнить проверку без возвращаемого значения | `dependencies=[Depends(check)]` на маршруте |
| Вернуть управляемую ошибку | `raise HTTPException(status_code=404, detail="...")` |
| Изменить код успешного ответа | `status_code=201` у декоратора |
| Вернуть HTML/redirect/особые заголовки | Специализированный `Response`; его тело уже не проходит обычную фильтрацию `response_model` |
| Принять файл | `UploadFile`; читай порциями, если не нужен весь файл в памяти |
| Проверить маршрут | В тесте проверяй полезный результат, неверный ввод и отсутствующий объект |

Для собственного обработчика исключений, форм и middleware см. [рецепты](recipes.md). Для изменения результата зависимости в тестах — [dependency overrides](testing.md#подмена-зависимости).

## Продвинутый уровень

- **Жизненный цикл и БД:** создавай/закрывай общие ресурсы в `lifespan`, сессию выдавай на запрос через `yield`. Синхронный SQLAlchemy используй в `def`-обработчиках; `async def` требует неблокирующего клиента. [Синхронный и async варианты](database.md).
- **Аутентификация:** извлечение bearer-строки ещё не проверяет пользователя. Проверяй пароль до выдачи токена, подпись/алгоритм/срок действия и пользователя при чтении токена. [Полный учебный рецепт](authentication.md).
- **Эксплуатация:** `--reload` нужен для разработки; число workers подбирай по нагрузке. Память процесса не является общей БД. [Workers и контейнер](deployment.md).
- **Миграция старых примеров:** Pydantic v1 `dict()` → `model_dump()`, `validator` → `field_validator`, `root_validator` → `model_validator`; события `on_event` → `lifespan`; HTTPX `AsyncClient(app=...)` → `ASGITransport(app=...)`. Это требует проверки поведения, а не только переименования.

## Частые ошибки

| Симптом | Причина | Исправление |
| --- | --- | --- |
| `422 Unprocessable Entity` | Ввод не соответствует схеме | Прочитай `detail`, проверь источник параметра и обязательные поля |
| Ответ содержит лишнее поле | Нет подходящей выходной модели либо возвращён готовый `Response` | Укажи `response_model`, проверь тестом отсутствие поля |
| Сервер зависает на I/O | Блокирующий вызов внутри `async def` | Возьми async-драйвер либо синхронный `def`-обработчик |
| Startup не вызван в тесте | Клиент не запустил lifespan | `with TestClient(app)` либо `LifespanManager` для async-клиента |
| Данные пропали после перезапуска | Учебное хранилище находится в памяти | Перейди к [БД](database.md) |
| CORS мешает браузеру | Не совпадают scheme/host/port разрешённого origin | Настрой точный origin и проверь preflight |

## Источники

- [FastAPI: release notes 0.162.0](https://fastapi.tiangolo.com/release-notes/#01620-2026-10-23).
- [Параметры query](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [модели ответа](https://fastapi.tiangolo.com/tutorial/response-model/).
- [Когда использовать async/def](https://fastapi.tiangolo.com/async/), [lifespan](https://fastapi.tiangolo.com/advanced/events/).
- [Миграция Pydantic v2](https://docs.pydantic.dev/latest/migration/).
- [FastAPI: async-тесты](https://fastapi.tiangolo.com/advanced/async-tests/).
