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
