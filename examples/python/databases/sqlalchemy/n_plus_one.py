from sqlalchemy import ForeignKey, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship(back_populates="posts")


def read_users(engine, *, eager=False):
    statements = []

    def count_select(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", count_select)
    try:
        with Session(engine) as session:
            stmt = select(User).order_by(User.id)
            if eager:
                stmt = stmt.options(selectinload(User.posts))
            users = session.scalars(stmt).all()
            rows = [(user.name, sorted(post.title for post in user.posts)) for user in users]
        return rows, len(statements)
    finally:
        event.remove(engine, "before_cursor_execute", count_select)


def main():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            session.add_all([
                User(name="alice", posts=[Post(title="Python"), Post(title="SQL")]),
                User(name="bob", posts=[]),
            ])

        expected = [("alice", ["Python", "SQL"]), ("bob", [])]
        lazy_rows, lazy_count = read_users(engine)
        eager_rows, eager_count = read_users(engine, eager=True)
        assert lazy_rows == eager_rows == expected
        assert lazy_count == 3
        assert eager_count == 2
        print(f"lazy: {lazy_count} SELECT; {lazy_rows}")
        print(f"selectinload: {eager_count} SELECT; {eager_rows}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
