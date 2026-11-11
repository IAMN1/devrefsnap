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
