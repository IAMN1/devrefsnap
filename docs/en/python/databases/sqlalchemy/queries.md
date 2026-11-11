<a id="запросы-join-и-выражения-sql"></a>
# Queries, JOINs, and SQL expressions

[Русский](../../../../ru/python/databases/sqlalchemy/queries.md)

Use this page to filter rows, join tables, or build a SQL expression.
The complete files use practice data from the shared schema. PostgreSQL examples are checked by compilation here.

[Reference](README.md) · [Shared schema](models-and-transactions.md#shared-schema-for-the-recipes)

| Task | Technique | Example |
| --- | --- | --- |
| Write SELECT/JOIN/CTE queries | select, aliased, func | [Complete query set](#select-join-subqueries-and-ctes) |
| Eliminate N+1 | Choose a loading strategy | [Relationship cards](relationship-loading.md) |
| Process many rows | yield_per and partitions | [Large result sets](streaming.md) |
| Check a PostgreSQL expression without a server | Compile with the selected dialect | [PostgreSQL](#postgresql-compilation-without-a-connection) |

**Level** — intermediate to advanced.
Prerequisites include SQL JOINs, aggregation, and Session.
Running the examples requires Python 3.14, SQLAlchemy 2.1.8, and pytest 9.2.0. SQLite comes with Python.
The files use `demo_models.py`.
Install `sqlalchemy[asyncio]` and `pytest` in a separate environment.

- [SELECT, JOIN, subqueries, and CTEs](#select-join-subqueries-and-ctes)
- [Check query results](#check-query-results)
- [Relationship loading](relationship-loading.md)
- [Large result sets](streaming.md)
- [PostgreSQL compilation without a connection](#postgresql-compilation-without-a-connection)

<a id="select-join-подзапросы-и-cte"></a>
## SELECT, JOIN, subqueries, and CTEs

The complete `demo_queries.py` creates a small dataset.
Call `seed()` once for each empty database.

[`sqlalchemy/demo_queries.py`](../../../../../examples/python/databases/sqlalchemy/demo_queries.py)

Run `python demo_queries.py`.
The result contains two authors and Alice's two posts.
Alice is set as Bob's manager.
The post counts are `2` and `0`.
The age groups have the values `adult` and `minor`.
Selecting multiple columns returns rows.
`scalars()` keeps the first column.
If you need all selected values, omit `scalars()`.

<a id="проверить-результаты-запросов"></a>
## Check query results

The complete `test_queries.py` checks the rows returned by `query_report()`.
Save the file next to `demo_models.py` and `demo_queries.py`.

[`sqlalchemy/test_queries.py`](../../../../../examples/python/databases/sqlalchemy/test_queries.py)

Run `python -m pytest -q test_queries.py`.
One test passes.
Each run creates a separate in-memory SQLite database.

<a id="загрузка-и-большие-выборки"></a>
## Loading and large result sets

For N+1 and loader selection, open the [relationship-loading cards](relationship-loading.md).
For incremental reading, open [large result sets](streaming.md).
The complete relationship checks are in [loading-lab.md](loading-lab.md).

<a id="postgresql-компиляция-без-подключения"></a>
## PostgreSQL compilation without a connection

**Level** — advanced.
The complete `demo_postgresql_sql.py` only compiles SQL.
The example does not connect to PostgreSQL.
Compilation does not verify locking, query plans, or execution.

[`sqlalchemy/demo_postgresql_sql.py`](../../../../../examples/python/databases/sqlalchemy/demo_postgresql_sql.py)

Run `python demo_postgresql_sql.py`.
The output contains `ON CONFLICT`, `FOR UPDATE`, a partial unique index, and an UPDATE with a CTE.
The UPSERT first creates an insert object.
The UPSERT then uses that object's `excluded` attribute.
Referencing `stmt` before assigning it is invalid.
Use a partial **unique index** to enforce conditional uniqueness in PostgreSQL. `UniqueConstraint(postgresql_where=...)` is invalid.
When executed against a database, these modifying queries change rows or the schema.
A lock exists only within a live transaction in the corresponding database system.

Sources include [PostgreSQL ON CONFLICT and indexes](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html) and [SQL expressions](https://docs.sqlalchemy.org/en/21/core/selectable.html).
