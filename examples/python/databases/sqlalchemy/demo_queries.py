from sqlalchemy import and_, bindparam, case, func, or_, select
from sqlalchemy.orm import Session, aliased

from demo_models import Comment, Post, User, new_engine


def seed(session: Session):
    alice = User(name="alice", email="alice@example.com", age=30)
    alice.posts = [Post(title="Python", comments=[Comment(text="Useful")]), Post(title="SQL")]
    bob = User(name="bob", email="bob@example.com", age=17, manager=alice)
    session.add_all([alice, bob])
    session.flush()
    return alice.id, bob.id


def query_report(session: Session):
    manager = aliased(User)
    count_posts = select(func.count(Post.id)).where(Post.user_id == User.id).scalar_subquery()
    active_users = select(User.name).where(User.is_active.is_(True)).cte("active_users")
    python_posts = aliased(Post, select(Post).where(Post.title == "Python").subquery())
    age_group = case((User.age < 18, "minor"), else_="adult")
    named = select(User.name).where(User.id == bindparam("uid"))
    return {
        "adults": session.scalars(select(User.name).where(and_(User.age >= 18, or_(User.name == "alice", User.name == "carol"))).order_by(User.name).limit(10).offset(0)).all(),
        "joined": list(session.execute(select(User.name, Post.title).join(User.posts).order_by(Post.title))),
        "outer": list(session.execute(select(User.name, Post.title).outerjoin(User.posts).order_by(User.name, Post.title))),
        "commented": session.scalars(select(User.name).join(User.posts).join(Post.comments).distinct()).all(),
        "managers": list(session.execute(select(User.name, manager.name).join(manager, User.manager_id == manager.id))),
        "counts": list(session.execute(select(User.name, count_posts).order_by(User.name))),
        "from_subquery": session.scalars(select(User.name).join(python_posts, python_posts.user_id == User.id)).all(),
        "cte": session.scalars(select(active_users.c.name).order_by(active_users.c.name)).all(),
        "groups": list(session.execute(select(User.is_active, func.count(User.id), func.avg(User.age)).group_by(User.is_active))),
        "age_group": list(session.execute(select(User.name, age_group).order_by(User.name))),
        "union": session.scalars(select(User.name).where(User.age < 18).union(select(User.name).where(User.age >= 18)).order_by("name")).all(),
        "exists": session.scalars(select(User.name).where(select(1).where(Post.user_id == User.id).exists())).all(),
        "parameter": session.scalar(named, {"uid": 1}),
    }


if __name__ == "__main__":
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
            print(query_report(session))
    finally:
        engine.dispose()
