from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class Filters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


@app.get("/items")
def items(query: Annotated[Filters, Query()]):
    return query.model_dump()
