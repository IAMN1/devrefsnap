# Настроить CORS и время обработки

Откройте страницу, чтобы разрешить браузерному клиенту доступ с конкретного origin и добавить диагностический заголовок.
Пример не реализует аутентификацию и не измеряет отправку всего потокового тела.

| Задача | Приём | Пример |
| --- | --- | --- |
| Разрешить конкретный origin | `CORSMiddleware` с явным списком | [Полный middleware_app.py](#middleware-и-cors) |
| Добавить длительность обработки | HTTP middleware и `perf_counter` | [Полное приложение](#middleware-и-cors) |
| Проверить preflight | OPTIONS с заголовками браузера | [Полные тесты](testing-lab.md#файлы-и-middleware) |

[Карточки HTTP](recipes.md) · [Справочник FastAPI](README.md) · [Проверки](testing.md)

Уровень: средний.
Используйте Python 3.14.
В отдельном окружении выполните `python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]'`.

## Middleware и CORS

Сохраните самостоятельный пример в файле `middleware_app.py`.

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
