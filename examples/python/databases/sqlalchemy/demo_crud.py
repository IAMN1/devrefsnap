from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from demo_models import User, new_engine


def run():
    engine = new_engine()
    try:
        with Session(engine) as session:
            with session.begin():
                user = User(name="alice", email="alice@example.com", age=30)
                session.add(user)
                session.flush()
                user_id = user.id
            with session.begin():
                row = session.get(User, user_id)
                row.full_name = "Alice Doe"
                session.execute(update(User).where(User.id == user_id).values(age=31))
                new_id = session.scalar(insert(User).values(name="bob", email="bob@example.com").returning(User.id))
            with session.begin():
                names = session.scalars(select(User.name).order_by(User.id)).all()
                session.execute(delete(User).where(User.id == new_id))
            return names
    finally:
        engine.dispose()


if __name__ == "__main__":
    print(run())
