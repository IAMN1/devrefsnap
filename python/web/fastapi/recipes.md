# HTTP API, параметры и файлы

Откройте страницу, чтобы вспомнить обработку HTTP-ввода, зависимости, multipart и CORS.
Карточки показывают отдельное изменение; полные приложения вынесены по задачам.

| Задача | Приём | Карточка / полный пример |
| --- | --- | --- |
| Частично изменить товар и проверить итог | Объединить поля, затем `model_validate` | [PATCH](#http-api-с-валидацией) · [Полный CRUD](http-api.md) |
| Переиспользовать параметры или поиск объекта | `Depends` и подзависимости | [Зависимости](#как-устроены-зависимости) |
| Проверить заголовок перед обработчиком | `dependencies=[Depends(...)]` | [Один самостоятельный файл](#проверка-заголовка-перед-обработчиком) |
| Принять файл с лимитом прочитанного содержимого | `UploadFile.read` порциями | [Карточка](#формы-и-загрузка-файлов) · [Полное приложение](uploads.md) |
| Разрешить браузерный origin и измерить обработку | CORS и middleware | [Карточка](#middleware-и-cors) · [Полное приложение](middleware.md) |

[Краткий справочник](README.md) · [Тесты](testing.md)

Уровень: базовый → средний.
Предпосылки: функции, аннотации типов и HTTP-методы.
Среда: Python 3.14, FastAPI 0.162.0 и Pydantic 2.14.3.
Установки и полный код находятся на страницах выбранных приложений; каждой задаче нужен только её набор пакетов.

## HTTP API с валидацией

**Ситуация:** у товара Book цена `25`; PATCH передаёт только новую цену `30`.
Остальные поля нужно сохранить и проверить итоговую модель.
**Изменение:** объедините сохранённые и переданные поля, затем вызовите `model_validate`.
Фрагмент обработчика `patch_item` из [полного `main.py`](http-api.md#http-api-с-валидацией):

```python
current = existing_item(item_id)
data = {**current.model_dump(exclude={"id"}), **patch.model_dump(exclude_unset=True)}
try:
    validated = ItemCreate.model_validate(data)
except ValidationError as exc:
    raise HTTPException(422, validation_details(exc)) from exc
items[item_id] = ItemOut(id=item_id, **validated.model_dump())
```

Здесь `patch` — проверенный `ItemPatch`, а `items` — словарь товаров полного приложения.
**Результат:** цена меняется на `30`, название остаётся `Book`.
Неверный итог даёт `422` до изменения словаря.
Сам `model_copy(update=...)` не проверяет обновления.
Хранилище в памяти не обеспечивает постоянство данных и конкурентный доступ.
[Полный CRUD, модели, ответы и запуск](http-api.md) · [Проверки PATCH](testing-lab.md#синхронный-testclient).

## Как устроены зависимости

**Уровень:** средний. В [полном `main.py`](http-api.md#http-api-с-валидацией):

- `search_query` — функция-зависимость. `effective_query` — зависимость с подзависимостью и настоящим `Cookie`.
- `Pagination` — класс-зависимость: FastAPI читает параметры его конструктора.
- `existing_item` — единое место поиска и `404`. Обработчик чтения получает уже найденный объект.

### Проверка заголовка перед обработчиком

Здесь зависимость — функция, которую FastAPI вызывает через `Depends` перед обработчиком.
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

`Header()` указывает источник параметра: HTTP-заголовок `X-Client`.
`Annotated` связывает тип `str` с настройкой `Header()`.
`Depends(verify_client)` передаёт FastAPI объект функции, а не результат вызова.
FastAPI сначала проверяет обязательный заголовок, затем вызывает `verify_client`.
Если зависимость завершается без ошибки, FastAPI вызывает `checked`.
Декоратор использует проверку, но не передаёт её результат в `checked`.

Запустите `uvicorn header_dependency:app --reload`.
Запрос `curl -H 'X-Client: training-client' http://127.0.0.1:8000/checked` вернёт `200`.
Неверное значение заголовка даёт `400`.
Отсутствующий обязательный заголовок даёт `422`.
Пример демонстрирует валидацию заголовка.
Этот заголовок не является секретным API-ключом или заменой [аутентификации](authentication.md).
[Подмените эту проверку в тесте](testing.md#подмена-зависимости), если тест должен проверять только обработчик.

Источники: [Depends](https://fastapi.tiangolo.com/tutorial/dependencies/), [подзависимости](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/), [проверка на уровне декоратора](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).

## Формы и загрузка файлов

**Ситуация:** один загруженный файл нужно прочитать порциями; больше 1 MiB обрабатывать нельзя.
**Изменение:** считайте накопленный размер и завершайте чтение с `413`.
Фрагмент `measure(file)` из [полного `uploads.py`](uploads.md#формы-и-загрузка-файлов):

```python
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
```

`file` — `UploadFile`, `MAX_BYTES = 1024 * 1024`.
Импортируйте `UploadFile` и `HTTPException` из FastAPI, как в полном приложении.
**Результат:** файл из `b"abc"` даёт размер `3`; файл больше лимита даёт `413`.
Лимит проверяется после multipart-парсинга и не ограничивает весь HTTP-запрос.
Задайте общий лимит тела и числа файлов на сервере или прокси.
[Формы, один/несколько файлов и запуск](uploads.md) · [Полные проверки](testing-lab.md#файлы-и-middleware).

## Middleware и CORS

**Ситуация:** браузер на `http://localhost:3000` должен читать API с credentials.
**Изменение:** перечислите origin явно.
Фрагмент [полного `middleware_app.py`](middleware.md#middleware-и-cors):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Process-Time"],
)
```

`app` — экземпляр `FastAPI`, а `CORSMiddleware` импортирован из `fastapi.middleware.cors`.
**Результат:** разрешённый origin получает CORS-заголовки; другой origin не получает разрешение браузерного чтения.
Origin включает scheme, host и port; `127.0.0.1` отличается от `localhost`.
CORS не проверяет пользователя.
[Полное приложение с таймером](middleware.md) · [Проверки preflight и отказа](testing-lab.md#файлы-и-middleware).
