from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator, model_validator

app = FastAPI(title="Каталог товаров", version="1.0.0")


def validation_details(exc: RequestValidationError | ValidationError):
    return [{key: error[key] for key in ("loc", "msg", "type")} for error in exc.errors()]


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": validation_details(exc)})


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price: float = Field(gt=0, allow_inf_nan=False)
    tax: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Название не должно быть пустым")
        return value

    @model_validator(mode="after")
    def premium_price(self) -> "ItemCreate":
        if self.name == "premium" and self.price < 100:
            raise ValueError("Цена premium должна быть не меньше 100")
        return self


class ItemOut(ItemCreate):
    id: int


class ItemPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    price: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    tax: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    tags: list[str] | None = None


class Pagination:
    def __init__(
        self,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
    ):
        self.offset = offset
        self.limit = limit


def search_query(q: Annotated[str | None, Query(max_length=100)] = None):
    return q


def effective_query(
    q: Annotated[str | None, Depends(search_query)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    return q if q is not None else last_query


items: dict[int, ItemOut] = {}


def existing_item(item_id: Annotated[int, Path(gt=0)]) -> ItemOut:
    if item_id not in items:
        raise HTTPException(404, "Товар не найден", headers={"X-Error": "item-missing"})
    return items[item_id]


@app.get("/")
async def root():
    return {"message": "Каталог работает"}


@app.post("/items", response_model=ItemOut, status_code=201)
async def create_item(item: ItemCreate):
    item_id = max(items, default=0) + 1
    saved = ItemOut(id=item_id, **item.model_dump())
    items[item_id] = saved
    return saved


@app.get("/items", response_model=list[ItemOut])
async def list_items(
    page: Annotated[Pagination, Depends()],
    query: Annotated[str | None, Depends(effective_query)],
    tags: Annotated[list[str] | None, Query()] = None,
):
    result = [item for item in items.values()
              if (query is None or query in item.name)
              and (not tags or set(tags).issubset(item.tags))]
    return result[page.offset:page.offset + page.limit]


@app.get("/items/{item_id}", response_model=ItemOut)
async def read_item(item: Annotated[ItemOut, Depends(existing_item)]):
    return item


@app.put("/items/{item_id}", response_model=ItemOut)
async def replace_item(item_id: int, item: ItemCreate):
    existing_item(item_id)
    items[item_id] = ItemOut(id=item_id, **item.model_dump())
    return items[item_id]


@app.patch("/items/{item_id}", response_model=ItemOut)
async def patch_item(item_id: int, patch: ItemPatch):
    current = existing_item(item_id)
    data = {**current.model_dump(exclude={"id"}), **patch.model_dump(exclude_unset=True)}
    try:
        validated = ItemCreate.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(422, validation_details(exc)) from exc
    items[item_id] = ItemOut(id=item_id, **validated.model_dump())
    return items[item_id]


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    existing_item(item_id)
    del items[item_id]
    return Response(status_code=204)


@app.get("/users/{user_id}/items/{item_id}")
async def nested_path(user_id: int, item_id: int, short: bool = False):
    return {"user_id": user_id, "item_id": item_id, "short": short}


class UserOut(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserIn(UserOut):
    password: str = Field(min_length=8)


@app.post("/user-preview", response_model=UserOut)
async def preview_user(user: UserIn):
    return user


class StockError(Exception):
    pass


@app.exception_handler(StockError)
async def stock_error_handler(request: Request, exc: StockError):
    return JSONResponse(status_code=409, content={"detail": "Недостаточно товара"})


@app.get("/stock/{quantity}")
async def check_stock(quantity: Annotated[int, Path(gt=0)]):
    if quantity > 5:
        raise StockError()
    return {"available": True}


@app.get("/custom")
async def custom_response():
    return JSONResponse({"message": "Особый ответ"}, headers={"X-Custom": "demo"})


@app.get("/html", response_class=HTMLResponse)
async def html():
    return "<h1>Каталог товаров</h1>"


@app.get("/redirect")
async def redirect():
    return RedirectResponse("/docs", status_code=307)
