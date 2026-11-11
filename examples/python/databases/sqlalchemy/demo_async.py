import asyncio

from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from demo_models import Base, Post, User


def new_async_engine():
    engine = create_async_engine("sqlite+aiosqlite://")

    @event.listens_for(engine.sync_engine, "connect")
    def sqlite_foreign_keys(connection, record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


async def run():
    engine = new_async_engine()
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            async with session.begin():
                user = User(name="alice", email="alice@example.com", posts=[Post(title="Async Python")])
                session.add(user)
                await session.flush()
                user_id = user.id
        async with sessions() as session:
            user = await session.get(User, user_id)
            posts = await user.awaitable_attrs.posts
            titles = [post.title for post in posts]
        async with sessions() as session:
            loaded = await session.scalar(select(User).where(User.id == user_id).options(selectinload(User.posts)))
        return titles, [post.title for post in loaded.posts]
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print(asyncio.run(run()))
