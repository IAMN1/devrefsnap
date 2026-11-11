from time import perf_counter

from sqlalchemy import event, select
from sqlalchemy.orm import Session

from demo_models import User, new_engine


def run():
    engine = new_engine()
    elapsed, commits, inserts = [], [], []

    def before_sql(conn, cursor, statement, parameters, context, executemany):
        context.training_started = perf_counter()

    def after_sql(conn, cursor, statement, parameters, context, executemany):
        elapsed.append(perf_counter() - context.training_started)

    def after_commit(session):
        commits.append("committed")

    def before_insert(mapper, connection, target):
        target.name = target.name.strip()
        inserts.append(target.name)

    listeners = [(engine, "before_cursor_execute", before_sql), (engine, "after_cursor_execute", after_sql),
                 (Session, "after_commit", after_commit), (User, "before_insert", before_insert)]
    for target, name, callback in listeners:
        event.listen(target, name, callback)
    try:
        with Session(engine) as session, session.begin():
            session.add(User(name=" alice ", email="alice@example.com"))
        with Session(engine) as session:
            name = session.scalar(select(User.name))
        return name, commits, inserts, elapsed
    finally:
        for target, name, callback in listeners:
            event.remove(target, name, callback)
        engine.dispose()
