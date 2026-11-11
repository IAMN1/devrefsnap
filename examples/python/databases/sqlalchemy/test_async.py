import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from demo_async import new_async_engine, run
from demo_models import Base, User


@pytest.mark.asyncio
async def test_async_roundtrip_and_loaded_relations():
    assert await run() == (["Async Python"], ["Async Python"])


@pytest.mark.asyncio
async def test_async_foreign_key_rejection_and_rollback():
    engine = new_async_engine()
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine)
        async with sessions() as session:
            session.add(User(name="orphan", email="orphan@example.com", manager_id=999))
            with pytest.raises(IntegrityError):
                await session.flush()
            await session.rollback()
            session.add(User(name="valid", email="valid@example.com"))
            await session.commit()
            assert await session.scalar(select(func.count()).select_from(User)) == 1
            assert await session.scalar(select(User.name)) == "valid"
    finally:
        await engine.dispose()
