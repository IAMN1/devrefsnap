from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

engine = create_engine(
    "sqlite:///./fastapi-sync.db",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(200), unique=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserOut(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(engine)
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserCreate, session: Annotated[Session, Depends(get_session)]):
    row = UserDB(**user.model_dump())
    session.add(row)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(409, "Email уже используется") from exc
    session.refresh(row)
    return UserOut.model_validate(row)


@app.get("/users", response_model=list[UserOut])
def list_users(session: Annotated[Session, Depends(get_session)]):
    return session.scalars(select(UserDB).order_by(UserDB.id)).all()
