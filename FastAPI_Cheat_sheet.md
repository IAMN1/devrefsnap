# 📘 Шпаргалка по FastAPI

*Краткий справочник по основным возможностям FastAPI. Сохраняйте, чтобы всегда иметь под рукой!*

---

## 📑 Содержание

- [Быстрый старт](#быстрый-старт)
- [Маршрутизация](#маршрутизация)
- [Параметры запроса](#параметры-запроса)
- [Модели Pydantic](#модели-pydantic)
- [Статус коды и ответы](#статус-коды-и-ответы)
- [Обработка ошибок](#обработка-ошибок)
- [Зависимости (Dependencies)](#зависимости-dependencies)
- [База данных](#база-данных)
- [Аутентификация](#аутентификация)
- [Middleware](#middleware)
- [Тестирование](#тестирование)
- [Деплой](#деплой)
- [Полезные команды](#полезные-команды)

---

## 🚀 Быстрый старт

```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Запуск: uvicorn main:app --reload
```

## 📍 Маршрутизация

### Методы HTTP
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
async def read_items():
    return ["item1", "item2"]

@app.post("/items")
async def create_item(item: dict):
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: dict):
    return {"item_id": item_id, **item}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": item_id}

@app.patch("/items/{item_id}")
async def patch_item(item_id: int, item: dict):
    return {"patched": item_id, **item}
```

### Пути с параметрами
```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: str = None,
    short: bool = False
):
    return {"user_id": user_id, "item_id": item_id, "q": q, "short": short}
```

## 🔍 Параметры запроса

### Query-параметры
```python
from typing import Optional, List

@app.get("/items/")
async def read_items(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    tags: List[str] = []
):
    return {"skip": skip, "limit": limit, "search": search, "tags": tags}
```

### Path-параметры
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### Body-параметры
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Form-данные
```python
from fastapi import Form

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

### File-загрузка
```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}
```

### Несколько файлов
```python
@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
```

## 📦 Модели Pydantic

### Базовые модели
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []

class UserIn(User):
    password: str

class UserOut(User):
    class Config:
        exclude = {"password"}
```

### Валидация
```python
from pydantic import validator, root_validator

class Item(BaseModel):
    name: str
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть положительной')
        return v
    
    @root_validator
    def check_name_and_price(cls, values):
        if 'name' in values and 'price' in values:
            if values['name'] == 'premium' and values['price'] < 100:
                raise ValueError('Премиум товары дороже 100')
        return values
```

## 📊 Статус коды и ответы

### Кастомные ответы
```python
from fastapi import Response, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

@app.get("/custom/")
async def custom_response():
    data = {"message": "Hello"}
    return JSONResponse(
        content=data,
        status_code=200,
        headers={"X-Custom-Header": "value"}
    )

@app.get("/html/")
async def html():
    html_content = "<h1>Hello World</h1>"
    return HTMLResponse(content=html_content)

@app.get("/redirect/")
async def redirect():
    return RedirectResponse(url="/docs")
```

### Response Model
```python
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    # Логика создания
    return user

@app.get("/items/", response_model=List[Item])
async def read_items():
    return [Item(name="Item1"), Item(name="Item2")]
```

## ❌ Обработка ошибок

### Стандартные исключения
```python
from fastapi import FastAPI, HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Item ID doesn't exist"}
        )
    return {"item": items_db[item_id]}
```

### Кастомные обработчики
```python
from fastapi import Request
from fastapi.responses import JSONResponse

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
```

## 🔗 Зависимости (Dependencies)

### Простые зависимости
```python
from fastapi import Depends

def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### Зависимости с классами
```python
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(pagination: Pagination = Depends()):
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### Подзависимости
```python
def query_extractor(q: str = None):
    return q

def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: str = None
):
    if not q:
        return last_query
    return q

@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}
```

### Зависимости на уровне пути
```python
async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

@app.get("/items/", dependencies=[Depends(verify_token)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]
```

## 💾 База данных

### SQLAlchemy (пример)
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
async def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserDB(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### Асинхронная база данных
```python
from databases import Database

database = Database("sqlite:///./test.db")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
```

## 🔐 Аутентификация

### OAuth2 с паролями
```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Проверка пользователя
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # Декодирование токена
    return {"token": token}
```

## 🛠️ Middleware

### Кастомный middleware
```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### CORS middleware
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Тестирование

### Тесты с pytest
```python
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Foo", "price": 45.2}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Foo"
```

### Тесты с асинхронным клиентом
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/items/1")
    assert response.status_code == 200
```

## 🚢 Деплой

### Uvicorn workers
```bash
# Продакшен
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4

# С Gunicorn (для Linux)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80
```

### Dockerfile
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

## 📝 Полезные команды

```bash
# Установка
pip install fastapi[all]
pip install fastapi uvicorn

# Запуск разработки
uvicorn main:app --reload
uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Документация
http://localhost:8000/docs     # Swagger UI
http://localhost:8000/redoc    # ReDoc

# Генерация схемы
python -c "import main; import json; print(json.dumps(main.app.openapi()))" > openapi.json
```

## 📚 Полезные ссылки

- [Официальная документация](https://fastapi.tiangolo.com/)
- [FastAPI на GitHub](https://github.com/tiangolo/fastapi)
- [Pydantic документация](https://pydantic-docs.helpmanual.io/)
- [Uvicorn документация](https://www.uvicorn.org/)

---

## 🎯 Быстрые советы

1. **Всегда используйте аннотации типов** - это дает автоматическую валидацию и документацию
2. **Pydantic модели** для входных/выходных данных
3. **Depends()** для инъекции зависимостей
4. **async/await** для I/O операций
5. **TestClient** для тестирования
6. **--reload** флаг при разработке
7. **Документация доступна автоматически** на `/docs` и `/redoc`

---

## 📄 Лицензия
Эта шпаргалка доступна для свободного использования. Делитесь с коллегами!
