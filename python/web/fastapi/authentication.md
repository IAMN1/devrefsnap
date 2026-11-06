# Проверить пароль и защитить маршрут JWT

[Краткий справочник](README.md) · [Тесты отказа доступа](testing.md#аутентификация)

| Параметр | Значение |
| --- | --- |
| Уровень | Продвинутый |
| Предпосылки | HTTP Authorization, зависимости, переменные окружения, основы хеширования и JWT |
| Сверено с документацией | 2026-11-06: FastAPI 0.162.0, PyJWT и pwdlib |
| Выполнено | 2026-11-06: вход, защищённый маршрут и отказы доступа проверены тестами. Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, PyJWT 2.15.1, pwdlib 0.3.1 с Argon2, python-multipart 0.0.33 |

Учебный сценарий: форма с логином/паролем → проверка Argon2-хеша → JWT с ограниченным сроком → проверка JWT и пользователя на защищённом маршруте.
Это минимальная локальная демонстрация.
OAuth2 password flow требует доверенного клиента.
Этот flow не заменяет внешний провайдер входа для произвольных приложений.

## Подготовка

В отдельном виртуальном окружении:

```bash
python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]' python-multipart PyJWT 'pwdlib[argon2]'
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Ключ создаётся локально для учебного запуска.
Не записывайте ключ в исходники.
Используйте один и тот же ключ во всех процессах одного приложения.
Новый ключ после перезапуска делает прежние токены недействительными.

## Полный пример

Сохраните полный пример в файле `auth_app.py`.
Учебный пользователь — `alice`.
Учебный пароль — `training-password-123`.
Пароль открыто указан только для воспроизводимости примера.
Словарь хранит хеш пароля.

<!-- example: auth_app.py -->
```python
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
if len(SECRET_KEY) < 32:
    raise RuntimeError("Для учебного JWT нужен случайный ключ длиной не меньше 32 символов")
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 15

app = FastAPI()
password_hash = PasswordHash.recommended()
demo_hash = password_hash.hash("training-password-123")
dummy_hash = password_hash.hash("unused-demo-password")
users = {"alice": {"username": "alice", "password_hash": demo_hash, "disabled": False}}
oauth2 = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PublicUser(BaseModel):
    username: str


def unauthorized() -> HTTPException:
    return HTTPException(401, "Неверные учётные данные", headers={"WWW-Authenticate": "Bearer"})


def issue_token(username: str, *, lifetime: timedelta | None = None) -> str:
    duration = lifetime if lifetime is not None else timedelta(minutes=ACCESS_TOKEN_MINUTES)
    claims = {"sub": username, "exp": datetime.now(timezone.utc) + duration}
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users.get(form.username)
    stored_hash = user["password_hash"] if user else dummy_hash
    valid_password = password_hash.verify(form.password, stored_hash)
    if not user or not valid_password or user["disabled"]:
        raise unauthorized()
    return Token(access_token=issue_token(user["username"]))


def current_user(token: Annotated[str, Depends(oauth2)]) -> PublicUser:
    try:
        claims = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        username = claims["sub"]
        if not isinstance(username, str) or not username:
            raise unauthorized()
    except InvalidTokenError as exc:
        raise unauthorized() from exc
    user = users.get(username)
    if user is None or user["disabled"]:
        raise unauthorized()
    return PublicUser(username=user["username"])


@app.get("/users/me", response_model=PublicUser)
def me(user: Annotated[PublicUser, Depends(current_user)]):
    return user
```

Хеширование пароля занимает процессорное время.
Поэтому пример использует синхронные функции.
FastAPI выполнит обработчик `def` и зависимость `def` в пуле потоков.
Dummy hash сохраняет работу проверки хеша для неизвестного имени.
Этот приём не обещает одинаковое время HTTP-ответа.

## Запуск и результат

```bash
uvicorn auth_app:app --reload
```

В другом терминале:

```bash
curl -i -X POST http://127.0.0.1:8000/token -d 'username=alice&password=training-password-123'
curl -i http://127.0.0.1:8000/users/me
```

Первый запрос даёт `200`, `access_token` и `token_type=bearer`.
Второй запрос даёт `401`.
В curl передайте полученный токен в заголовке `Authorization: Bearer <токен>`.
Маршрут `/users/me` вернёт `{"username":"alice"}`.
В Swagger UI `/docs` нажмите **Authorize**.
Введите учебные username/password.
UI сам получит токен у `/token`.
Затем UI подставит заголовок.
Неверный пароль даёт `401`.
Испорченный или истёкший токен даёт `401`.
Отсутствие обязательного `exp` даёт `401`.
Неизвестный пользователь даёт `401`.
[Тесты](testing.md#аутентификация) проверяют эти случаи без запуска HTTP-сервера.

## Ограничения и следующие задачи

- JWT подписан, но payload токена не зашифрован. Не помещайте в payload пароль или другие секреты. Алгоритм задаёт сервер. Сервер не выбирает алгоритм из непроверенного заголовка токена.
- Демо-словарь и хеш создаются при импорте для одного известного пользователя. Настоящие хеши хранятся в БД. Клиент никогда не получает `password_hash`.
- Для эксплуатации нужны HTTPS, ограничения перебора паролей, управление ключами, политика отзыва/обновления токенов и проверка разрешений. При нескольких потребителях/издателях настройте также `aud`/`iss`. Здесь приложение одно, поэтому `aud`/`iss` отсутствуют.
- Нет регистрации, восстановления пароля, refresh-токенов и полной интеграции с внешним OAuth/OIDC-провайдером. Не добавляйте эти возможности в короткий рецепт без отдельной модели угроз и требований.

Источники: [FastAPI: пароль, хеширование и JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [PyJWT: проверка exp и обязательных claims](https://pyjwt.readthedocs.io/en/stable/usage.html), [PyJWT: decode и алгоритмы](https://pyjwt.readthedocs.io/en/stable/api.html#jwt.decode), [pwdlib: базовый API](https://frankie567.github.io/pwdlib/guide/).
