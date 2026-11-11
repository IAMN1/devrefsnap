<a id="подготовить-учебную-базу-postgresql"></a>
# Set up a PostgreSQL practice database

[Русский](../../../../ru/databases/relational/postgresql/query-lab.md)

This example creates users, products, and orders for the PostgreSQL reference.
It creates a new `cheatsheet_demo` database on a separate server.
[Query examples](queries.md) · [PostgreSQL](README.md).

Use PostgreSQL 18, `createdb`, `psql`, and a role that can create the practice database.

<a id="полный-пример-учебная-база"></a>
## Complete practice database example

Prepare a separate practice server or cluster.
The shell commands below target a local server with the `postgres` role.
Adjust the address and role for your installation.
Enter the password when prompted or use a configured password file.

Save [`queries.sql`](../../../../../examples/databases/relational/postgresql/queries.sql) in the current directory.
Run the shell commands.
The first creates a new database.
If the name already exists, it fails and leaves existing data intact.

```bash
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_demo && \
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --no-psqlrc --set=ON_ERROR_STOP=1 --file=queries.sql
```

The complete example uses the PostgreSQL 18 dialect.
It creates a persistent `demo` schema and data in one transaction.
Running it again in the same database stops at the existing schema.
The script keeps existing objects intact.

[`queries.sql`](../../../../../examples/databases/relational/postgresql/queries.sql)

Expect totals of `alice | 140.00`, `bob | 300.00`, and `carol | 0`.
`RETURNING` returns `Keyboard | 9`.
`rollback_ok` is `t`.
After COMMIT, the original stock is `10`.
The orders are practice records. A complete sales workflow would also need inventory deduction.

Run the [query examples](queries.md) in `cheatsheet_demo` after this setup.
The explicit `demo` schema keeps the result independent of `search_path`.

<a id="источники"></a>
## Sources

- [INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html), [UPDATE](https://www.postgresql.org/docs/18/sql-update.html), [DELETE](https://www.postgresql.org/docs/18/sql-delete.html).
- [Joins and grouping](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTEs and recursion](https://www.postgresql.org/docs/18/queries-with.html).
- [Window functions](https://www.postgresql.org/docs/18/functions-window.html), [window frames](https://www.postgresql.org/docs/18/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).
- [String functions](https://www.postgresql.org/docs/18/functions-string.html), [math](https://www.postgresql.org/docs/18/functions-math.html), [dates and times](https://www.postgresql.org/docs/18/functions-datetime.html).
