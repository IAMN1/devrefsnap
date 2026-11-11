from decimal import Decimal

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from demo_crud import run
from demo_models import Comment, Post, Product, Profile, Status, Tag, User, new_engine


def test_crud():
    assert run() == ["alice", "bob"]


def test_savepoint_keeps_outer_transaction():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                session.add(User(name="alice", email="alice@example.com"))
            with session.begin():
                session.add(User(name="bob", email="bob@example.com"))
                try:
                    with session.begin_nested():
                        session.add(User(name="duplicate", email="alice@example.com"))
                        session.flush()
                except IntegrityError:
                    pass
                session.add(User(name="carol", email="carol@example.com"))
            assert session.scalars(select(User.name).order_by(User.id)).all() == ["alice", "bob", "carol"]
    finally:
        engine.dispose()


def test_rollback_after_invalid_flush():
    engine = new_engine()
    try:
        with Session(engine) as session:
            session.add(User(name="bad", email="bad@example.com", age=-1))
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()
            session.add(User(name="good", email="good@example.com"))
            session.commit()
            assert session.scalar(select(func.count()).select_from(User)) == 1
    finally:
        engine.dispose()


def test_relations_enum_and_json():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                user = User(name="alice", email="alice@example.com", profile=Profile(bio="Author"))
                user.posts = [Post(title="Python", comments=[Comment(text="Useful")], tags=[Tag(name="python")])]
                product = Product(price=Decimal("10.25"), attributes={"color": "blue"})
                session.add_all([user, product])
            assert session.scalar(select(User)).status == Status.ACTIVE
            assert session.scalar(text("SELECT status FROM users")) == "active"
            product.attributes["color"] = "green"
            session.commit()
            session.expire_all()
            assert session.scalar(select(Product)).attributes == {"color": "green"}
            assert session.scalar(select(Product)).price == Decimal("10.25")
            session.delete(session.scalar(select(User)))
            session.commit()
            assert session.scalar(select(func.count()).select_from(Post)) == 0
            assert session.scalar(select(func.count()).select_from(Comment)) == 0
            assert session.scalar(select(func.count()).select_from(Profile)) == 0
    finally:
        engine.dispose()
