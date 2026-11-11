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
