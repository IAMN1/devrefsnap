# HTTP API, параметры и файлы

[Краткий справочник](README.md) · [Тестирование этих примеров](testing.md)

| Проверка | Статус |
| --- | --- |
| Сверено с документацией | 2026-11-06, FastAPI 0.162.0 и Pydantic v2 |
| Выполнено | 2026-11-06: CRUD, валидация, фильтрация ответа, зависимости, формы/файлы и CORS проверены через TestClient. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0, python-multipart 0.0.33 |

- [HTTP API с валидацией](#http-api-с-валидацией)
- [Как устроены зависимости](#как-устроены-зависимости)
- [Формы и загрузка файлов](#формы-и-загрузка-файлов)
- [Middleware и CORS](#middleware-и-cors)

## HTTP API с валидацией

**Уровень:** базовый → средний.
**Задача:** создать небольшой CRUD с разделением path/query/body, проверкой полей и управляемыми ответами.
**Предпосылки:** функции, типы, HTTP-методы.

В отдельной папке установите `fastapi==0.162.0`, `uvicorn[standard]` и `pydantic[email]`.
Создайте полный файл `main.py`:

<!-- example: main.py -->
```python
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator, model_validator

app = FastAPI(title="Каталог товаров", version="1.0.0")


def validation_details(exc: RequestValidationError | ValidationError):
    return [{key: error[key] for key in ("loc", "msg", "type")} for error in exc.errors()]


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": validation_details(exc)})


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price: float = Field(gt=0, allow_inf_nan=False)
    tax: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Название не должно быть пустым")
        return value

    @model_validator(mode="after")
    def premium_price(self) -> "ItemCreate":
        if self.name == "premium" and self.price < 100:
            raise ValueError("Цена premium должна быть не меньше 100")
        return self


class ItemOut(ItemCreate):
    id: int


class ItemPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    price: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    tax: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    tags: list[str] | None = None


class Pagination:
    def __init__(
        self,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
    ):
        self.offset = offset
        self.limit = limit


def search_query(q: Annotated[str | None, Query(max_length=100)] = None):
    return q


def effective_query(
    q: Annotated[str | None, Depends(search_query)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    return q if q is not None else last_query


items: dict[int, ItemOut] = {}


def existing_item(item_id: Annotated[int, Path(gt=0)]) -> ItemOut:
    if item_id not in items:
        raise HTTPException(404, "Товар не найден", headers={"X-Error": "item-missing"})
    return items[item_id]


@app.get("/")
async def root():
    return {"message": "Каталог работает"}


@app.post("/items", response_model=ItemOut, status_code=201)
async def create_item(item: ItemCreate):
    item_id = max(items, default=0) + 1
    saved = ItemOut(id=item_id, **item.model_dump())
    items[item_id] = saved
    return saved


@app.get("/items", response_model=list[ItemOut])
async def list_items(
    page: Annotated[Pagination, Depends()],
    query: Annotated[str | None, Depends(effective_query)],
    tags: Annotated[list[str] | None, Query()] = None,
):
    result = [item for item in items.values()
              if (query is None or query in item.name)
              and (not tags or set(tags).issubset(item.tags))]
    return result[page.offset:page.offset + page.limit]


@app.get("/items/{item_id}", response_model=ItemOut)
async def read_item(item: Annotated[ItemOut, Depends(existing_item)]):
    return item


@app.put("/items/{item_id}", response_model=ItemOut)
async def replace_item(item_id: int, item: ItemCreate):
    existing_item(item_id)
    items[item_id] = ItemOut(id=item_id, **item.model_dump())
    return items[item_id]


@app.patch("/items/{item_id}", response_model=ItemOut)
async def patch_item(item_id: int, patch: ItemPatch):
    current = existing_item(item_id)
    data = {**current.model_dump(exclude={"id"}), **patch.model_dump(exclude_unset=True)}
    try:
        validated = ItemCreate.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(422, validation_details(exc)) from exc
    items[item_id] = ItemOut(id=item_id, **validated.model_dump())
    return items[item_id]


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    existing_item(item_id)
    del items[item_id]
    return Response(status_code=204)


@app.get("/users/{user_id}/items/{item_id}")
async def nested_path(user_id: int, item_id: int, short: bool = False):
    return {"user_id": user_id, "item_id": item_id, "short": short}


class UserOut(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserIn(UserOut):
    password: str = Field(min_length=8)


@app.post("/user-preview", response_model=UserOut)
async def preview_user(user: UserIn):
    return user


class StockError(Exception):
    pass


@app.exception_handler(StockError)
async def stock_error_handler(request: Request, exc: StockError):
    return JSONResponse(status_code=409, content={"detail": "Недостаточно товара"})


@app.get("/stock/{quantity}")
async def check_stock(quantity: Annotated[int, Path(gt=0)]):
    if quantity > 5:
        raise StockError()
    return {"available": True}


@app.get("/custom")
async def custom_response():
    return JSONResponse({"message": "Особый ответ"}, headers={"X-Custom": "demo"})


@app.get("/html", response_class=HTMLResponse)
async def html():
    return "<h1>Каталог товаров</h1>"


@app.get("/redirect")
async def redirect():
    return RedirectResponse("/docs", status_code=307)
```

Запуск и запросы в другом терминале:

```bash
uvicorn main:app --reload
```

```bash
curl -i -X POST http://127.0.0.1:8000/items -H 'Content-Type: application/json' -d '{"name":"Book","price":25,"tags":["python"]}'
curl 'http://127.0.0.1:8000/items?q=Book&tags=python&limit=5'
curl -i -X PATCH http://127.0.0.1:8000/items/1 -H 'Content-Type: application/json' -d '{"price":30}'
curl -i http://127.0.0.1:8000/items/999
```

Результат создания — `201` с `id=1`.
Выборка возвращает список из одного товара.
PATCH меняет цену на `30`.
Запрос отсутствующего товара даёт `404`.
Отрицательная цена и `premium` дешевле `100` дают `422`.
`DELETE` возвращает `204` без тела.
Маршрут `/user-preview` демонстрирует фильтрацию пароля выходной моделью.
Маршрут не сохраняет пользователя и не является регистрацией.

Ограничения: данные живут до перезапуска в одном процессе.
Это хранилище не обеспечивает постоянство данных и конкурентный доступ.
Здесь `float` выбран для простоты.
Для точных денежных расчётов нужна отдельно выбранная модель чисел.
PATCH сначала объединяет поля.
Затем PATCH повторно проверяет всю модель.
Сам по себе `model_copy(update=...)` не выполняет такую валидацию.
Явный `null` допускается только у полей итоговой модели, допускающих `None`.

Цена и налог должны быть конечными числами.
`allow_inf_nan=False` отклоняет бесконечность и NaN.
Число `1e999` может стать `inf` уже при разборе JSON.
Поэтому обработчик ошибки возвращает только `loc`, `msg`, `type`.
Обработчик исключает исходный `input` и `ctx`.
Эти значения сами могут не сериализоваться в JSON.
Тот же формат используется при повторной валидации PATCH.

Источники: [ограничения параметров](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [Pydantic v2 validators](https://docs.pydantic.dev/latest/concepts/validators/), [ограничения Field](https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field), [обновление body](https://fastapi.tiangolo.com/tutorial/body-updates/), [выходная модель](https://fastapi.tiangolo.com/tutorial/response-model/), [обработка ошибок](https://fastapi.tiangolo.com/tutorial/handling-errors/).

## Как устроены зависимости

**Уровень:** средний. В `main.py` выше:

- `search_query` — функция-зависимость. `effective_query` — зависимость с подзависимостью и настоящим `Cookie`.
- `Pagination` — класс-зависимость: FastAPI читает параметры его конструктора.
- `existing_item` — единое место поиска и `404`. Обработчик чтения получает уже найденный объект.

Если результат проверки не нужен обработчику, вынесите проверку в `dependencies`.
Ниже приведён самостоятельный файл `header_dependency.py`.
Зависимости те же, что для `minimal.py`.

<!-- example: header_dependency.py -->
```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


def verify_client(x_client: Annotated[str, Header()]):
    if x_client != "training-client":
        raise HTTPException(400, "Неизвестный клиент")


@app.get("/checked", dependencies=[Depends(verify_client)])
def checked():
    return {"checked": True}
```

Запустите `uvicorn header_dependency:app --reload`.
Запрос `curl -H 'X-Client: training-client' http://127.0.0.1:8000/checked` вернёт `200`.
Неверное значение заголовка даёт `400`.
Отсутствующий обязательный заголовок даёт `422`.
Пример демонстрирует валидацию заголовка.
Этот заголовок не является секретным API-ключом или заменой [аутентификации](authentication.md).

Источники: [Depends](https://fastapi.tiangolo.com/tutorial/dependencies/), [подзависимости](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/), [проверка на уровне декоратора](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).

## Формы и загрузка файлов

**Уровень:** средний.
**Задача:** принять форму, один файл или список файлов.
Установите дополнительно `python-multipart`.
Сохраните самостоятельный пример в файле `uploads.py`:

<!-- example: uploads.py -->
```python
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

app = FastAPI()
MAX_BYTES = 1024 * 1024


@app.post("/form")
async def read_form(username: Annotated[str, Form(min_length=1)]):
    return {"username": username}


async def measure(file: UploadFile):
    size = 0
    try:
        while chunk := await file.read(64 * 1024):
            size += len(chunk)
            if size > MAX_BYTES:
                raise HTTPException(413, "Файл больше 1 MiB")
        return {"filename": file.filename, "size": size}
    finally:
        await file.close()


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    return await measure(file)


@app.post("/uploads")
async def uploads(files: Annotated[list[UploadFile], File()]):
    return [await measure(file) for file in files]
```

```bash
uvicorn uploads:app --reload
```

Для проверки загрузите существующий учебный файл.
`@` в curl означает чтение локального файла:

```bash
curl -F 'username=alice' http://127.0.0.1:8000/form
curl -F 'file=@uploads.py' http://127.0.0.1:8000/upload
curl -F 'files=@uploads.py' -F 'files=@uploads.py' http://127.0.0.1:8000/uploads
```

Первый результат содержит имя из формы.
Второй результат содержит имя и размер файла.
Третий результат содержит список из двух результатов.
Ограничение в обработчике проверяет прочитанное содержимое одного файла.
Это ограничение не проверяет полный размер HTTP-запроса до multipart-парсинга.
Задайте общий лимит тела также на сервере или прокси.
Задайте лимит числа файлов также на сервере или прокси.
Имя и MIME-тип присылает клиент.
Пример не сохраняет файлы.
Пример не проверяет фактический формат файлов.
JSON body и multipart body — разные форматы одного запроса.

Источники: [файлы](https://fastapi.tiangolo.com/tutorial/request-files/), [формы и файлы](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/).

## Middleware и CORS

**Уровень:** средний.
**Задача:** добавить время обработки и разрешить браузерные запросы с конкретного origin.
Сохраните самостоятельный пример в файле `middleware_app.py`.
Базовые зависимости те же, что для `minimal.py`.

<!-- example: middleware_app.py -->
```python
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Process-Time"],
)


@app.middleware("http")
async def timing(request: Request, call_next):
    start = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{perf_counter() - start:.6f}"
    return response


@app.get("/")
async def root():
    return {"ok": True}
```

Запустите `uvicorn middleware_app:app --reload`.
`curl -i -H 'Origin: http://localhost:3000' http://127.0.0.1:8000/` покажет `Access-Control-Allow-Origin` и `X-Process-Time`.
Для проверки preflight отправьте `OPTIONS` с заголовками `Origin` и `Access-Control-Request-Method: GET`.
Этот сценарий проверяет [автоматический тест](testing.md#файлы-и-middleware).

Origin включает схему, хост и порт.
`127.0.0.1` отличается от `localhost`.
При credentials перечисляйте допустимые origins явно.
CORS регулирует доступ браузера к ответу.
CORS не аутентифицирует запросы.
Таймер измеряет путь до получения объекта ответа.
Таймер не измеряет полную отправку потокового тела.
Необработанное исключение может пройти другим путём обработки ошибок.

Источники: [middleware](https://fastapi.tiangolo.com/tutorial/middleware/), [CORS](https://fastapi.tiangolo.com/tutorial/cors/).
