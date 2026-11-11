import pytest
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload

from demo_models import User, new_engine
from demo_queries import seed


@pytest.fixture
def engine():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
        yield engine
    finally:
        engine.dispose()


def test_partitions_preserve_all_names(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).order_by(User.id).execution_options(yield_per=1))
        names = []
        for batch in result.partitions():
            assert len(batch) == 1
            names.extend(user.name for user in batch)
        assert names == ["alice", "bob"]


def test_selectin_with_partitions_on_sqlite(engine):
    with Session(engine) as session:
        result = session.scalars(
            select(User).options(selectinload(User.posts)).order_by(User.id)
            .execution_options(yield_per=1)
        )
        observed = [(user.name, len(user.posts)) for batch in result.partitions() for user in batch]
        assert observed == [("alice", 2), ("bob", 0)]


@pytest.mark.parametrize("loader", [joinedload, subqueryload])
def test_collection_loaders_reject_yield_per(engine, loader):
    with Session(engine) as session:
        with pytest.raises(InvalidRequestError):
            session.scalars(
                select(User).options(loader(User.posts)).execution_options(yield_per=1)
            ).all()


def test_unique_rejects_yield_per(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).execution_options(yield_per=1))
        with pytest.raises(InvalidRequestError):
            list(result.unique())
