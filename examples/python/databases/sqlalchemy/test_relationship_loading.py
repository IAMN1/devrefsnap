from contextlib import contextmanager

import pytest
from sqlalchemy import event, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, contains_eager, joinedload, raiseload, selectinload

from demo_models import Post, User, new_engine
from demo_queries import seed


@contextmanager
def count_selects(engine):
    statements = []

    def before_cursor_execute(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


@pytest.fixture
def engine():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
        yield engine
    finally:
        engine.dispose()


@pytest.mark.parametrize("extra_users", [0, 3])
@pytest.mark.parametrize("strategy", ["lazy", "selectin", "joined"])
def test_same_collections_and_select_counts(engine, extra_users, strategy):
    with Session(engine) as session, session.begin():
        session.add_all([
            User(name=f"extra-{i}", email=f"extra-{i}@example.com")
            for i in range(extra_users)
        ])
    expected = {"alice": ["Python", "SQL"], "bob": []}
    expected.update({f"extra-{i}": [] for i in range(extra_users)})
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(User).order_by(User.id)
        if strategy == "selectin":
            stmt = stmt.options(selectinload(User.posts))
        elif strategy == "joined":
            stmt = stmt.options(joinedload(User.posts))
        result = session.scalars(stmt)
        if strategy == "joined":
            result = result.unique()
        users = result.all()
        actual = {user.name: sorted(post.title for post in user.posts) for user in users}
        assert actual == expected
    expected_count = {"lazy": 3 + extra_users, "selectin": 2, "joined": 1}[strategy]
    assert len(statements) == expected_count


def test_joined_collection_requires_unique(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).options(joinedload(User.posts)))
        with pytest.raises(InvalidRequestError, match="unique"):
            result.all()


@pytest.mark.parametrize("strategy, expected_count", [("lazy", 2), ("selectin", 2), ("joined", 1)])
def test_scalar_author_and_identity_map(engine, strategy, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(Post).order_by(Post.id)
        if strategy == "selectin":
            stmt = stmt.options(selectinload(Post.author))
        elif strategy == "joined":
            stmt = stmt.options(joinedload(Post.author))
        posts = session.scalars(stmt).all()
        assert [post.author.name for post in posts] == ["alice", "alice"]
        assert posts[0].author is posts[1].author
    assert len(statements) == expected_count


def test_joined_collection_sql_rows_repeat_parent(engine):
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # Connection возвращает строки SQL без сборки ORM-объектов и без unique().
    with engine.connect() as connection:
        rows = connection.execute(stmt).mappings().all()
    assert [row["name"] for row in rows] == ["alice", "alice", "bob"]
    assert len(rows) == 3


@pytest.mark.parametrize("loader, expected_count", [(selectinload, 2), (joinedload, 1)])
def test_parent_limit_keeps_full_collection(engine, loader, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(User).options(loader(User.posts)).order_by(User.id).limit(1)
        result = session.scalars(stmt)
        if loader is joinedload:
            result = result.unique()
        users = result.all()
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == ["Python", "SQL"]
    assert len(statements) == expected_count


def test_explicit_join_limit_counts_rows_before_unique(engine):
    with Session(engine) as session, session.begin():
        bob = session.scalar(select(User).where(User.name == "bob"))
        session.add(Post(title="Bob post", author=bob))
    stmt = (
        select(User).join(User.posts).options(selectinload(User.posts))
        .order_by(User.id, Post.id)
    )
    with Session(engine) as session:
        all_users = session.scalars(stmt).unique().all()
        assert {user.name: sorted(post.title for post in user.posts) for user in all_users} == {
            "alice": ["Python", "SQL"], "bob": ["Bob post"],
        }
    with Session(engine) as session:
        users = session.scalars(stmt.limit(2)).unique().all()
        # Лимит двух строк JOIN оставляет одного родителя с двумя постами.
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == ["Python", "SQL"]


@pytest.mark.parametrize("loader, expected_count", [(selectinload, 2), (joinedload, 1)])
def test_optional_scalar_keeps_parents(engine, loader, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(loader(User.manager)).order_by(User.id)
        ).all()
        assert [(user.name, user.manager.name if user.manager else None) for user in users] == [
            ("alice", None), ("bob", "alice"),
        ]
        assert users[1].manager is users[0]
    assert len(statements) == expected_count


def test_raiseload_allows_posts_and_rejects_other_relationships(engine):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(selectinload(User.posts), raiseload("*")).order_by(User.id)
        ).all()
        assert [len(user.posts) for user in users] == [2, 0]
        assert len(statements) == 2
        with pytest.raises(InvalidRequestError):
            _ = users[0].profile
        with pytest.raises(InvalidRequestError):
            _ = users[0].posts[0].comments
        assert len(statements) == 2


def test_nested_selectin_loads_comments_without_later_selects(engine):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(
                selectinload(User.posts).selectinload(Post.comments), raiseload("*")
            ).order_by(User.id)
        ).all()
        comments = sorted(
            comment.text for user in users for post in user.posts for comment in post.comments
        )
        assert comments == ["Useful"]
        assert len(statements) == 3


@pytest.mark.parametrize("partial, expected_titles, expected_count", [
    (False, ["Python", "SQL"], 2),
    (True, ["Python"], 1),
])
def test_filter_parents_and_choose_collection_content(engine, partial, expected_titles, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        option = contains_eager(User.posts) if partial else selectinload(User.posts)
        users = session.scalars(
            select(User).join(User.posts).where(Post.title == "Python")
            .options(option).order_by(User.id)
        ).unique().all()
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == expected_titles
    assert len(statements) == expected_count


def test_existing_collection_requires_explicit_refresh(engine):
    with Session(engine) as session:
        alice = session.scalar(
            select(User).where(User.name == "alice").options(selectinload(User.posts))
        )
        assert sorted(post.title for post in alice.posts) == ["Python", "SQL"]
        stmt = (
            select(User).join(User.posts).where(Post.title == "Python")
            .options(contains_eager(User.posts))
        )
        same = session.scalars(stmt).unique().one()
        assert same is alice
        assert sorted(post.title for post in same.posts) == ["Python", "SQL"]
        refreshed = session.scalars(stmt.execution_options(populate_existing=True)).unique().one()
        assert refreshed is alice
        assert [post.title for post in refreshed.posts] == ["Python"]
        alice_id = alice.id
        session.expire_all()
        assert session.get(User, alice_id) is alice
        assert sorted(post.title for post in alice.posts) == ["Python", "SQL"]


def test_eager_collection_is_available_after_session_close(engine):
    with Session(engine) as session:
        users = session.scalars(
            select(User).options(selectinload(User.posts)).order_by(User.id)
        ).all()
    assert [len(user.posts) for user in users] == [2, 0]
