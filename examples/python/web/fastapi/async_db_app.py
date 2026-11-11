from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine("sqlite+aiosqlite:///./fastapi-async.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class NoteDB(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(200))


class NoteCreate(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class NoteOut(NoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


@app.post("/notes", response_model=NoteOut, status_code=201)
async def create_note(note: NoteCreate, session: Annotated[AsyncSession, Depends(get_session)]):
    async with session.begin():
        row = NoteDB(**note.model_dump())
        session.add(row)
        await session.flush()
    return NoteOut.model_validate(row)


@app.get("/notes", response_model=list[NoteOut])
async def list_notes(session: Annotated[AsyncSession, Depends(get_session)]):
    return (await session.scalars(select(NoteDB).order_by(NoteDB.id))).all()
