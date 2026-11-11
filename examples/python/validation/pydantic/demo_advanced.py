import re
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler, TypeAdapter, create_model
from pydantic_core import core_schema

from demo_types import UserView

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)


class Slug(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(cls.check, handler(str))

    @classmethod
    def check(cls, value: str):
        if not re.fullmatch(r"[a-z][a-z0-9-]*", value):
            raise ValueError("Ожидается slug из строчных латинских букв, цифр и дефиса")
        return cls(value)


class Article(BaseModel):
    slug: Slug


class Flexible(BaseModel):
    model_config = ConfigDict(extra="allow")
    metadata: dict[str, Any] = Field(default_factory=dict)


Label = create_model("Label", name=(str, ...), weight=(int, 0))
user_list = TypeAdapter(list[UserView])


if __name__ == "__main__":
    users = user_list.validate_python([{"id": 1, "name": "Alice"}])
    print(Page[UserView](items=users, total=1, page=1, per_page=10).model_dump_json())
    print(Article(slug="python-guide").model_dump_json())
