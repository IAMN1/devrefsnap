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
