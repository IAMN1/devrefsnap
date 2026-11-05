# Pydantic v2 Шпаргалка

## Содержание
- [Введение](#введение)
- [Базовые модели](#базовые-модели)
- [Типы данных](#типы-данных)
- [Валидация](#валидация)
- [Настройки моделей](#настройки-моделей)
- [Работа с JSON](#работа-с-json)
- [Модели ORM](#модели-orm)
- [Создание типов](#создание-типов)
- [Полезные паттерны](#полезные-паттерны)
- [Производительность](#производительность)
- [Миграция с v1](#миграция-с-v1)

## Введение

Pydantic — библиотека для валидации данных и управления настройками через аннотации типов Python. Основные возможности:

- **Валидация данных** через аннотации типов
- **Сериализация/десериализация** JSON, YAML и других форматов
- **Настройки приложений** с загрузкой из переменных окружения
- **Генерация схем** JSON Schema, OpenAPI

```bash
# Установка
pip install pydantic
pip install pydantic[email]  # с дополнительными типами
pip install pydantic-settings  # для работы с настройками
```

## Базовые модели

```python
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime

class User(BaseModel):
    # Обязательные поля
    id: int
    username: str
    email: str
    
    # Необязательные поля с значениями по умолчанию
    age: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Поле с валидацией длины
    password: str = Field(min_length=8, max_length=100)
    
    # Псевдонимы для полей (алиасы)
    full_name: str = Field(alias="fullName")
    
    # Скрытие поля в выводе
    secret_key: str = Field(exclude=True)
    
    # Примеры значений для документации
    role: str = Field(examples=["admin", "user", "guest"])

# Создание экземпляра
user = User(
    id=1,
    username="john_doe",
    email="john@example.com",
    fullName="John Doe",  # используем алиас
    password="secure123"
)

# Доступ к данным
print(user.id)  # 1
print(user.model_dump())  # преобразование в dict
```

## Типы данных

### Скалярные типы
```python
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr, PaymentCardNumber
from decimal import Decimal
from uuid import UUID
from ipaddress import IPv4Address

class DataTypes(BaseModel):
    # Строки с валидацией
    email: EmailStr
    url: HttpUrl
    secret: SecretStr  # скрывается при выводе
    ip: IPv4Address
    
    # Числовые типы
    decimal: Decimal = Field(max_digits=10, decimal_places=2)
    ratio: float = Field(ge=0.0, le=1.0)  # от 0 до 1
    
    # Специальные типы
    uuid: UUID
    card_number: PaymentCardNumber
    
    # Псевдонимы типов
    UserID = int  # создаем тип для семантики
    user_id: UserID
```

### Составные типы
```python
from typing import Union, Literal, Annotated
from pydantic import BaseModel, Field
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class ComplexTypes(BaseModel):
    # Union типы
    value: Union[int, str, None]
    
    # Литералы
    status: Literal["active", "inactive", "pending"]
    
    # Enum
    enum_status: Status
    
    # Списки и словари
    tags: List[str] = Field(min_length=1, max_length=10)
    metadata: Dict[str, Any]
    
    # Вложенные модели
    friends: List["User"] = []  # forward reference
    
    # Аннотированные типы
    score: Annotated[int, Field(ge=0, le=100)]
```

## Валидация

### Встроенные валидаторы
```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import ClassVar

class Product(BaseModel):
    name: str
    price: float
    discount_price: Optional[float] = None
    
    # Валидатор для отдельного поля
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return round(v, 2)
    
    # Валидатор для нескольких полей
    @field_validator('name', 'price')
    @classmethod
    def validate_name_price(cls, v, info):
        if info.field_name == 'name' and len(v) < 2:
            raise ValueError('Name too short')
        return v
    
    # Валидатор модели (до/после)
    @model_validator(mode='after')
    def validate_discount(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValueError('Discount must be less than price')
        return self
    
    # Root валидатор (для всей модели)
    @model_validator(mode='before')
    @classmethod
    def validate_root(cls, data):
        if isinstance(data, dict) and 'price' in data:
            data['price'] = float(data['price'])
        return data
    
    # Поле только для чтения (вычисляемое)
    @property
    def final_price(self) -> float:
        return self.discount_price or self.price
```

### Кастомные валидаторы
```python
from pydantic import BaseModel, field_validator
import re

class CustomValidation(BaseModel):
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number')
        return v
```

## Настройки моделей

```python
from pydantic import BaseModel, ConfigDict
from typing import ClassVar

class ConfigExample(BaseModel):
    # Конфигурация через ConfigDict (новый способ в v2)
    model_config = ConfigDict(
        # Режимы валидации
        validate_assignment=True,  # валидация при присваивании
        revalidate_instances='always',  # всегда ревалидировать
        
        # Сериализация
        from_attributes=True,  # создание из ORM объектов
        populate_by_name=True,  # разрешить имена полей и алиасы
        
        # Дополнительные параметры
        extra='forbid',  # запретить лишние поля
        str_strip_whitespace=True,  # обрезать пробелы в строках
        str_min_length=1,  # минимальная длина строки
        use_enum_values=True,  # использовать значения enum
        
        # Заморозка модели
        frozen=True,  # сделать модель неизменяемой
        
        # Скрытие полей
        protected_namespaces=('protect_',)  # защищенные пространства имен
    )
    
    # Статические поля (не включены в схему)
    _secret: ClassVar[str] = "hidden"
    
    # Публичные поля
    public_field: str
```

## Работа с JSON

```python
from pydantic import BaseModel
import json

class Item(BaseModel):
    name: str
    price: float

# Сериализация
item = Item(name="Laptop", price=999.99)
json_str = item.model_dump_json()  # -> JSON строка
dict_data = item.model_dump()      # -> словарь

# Десериализация
item2 = Item.model_validate_json(json_str)
item3 = Item.model_validate(dict_data)

# Кастомная сериализация
class CustomJSON(BaseModel):
    dt: datetime
    
    @field_serializer('dt')
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()

# Режимы сериализации
json_with_mode = item.model_dump_json(
    mode='json',  # 'json' или 'python'
    indent=2,
    exclude={'price'},  # исключить поля
    include={'name'},   # только указанные поля
    by_alias=True       # использовать алиасы
)
```

## Модели ORM

```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Pydantic модель для ORM
class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    
    model_config = ConfigDict(
        from_attributes=True,  # было orm_mode в v1
        populate_by_name=True
    )

# Конвертация ORM -> Pydantic
db_user = UserDB(id=1, name="John", email="john@example.com")
schema_user = UserSchema.model_validate(db_user)

# Модель только для создания (без id)
class UserCreate(BaseModel):
    name: str
    email: str
```

## Создание типов

### Кастомные типы
```python
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any

class CustomType:
    def __init__(self, value: str):
        self.value = value
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )
    
    @classmethod
    def validate(cls, v: Any, info):
        if not isinstance(v, str):
            raise ValueError('Must be string')
        if len(v) < 3:
            raise ValueError('Too short')
        return cls(v)

class WithCustomType(BaseModel):
    data: CustomType
```

### Generic модели
```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int

# Использование
user_response = Response[User](success=True, data=user)
paginated = PaginatedResponse[User](items=[user], total=1, page=1, per_page=10)
```

## Полезные паттерны

### Модель настроек
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Автоматическая загрузка из .env файла и переменных окружения
    app_name: str = "My App"
    database_url: str
    api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()  # загружает из окружения
```

### Динамические модели
```python
from pydantic import create_model, BaseModel
from typing import Dict

# Создание модели на лету
DynamicModel = create_model(
    'DynamicModel',
    name=(str, ...),  # обязательное поле
    value=(int, 0),   # поле со значением по умолчанию
)

# Модель с динамическими полями
class FlexibleModel(BaseModel):
    data: Dict[str, Any]
    model_config = ConfigDict(extra='allow')
```

### Валидация запросов FastAPI
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class ItemQuery(BaseModel):
    q: str = Field(min_length=1)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

@app.get("/items/")
async def read_items(query: ItemQuery):
    return {"query": query}
```

## Производительность

### Оптимизации
```python
# 1. Используйте __slots__ для уменьшения памяти
class OptimizedModel(BaseModel):
    __slots__ = ('field1', 'field2')
    field1: str
    field2: int
    
    model_config = ConfigDict(
        frozen=True,  # иммутабельные модели быстрее
    )

# 2. Кэширование схемы
from pydantic import TypeAdapter

UserListAdapter = TypeAdapter(List[User])
users = UserListAdapter.validate_python([{"id": 1, "name": "John"}])

# 3. Избегайте лишней валидации
user = User.model_construct(id=1, name="John")  # без валидации
```

### Бенчмаркинг
```python
# Для тестирования производительности
import time
from pydantic import BaseModel

class SimpleModel(BaseModel):
    x: int
    y: str

# Тест сериализации
start = time.time()
for _ in range(10000):
    m = SimpleModel(x=1, y="test")
    m.model_dump()
print(f"Time: {time.time() - start}")
```

## Миграция с v1

### Основные изменения
```python
# v1 (старый) -> v2 (новый)

# Конфигурация
class OldConfig:
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class NewConfig:
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

# Валидаторы
@validator('field')           # v1 -> @field_validator('field') в v2
@root_validator               # v1 -> @model_validator(mode='before/after') в v2

# Сериализация
dict()                        # v1 -> model_dump() в v2
json()                        # v1 -> model_dump_json() в v2
parse_obj()                   # v1 -> model_validate() в v2
parse_raw()                   # v1 -> model_validate_json() в v2

# Настройки
BaseSettings в pydantic v1 -> pydantic_settings в v2
```

### Автоматическая миграция
```bash
# Установка инструментов миграции
pip install pydantic-v1 pydantic

# Использование совместимости
from pydantic import v1 as pydantic_v1
from pydantic.v1 import BaseModel as V1BaseModel

# Постепенная миграция
class MixedModel(V1BaseModel):
    # старая модель
    pass

class NewModel(BaseModel):
    # новая модель
    pass
```

---

## Полезные ссылки
- [Документация Pydantic](https://docs.pydantic.dev)
- [GitHub Repository](https://github.com/pydantic/pydantic)
- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Список типов](https://docs.pydantic.dev/latest/concepts/types/)

## Советы
1. Всегда включайте `validate_assignment=True` для валидации при изменении
2. Используйте `TypeAdapter` для работы с типами без создания моделей
3. Для высоконагруженных API кэшируйте схемы валидации
4. При миграции с v1 используйте постепенный подход
5. Для работы с ORM всегда включайте `from_attributes=True`

Эта шпаргалка охватывает ключевые аспекты Pydantic v2, актуальные на начало 2026 года. Основные изменения по сравнению с более ранними версиями:

1. **ConfigDict вместо Config класса** - новый способ конфигурации
2. **TypeAdapter** для работы с отдельными типами
3. **Улучшенная производительность** - до 50x быстрее v1
4. **pydantic-settings** выделен в отдельный пакет
5. **Новые методы валидации** - `field_validator` и `model_validator`

