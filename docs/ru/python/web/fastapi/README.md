
# FastAPI

[English](../../../../en/python/web/fastapi/README.md)

FastAPI строит HTTP API из аннотаций Python и моделей Pydantic.
Используйте справочник для запросов, БД, тестирования, аутентификации и запуска.
Подробные примеры находятся в самостоятельных рецептах.

[Каталог Python](../../README.md)


## Быстрый поиск

| Задача | API / команда | Подробности |
| --- | --- | --- |
| Поднять API | `uvicorn minimal:app --reload` | [Первый запуск](#первый-запуск) |
| CRUD, path/query/body, валидация | `Path`, `Query`, `BaseModel`, `Field` | [Полный CRUD](http-api.md#http-api-с-валидацией) |
| Ответы, ошибки, выходная модель | `response_model`, `HTTPException`, `JSONResponse` | [Модели и ответы](http-api.md#http-api-с-валидацией) |
| Посмотреть HTTP-ответ из терминала | `curl -i`, `jq` | [HTTP и JSON](../../../tools/http-json.md) |
| Функция, класс, подзависимость | `Annotated[T, Depends(...)]` | [Зависимости](recipes.md#как-устроены-зависимости) |
| Форма, один или несколько файлов | `Form`, `UploadFile`, `File` | [Полное приложение](uploads.md#формы-и-загрузка-файлов) |
| Время запроса и CORS | `@app.middleware`, `CORSMiddleware` | [Полное приложение](middleware.md#middleware-и-cors) |
| Сессия на запрос, startup/shutdown | `yield`, `lifespan`, SQLAlchemy | [База данных](database.md) |
| Проверить API синхронно/асинхронно | `TestClient`, `ASGITransport` | [Тестирование](testing.md) |
| Проверить обработчик без вызова реальной зависимости | `app.dependency_overrides` | [Карточка выбора](testing.md#подмена-зависимости) · [Самостоятельная программа](dependency-overrides.md#минимальный-самостоятельный-пример) |
| Восстановить зависимости после теста или ошибки | `try` / `finally` | [Полные проверки восстановления](dependency-overrides.md#полный-файл-тестов) |
| Проверить пароль и JWT | `pwdlib`, `PyJWT`, `OAuth2PasswordBearer` | [Аутентификация](authentication.md) |
| Workers, контейнер, OpenAPI | Uvicorn, Docker, `app.openapi()` | [Запуск и деплой](deployment.md) |

| Параметр | Значение |
| --- | --- |
| Целевой API | FastAPI 0.162.0, Pydantic v2; синтаксис примеров Python 3.10+ |
| Предпосылки | Функции, аннотации типов, HTTP/JSON; для продвинутых задач — `async` и контекстные менеджеры |

<a id="навигация"></a>

<a id="базовый-уровень"></a>


## Первый запуск

Для воспроизведения используйте Python 3.14, FastAPI 0.162.0 и Uvicorn 0.54.0.

Создайте виртуальное окружение в отдельной учебной папке.
Установите зависимости в учебное окружение.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]'
```

Полный пример: файл `minimal.py` в этой папке.

[`minimal.py`](../../../../../examples/python/web/fastapi/minimal.py)

```bash
uvicorn minimal:app --reload
curl http://127.0.0.1:8000/
```

Результат: `200` и `{"message":"Привет"}`.
Swagger UI доступен на [localhost:8000/docs](http://localhost:8000/docs).
ReDoc доступен на [localhost:8000/redoc](http://localhost:8000/redoc).
Схема доступна на [localhost:8000/openapi.json](http://localhost:8000/openapi.json).
`version` здесь обозначает версию вашего API.

Вызовите этот же маршрут из [HTTP-клиента на TypeScript](../../../typescript/README.md), чтобы проверить поля ответа в коде.
Для запуска с PostgreSQL и проверки ответов в CI используйте [сквозной пример](../../../tools/api-contract-lab.md).


## Откуда берётся параметр

| Объявление | Источник |
| --- | --- |
| `item_id: int` при пути `/items/{item_id}` | Сегмент URL |
| `q: str \| None = None` | Необязательный query-параметр |
| `tags: Annotated[list[str] \| None, Query()] = None` | Повторяющийся query: `?tags=a&tags=b` |
| `item: ItemCreate` | JSON body с проверкой Pydantic |
| `x_token: Annotated[str, Header()]` | Заголовок `X-Token` |
| `last_query: Annotated[str \| None, Cookie()] = None` | Cookie `last_query` |

Это фрагменты сигнатур.
Полные импорты и обработчики находятся в [рецептах](recipes.md).
Для списка query-параметров указывайте `Query` явно.
`str | None` разрешает `null`/`None`.
Значение по умолчанию определяет обязательность параметра.


## Методы и модели

`GET` читает данные.
`POST` создаёт данные.
`PUT` полностью заменяет данные.
`PATCH` меняет переданные поля.
`DELETE` удаляет данные.
Семантику реализует обработчик.
Декоратор не обеспечивает эту семантику.

Для входных данных используйте `BaseModel`.
Задавайте ограничения через `Field`.
Задавайте пользовательские правила через `field_validator`/`model_validator`.
Для выхода объявляйте отдельную модель без пароля.
Указывайте выходную модель в `response_model`.
[Согласованный CRUD и модели](recipes.md#http-api-с-валидацией).

<a id="средний-уровень"></a>


## Отдать публичную модель без пароля

**Ситуация:** вход `/user-preview` принимает пароль, но HTTP-ответ не должен содержать пароль.
**Изменение:** задайте отдельную модель `UserOut` через `response_model`.
Фрагмент [полного HTTP-приложения](recipes.md#http-api-с-валидацией), где обе модели уже определены:

```python
@app.post("/user-preview", response_model=UserOut)
async def preview_user(user: UserIn):
    return user
```

**Результат:** запрос с `username`, `email`, `password` возвращает публичные поля без `password`.
Готовый `Response` обходит обычную фильтрацию модели ответа.
[Полное приложение](recipes.md#http-api-с-валидацией) · [Проверка отсутствия пароля](testing.md#синхронный-testclient).


| Задача | Что помнить |
| --- | --- |
| Переиспользовать параметры | `Depends` вызывает функцию/класс. Подзависимости формируют дерево |
| Выполнить проверку без возвращаемого значения | `dependencies=[Depends(check)]` на маршруте |
| Вернуть управляемую ошибку | `raise HTTPException(status_code=404, detail="...")` |
| Изменить код успешного ответа | `status_code=201` у декоратора |
| Вернуть HTML/redirect/особые заголовки | Используйте специализированный `Response`. Тело такого ответа не проходит обычную фильтрацию `response_model` |
| Принять файл | Если весь файл не нужен в памяти, читайте `UploadFile` порциями |
| Проверить маршрут | Проверьте полезный результат. Проверьте неверный ввод. Проверьте отсутствующий объект |

Используйте [рецепты](recipes.md) для собственного обработчика исключений, форм и middleware.
Для изменения результата зависимости в тестах используйте [dependency overrides](testing.md#подмена-зависимости).

<a id="продвинутый-уровень"></a>


## Закрывать сессию после запроса

**Ситуация:** каждый синхронный обработчик должен получить свою SQLAlchemy Session.
**Изменение:** выдавайте сессию из зависимости с `yield`.
Фрагмент [полного `db_app.py`](database.md#синхронный-sqlalchemy), где `SessionLocal` — фабрика сессий:

```python
def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
```

**Результат:** выход из зависимости закрывает сессию; обработчик получает сессию через `Depends(get_session)`.
Контекст Session сам не делает commit.
В полном примере обработчик явно фиксирует или откатывает транзакцию.
[Sync/async-приложения](database.md) · [Проверки БД и lifespan](testing.md#сессии-бд-и-lifespan).


- **Жизненный цикл и БД:** создавайте общие ресурсы в `lifespan`. Закрывайте общие ресурсы в `lifespan`. Выдавайте сессию на запрос через `yield`. Используйте синхронный SQLAlchemy в `def`-обработчиках. `async def` требует неблокирующего клиента. [Синхронный и async варианты](database.md).
- **Аутентификация:** извлечение bearer-строки ещё не проверяет пользователя. До выдачи токена проверяйте пароль. При чтении токена проверяйте подпись, алгоритм, срок действия и пользователя. [Полный учебный рецепт](authentication.md).
- **Эксплуатация:** `--reload` нужен для разработки. Подбирайте число workers по нагрузке. Память процесса не является общей БД. [Workers и контейнер](deployment.md).
- **Миграция старых примеров:** Pydantic v1: `dict()` → `model_dump()`, `validator` → `field_validator`, `root_validator` → `model_validator`. События: `on_event` → `lifespan`. HTTPX: `AsyncClient(app=...)` → `ASGITransport(app=...)`. После миграции проверьте поведение. Одного переименования недостаточно.


## Частые ошибки

| Симптом | Причина | Исправление |
| --- | --- | --- |
| `422 Unprocessable Entity` | Ввод не соответствует схеме | Прочитайте `detail`. Проверьте источник параметра. Проверьте обязательные поля |
| Ответ содержит лишнее поле | Нет подходящей выходной модели либо возвращён готовый `Response` | Укажите `response_model`. Проверьте тестом отсутствие поля |
| Сервер зависает на I/O | Блокирующий вызов внутри `async def` | Используйте async-драйвер либо синхронный `def`-обработчик |
| Startup не вызван в тесте | Клиент не запустил lifespan | `with TestClient(app)` либо `LifespanManager` для async-клиента |
| Данные пропали после перезапуска | Учебное хранилище находится в памяти | Перейдите к [БД](database.md) |
| CORS мешает браузеру | Не совпадают scheme/host/port разрешённого origin | Настройте точный origin. Проверьте preflight |


## Источники

- [FastAPI: release notes 0.162.0](https://fastapi.tiangolo.com/release-notes/#01620-2026-10-23).
- [Параметры query](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [модели ответа](https://fastapi.tiangolo.com/tutorial/response-model/).
- [Когда использовать async/def](https://fastapi.tiangolo.com/async/), [lifespan](https://fastapi.tiangolo.com/advanced/events/).
- [Миграция Pydantic v2](https://docs.pydantic.dev/latest/migration/).
- [FastAPI: async-тесты](https://fastapi.tiangolo.com/advanced/async-tests/).
