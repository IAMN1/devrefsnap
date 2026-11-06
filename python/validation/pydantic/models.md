# Проверить модель и сериализовать данные

[Справочник](README.md) · [Расширенные задачи](advanced.md)

**Уровень:** базовый → средний.
**Предпосылки:** классы, типы, Decimal и JSON.
Поместите все файлы ниже в одну учебную папку.
Используйте Python 3.14.7.
Выполните `python -m pip install 'pydantic[email]==2.14.3' 'email-validator==2.3.0' 'pytest==9.2.0'`.

## Модели, валидация и JSON

Полный пример `demo_models.py` разделяет вход пользователя и публичный вывод.
Пример не возвращает пароль.

<!-- example: pydantic/demo_models.py -->
```python
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, SecretStr
from pydantic import computed_field, field_serializer, field_validator, model_validator


class PublicUser(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True,
        validate_by_name=True, validate_by_alias=True,
    )
    id: int = Field(gt=0)
    full_name: str = Field(alias="fullName", min_length=2)
    email: EmailStr
    role: Literal["user", "admin"] = "user"
    age: int | None = Field(default=None, ge=0)
    tags: list[str] = Field(default_factory=list)
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("created_at", when_used="json")
    def utc_seconds(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class UserInput(PublicUser):
    password: SecretStr = Field(exclude=True, min_length=8)


class Product(BaseModel):
    name: str = Field(min_length=1)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, allow_inf_nan=False)
    discount_price: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)

    @model_validator(mode="before")
    @classmethod
    def old_title(cls, data):
        if isinstance(data, dict) and "title" in data and "name" not in data:
            data = {**data, "name": data["title"]}
        return data

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Название не должно быть пустым")
        return value

    @model_validator(mode="after")
    def valid_discount(self) -> "Product":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("Скидочная цена должна быть меньше обычной")
        return self

    @computed_field
    @property
    def final_price(self) -> Decimal:
        return self.discount_price if self.discount_price is not None else self.price


class Tree(BaseModel):
    name: str
    children: list["Tree"] = Field(default_factory=list)


if __name__ == "__main__":
    user = UserInput(id=1, fullName=" Alice Doe ", email="alice@example.com", password="training-password")
    public = PublicUser.model_validate(user.model_dump())
    print(public.model_dump_json(by_alias=True))
    product = Product.model_validate_json('{"title":"Book","price":"10.00","discount_price":"0"}')
    print(product.model_dump(mode="json"))
```

Запустите `python demo_models.py`.
Результат содержит JSON пользователя без пароля.
У товара `final_price` равна `"0"`.
`model_dump()` сохраняет Decimal.
Параметр `mode="json"` делает строковое представление JSON-совместимым.
Для выборочного вывода используйте `include`, `exclude`, `exclude_unset` или `exclude_none`.
Эти параметры не меняют правила входа.
Сериализация с исключёнными обязательными полями не обязана проходить обратную проверку той же входной моделью.

Поле `created_at` требует timezone через `AwareDatetime`.
Модель отвергает значение без смещения.
Значение `2026-11-06T12:00:00+03:00` сериализуется как `2026-11-06T09:00:00Z`.
Преобразование не использует локальную timezone машины.
Вывод имеет точность до секунды.

Полный `test_models.py`:

<!-- example: pydantic/test_models.py -->
```python
from decimal import Decimal

import pytest
from pydantic import ValidationError

from demo_models import Product, PublicUser, Tree, UserInput


def test_alias_and_public_output():
    user = UserInput(id="1", fullName=" Alice Doe ", email="alice@example.com", password="training-password")
    assert user.id == 1
    assert user.full_name == "Alice Doe"
    assert "password" not in user.model_dump()
    assert PublicUser.model_validate(user.model_dump()).model_dump(by_alias=True)["fullName"] == "Alice Doe"


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        PublicUser(id=1, fullName="Alice", email="alice@example.com", created_at="2026-11-06T12:00:00")


def test_offset_timestamp_serializes_in_utc():
    user = PublicUser(id=1, fullName="Alice", email="alice@example.com", created_at="2026-11-06T12:00:00+03:00")
    assert user.model_dump(mode="json")["created_at"] == "2026-11-06T09:00:00Z"


@pytest.mark.parametrize("patch", [{"id": 0}, {"email": "bad"}, {"role": "root"}, {"extra": 1}])
def test_invalid_user(patch):
    data = {"id": 1, "fullName": "Alice", "email": "alice@example.com", **patch}
    with pytest.raises(ValidationError):
        PublicUser.model_validate(data)


def test_zero_discount_and_json_roundtrip():
    product = Product(name="Book", price="10.00", discount_price="0")
    assert product.final_price == Decimal("0")
    assert Product.model_validate_json(product.model_dump_json()).final_price == Decimal("0")


@pytest.mark.parametrize("price,discount", [("10", "10"), ("0", None), ("Infinity", None), ("NaN", None)])
def test_invalid_product(price, discount):
    with pytest.raises(ValidationError):
        Product(name="Book", price=price, discount_price=discount)


def test_recursive_model_and_independent_lists():
    first = Tree(name="root", children=[{"name": "leaf"}])
    second = Tree(name="other")
    assert first.children[0].name == "leaf"
    assert second.children == []
```

## Атрибуты, конфигурация и типы

Полный пример `demo_types.py` читает ORM-подобные объекты без подключения БД.
Для настоящего SQLAlchemy используйте [его рецепты](../../databases/sqlalchemy/README.md).

<!-- example: pydantic/demo_types.py -->
```python
from dataclasses import dataclass
from enum import Enum
from ipaddress import IPv4Address
from typing import Annotated, ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

PositiveID = Annotated[int, Field(gt=0)]


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: ClassVar[str] = "payload"
    user_id: PositiveID
    url: HttpUrl
    ip: IPv4Address
    uuid: UUID
    status: Status
    value: int | str | None
    score: float = Field(ge=0, le=1, allow_inf_nan=False)
    metadata: dict[str, str] = Field(default_factory=dict)


@dataclass
class UserRow:
    id: int
    name: str


class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True, revalidate_instances="always")
    id: int
    name: str


class Counter(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    value: int = Field(ge=0)


class FrozenPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int


class StrictCount(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int
```

Полный `test_types.py`:

<!-- example: pydantic/test_types.py -->
```python
import pytest
from pydantic import ValidationError

from demo_types import Counter, FrozenPoint, Payload, StrictCount, UserRow, UserView


def test_orm_like_attributes():
    assert UserView.model_validate(UserRow(1, "Alice")).name == "Alice"


def test_assignment_and_frozen():
    counter = Counter(value=1)
    with pytest.raises(ValidationError):
        counter.value = -1
    assert counter.value == 1
    with pytest.raises(ValidationError):
        FrozenPoint(x=1).x = 2
    with pytest.raises(ValidationError):
        StrictCount(count="1")


def test_scalar_types():
    data = dict(user_id=1, url="https://example.com", ip="192.0.2.1",
                uuid="12345678-1234-5678-1234-567812345678", status="active", value=None, score=0.5)
    payload = Payload.model_validate(data)
    assert str(payload.ip) == "192.0.2.1"
    assert "kind" not in payload.model_dump()
    with pytest.raises(ValidationError):
        Payload.model_validate({**data, "score": float("inf")})
```

Запустите все тесты страницы: `python -m pytest -q test_models.py test_types.py`.
Ожидается успешная проверка допустимых значений.
Для указанных невалидных значений ожидаются отказы.
Телефон можно ограничить `Field(pattern=r'^\+?[1-9][0-9]{1,14}$')`.
Этот синтаксический шаблон не подтверждает существование номера.
После установки `pydantic-extra-types` импортируйте `PaymentCardNumber` для новых примеров из `pydantic_extra_types.payment`.
Не логируйте платёжные данные ради проверки типа.

Источники: [валидаторы](https://docs.pydantic.dev/latest/concepts/validators/), [сериализаторы](https://docs.pydantic.dev/latest/concepts/serialization/), [ConfigDict](https://docs.pydantic.dev/latest/api/config/), [стандартные типы](https://docs.pydantic.dev/latest/api/standard_library_types/), [PaymentCardNumber](https://docs.pydantic.dev/latest/api/pydantic_extra_types_payment/).
