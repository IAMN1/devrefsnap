<a id="подготовить-блог-sqlite-и-проверить-запросы"></a>
# Set up a SQLite blog and verify its queries

[Русский](../../../../ru/databases/relational/sqlite/query-lab.md)

This example checks joins, parameters, constraints, cascading deletes, and rollback.
The database exists only in memory, so the example leaves user files untouched.
[Query examples](python-and-queries.md) · [SQLite](README.md).

Use Python 3.14 with the built-in sqlite3 module and SQLite 3.37 or later for STRICT.

<a id="полный-пример-блог-в-памяти"></a>
## Complete in-memory blog example

Save the code as `demo.py`.
Run `python3.14 demo.py`.
The example uses only the standard library.
It explicitly sets autocommit=True.
The SQL commands BEGIN, COMMIT, and ROLLBACK control the transaction.

[`sqlite/demo.py`](../../../../../examples/databases/relational/sqlite/demo.py)

The example verifies a successful JOIN.
It checks that SQLite rejects an unknown user and an invalid type.
It also checks a cascading delete and verifies that rollback fully reverses it.
Read the RETURNING result before committing.
`last_insert_rowid()` and cursor.lastrowid refer to the last applicable insert on the connection.
RETURNING often makes the relationship between the ID and the statement clearer.

<a id="источники"></a>
## Sources

- [Python sqlite3 transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [functions](https://www.sqlite.org/lang_corefunc.html), [dates](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [indexes](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
- [SQLite 3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html).
