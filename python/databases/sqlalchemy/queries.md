# Запросы, JOIN и выражения SQL

[Справочник](README.md) · [Общая схема](models-and-transactions.md#единая-схема-для-рецептов)

| Задача | Приём | Пример |
| --- | --- | --- |
| Написать SELECT/JOIN/CTE | select, aliased, func | [Полный набор запросов](#select-join-подзапросы-и-cte) |
| Устранить N+1 | Выбрать стратегию загрузки | [Карточки отношений](relationship-loading.md) |
| Обработать много строк | yield_per и partitions | [Большие выборки](streaming.md) |
| Проверить PostgreSQL-выражение без сервера | Компиляция выбранным диалектом | [PostgreSQL](#postgresql-компиляция-без-подключения) |

**Уровень:** средний → продвинутый.
Предпосылки: SQL JOIN/агрегация и Session.
Сверено 2026-11-06 с SQLAlchemy 2.1.
Выполнено 2026-11-06: один тест результатов SQLite и компиляция четырёх выражений PostgreSQL.
Загрузка отношений и пакетная обработка проверены на связанных страницах.
Окружение: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0.
Файлы используют `demo_models.py`.
Установите `sqlalchemy[asyncio]` и `pytest` в отдельное окружение.
PostgreSQL не запускался.

- [SELECT, JOIN, подзапросы и CTE](#select-join-подзапросы-и-cte)
- [Проверки результатов](#проверить-результаты-запросов)
- [Загрузка отношений](relationship-loading.md)
- [Большие выборки](streaming.md)
- [PostgreSQL: компиляция без подключения](#postgresql-компиляция-без-подключения)

## SELECT, JOIN, подзапросы и CTE

Полный пример `demo_queries.py` создаёт небольшой набор данных.
Вызывайте `seed()` один раз для каждой пустой базы.

<!-- example: sqlalchemy/demo_queries.py -->
```python
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
```

Запустите `python demo_queries.py`.
Результат содержит двух авторов и два поста Alice.
У Bob руководителем указана Alice.
Количества постов равны `2` и `0`.
Возрастные группы имеют значения `adult`/`minor`.
Выбор нескольких колонок возвращает строки.
`scalars()` оставляет первую колонку.
Если нужны все выбранные значения, не применяйте `scalars()`.

## Проверить результаты запросов

Полный `test_queries.py` проверяет строки, возвращаемые `query_report()`.
Сохраните файл рядом с `demo_models.py` и `demo_queries.py`.

<!-- example: sqlalchemy/test_queries.py -->
```python
from sqlalchemy.orm import Session

from demo_models import new_engine
from demo_queries import query_report, seed


def test_query_results():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
            report = query_report(session)
            assert report["adults"] == ["alice"]
            assert report["joined"] == [("alice", "Python"), ("alice", "SQL")]
            assert report["outer"] == [("alice", "Python"), ("alice", "SQL"), ("bob", None)]
            assert report["managers"] == [("bob", "alice")]
            assert report["counts"] == [("alice", 2), ("bob", 0)]
            assert report["cte"] == report["union"] == ["alice", "bob"]
            assert report["commented"] == report["from_subquery"] == report["exists"] == ["alice"]
            assert report["age_group"] == [("alice", "adult"), ("bob", "minor")]
            assert report["groups"] == [(True, 2, 23.5)]
    finally:
        engine.dispose()

```

Запустите `python -m pytest -q test_queries.py`.
Результат: один тест проходит.
Каждый запуск создаёт отдельную SQLite в памяти.

## Загрузка и большие выборки

Для N+1 и выбора loader откройте [карточки загрузки отношений](relationship-loading.md).
Для чтения по частям откройте [большие выборки](streaming.md).
Полные проверки отношений находятся в [loading-lab.md](loading-lab.md).
Эти задачи вынесены отдельно, чтобы примеры SELECT не мешали выбору загрузки.

## PostgreSQL: компиляция без подключения

**Уровень:** продвинутый.
Полный пример `demo_postgresql_sql.py` только компилирует SQL.
Пример не подключается к PostgreSQL.
Компиляция не подтверждает блокировки, планы или выполнение.

<!-- example: sqlalchemy/demo_postgresql_sql.py -->
```python
from sqlalchemy import Boolean, Column, Index, Integer, MetaData, String, Table, func, select, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.schema import CreateIndex

accounts = Table(
    "accounts", MetaData(),
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("email", String),
    Column("active", Boolean),
)


def statements():
    insert_stmt = insert(accounts).values(name="alice", email="alice@example.com", active=True)
    upsert = insert_stmt.on_conflict_do_update(
        index_elements=[accounts.c.name], set_={"email": insert_stmt.excluded.email},
    )
    locked = select(accounts).where(accounts.c.id == 1).with_for_update()
    partial = Index("uq_active_email", accounts.c.email, unique=True, postgresql_where=accounts.c.active.is_(True))
    cte = select(accounts.c.id, func.concat(accounts.c.name, "_new").label("new_name")).where(accounts.c.active.is_(True)).cte("renames")
    batch_update = update(accounts).where(accounts.c.id == cte.c.id).values(name=cte.c.new_name)
    dialect = postgresql.dialect()
    return {"upsert": str(upsert.compile(dialect=dialect)),
            "lock": str(locked.compile(dialect=dialect)),
            "partial_index": str(CreateIndex(partial).compile(dialect=dialect)),
            "cte_update": str(batch_update.compile(dialect=dialect))}


if __name__ == "__main__":
    for name, sql in statements().items():
        print(name, sql)
```

Запустите `python demo_postgresql_sql.py`.
Вывод содержит `ON CONFLICT`, `FOR UPDATE`, частичный уникальный индекс и UPDATE с CTE.
UPSERT сначала создаёт insert-объект.
Затем UPSERT использует `excluded` этого объекта.
Ссылка на ещё не присвоенный `stmt` неверна.
Условная уникальность PostgreSQL реализуется частичным **уникальным индексом**, а не `UniqueConstraint(postgresql_where=...)`.
При реальном выполнении эти изменяющие запросы обновят строки или схему.
Блокировка существует только в живой транзакции соответствующей СУБД.
PostgreSQL здесь не запускался.

Источники: [PostgreSQL ON CONFLICT и индексы](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html), [SQL выражения](https://docs.sqlalchemy.org/en/21/core/selectable.html).
