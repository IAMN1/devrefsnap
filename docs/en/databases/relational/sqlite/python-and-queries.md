<a id="подключение-схема-и-запросы-sqlite"></a>
# SQLite connections, schemas, and queries

[Русский](../../../../ru/databases/relational/sqlite/python-and-queries.md)

Use this page to connect to SQLite from Python, bind parameters, design a schema, or run queries.
The short example runs in memory. Type and transaction behavior depend on the library version.

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Select rows using a user-supplied value | execute parameters | [Short example](#pass-a-value-as-a-parameter) |
| Check relationships and rollback on a prepared schema | Foreign keys, STRICT, and an explicit SQL transaction | [Complete blog example](query-lab.md#complete-in-memory-blog-example) |
| Choose a type or inspect an index | Affinity, STRICT, functions, and query plans | [Types and functions](#types-functions-and-indexes) |
| Group several changes | autocommit and explicit BEGIN or ROLLBACK | [Transactions](#manage-a-transaction-in-the-application) |
| Inspect a database in a terminal or another language | CLI or a driver for that language | [Connections](#cli-and-other-languages) |

[SQLite](README.md)

| Item | Details |
| --- | --- |
| Levels | Basic for connections and CRUD. Intermediate for constraints, indexes, and transactions. |
| Prerequisites | Python 3.14 with built-in sqlite3. SQLite 3.37 or later for STRICT. |

<a id="полный-пример-блог-в-памяти"></a>

<a id="передать-значение-параметром"></a>
## Pass a value as a parameter

Bind user-supplied values as parameters to keep them out of the SQL text.
This complete Python 3.14 example uses only the standard library.
Save it as `lookup.py` and run `python3.14 lookup.py`.

```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:", autocommit=True)) as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL)")
    db.execute("INSERT INTO users VALUES (?, ?)", (1, "alice"))
    rows = db.execute("SELECT id FROM users WHERE username = ?", ("alice",)).fetchall()
    print(rows)
```

The result is `[(1,)]`. The database stays in memory.
Bind values through parameters. Select table and column names through a separate, controlled mechanism.
Use `closing` to close the connection. `with db:` alone manages the transaction.
[Complete blog setup and checks for JOIN, foreign keys, STRICT, RETURNING, CASCADE, and rollback](query-lab.md#complete-in-memory-blog-example).

<a id="типы-функции-и-индексы"></a>
## Types, functions, and indexes

**Intermediate.** SQLite storage classes are NULL, INTEGER, REAL, TEXT, and BLOB.
Column affinity specifies the preferred conversion for values.
STRICT accepts INT, INTEGER, REAL, TEXT, BLOB, and ANY.
BOOLEAN, DATETIME, and JSON are outside the supported set of STRICT type names.
Store Boolean values as 0 or 1 with a CHECK constraint.
Store timestamps in a consistent UTC text format or as a number.
Store JSON as TEXT with suitable validation.
REAL uses a binary approximation, so it cannot provide fixed-point decimal arithmetic.

Run this standalone SQLite snippet without creating tables.

```sql
SELECT substr('Hello', 2, 3) AS part,
       round(3.14159, 2) AS rounded,
       date('2026-11-06', '+1 day') AS tomorrow,
       json_extract('{"name":"Ada"}', '$.name') AS name;
```

The result is `ell | 3.14 | 2026-11-07 | Ada`.
Your SQLite build must provide the JSON functions.
Other functions and expressions include the following.

- Strings — LENGTH, LOWER, UPPER, TRIM, and REPLACE.
- Numbers — ABS and RANDOM.
- Aggregation — COUNT, SUM, AVG, MIN, and MAX.
- Conditions and NULL — CASE, COALESCE, NULLIF, and IFNULL.
- Dates and times — DATE, TIME, DATETIME, and STRFTIME.

`'now'` returns UTC unless you apply localtime.
Check time conversions and ambiguous month shifts on your data.

Use these individual SQL statements as a reference for an existing schema.

```text
PRAGMA table_info(users);
PRAGMA index_list(users);
PRAGMA index_info(posts_user_created_idx);
SELECT name, sql FROM sqlite_schema WHERE type = 'index';
EXPLAIN QUERY PLAN SELECT * FROM posts WHERE user_id = 1;
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users RENAME COLUMN phone TO phone_number;
ALTER TABLE users DROP COLUMN phone_number;
```

PRIMARY KEY and UNIQUE already enforce uniqueness.
Avoid duplicate indexes unless you have a specific reason to add one.
The planner uses the composite or partial index from the complete example only if the index improves the plan.
SQLite added DROP COLUMN in 3.35.0, with restrictions on dependencies.
Check ALTER TABLE support for the change you need.
When committed, DROP TABLE removes the table and its data.
DELETE without WHERE deletes all rows.
Where DELETE LIMIT is unavailable, select IDs in a subquery:
`WHERE id IN (SELECT id FROM users WHERE ... ORDER BY id LIMIT 10)`.

<a id="транзакция-в-приложении"></a>
## Manage a transaction in the application

**Intermediate.** The complete example sets autocommit=True.
Use SQL COMMIT and ROLLBACK to control the transaction in this mode. db.commit() and db.rollback() have no effect.
With autocommit=False, Python keeps a transaction open and those methods behave differently.
Choose the transaction mode explicitly.
`with db:` leaves the connection open and does not create a nested SAVEPOINT.
Use an explicit SAVEPOINT for partial rollback.
In legacy transaction mode, `executescript` has its own commit behavior.

For several related changes, start a transaction with BEGIN.
Run all statements.
On success, run COMMIT.
On exception, run ROLLBACK.
Then re-raise the exception with `raise`.
BEGIN IMMEDIATE requests the write lock at the start.
If another writer is active, SQLite may wait or return SQLITE_BUSY.
EXCLUSIVE behaves differently in rollback journal mode and WAL mode.
Use EXCLUSIVE based on its locking behavior for your mode.

<a id="cli-и-другие-языки"></a>
## CLI and other languages

**Basic.** Run the following commands in your shell.
`sqlite3 database.db` opens or creates the database file.
`sqlite3 -readonly existing.db` opens an existing file in read-only mode.
`sqlite3 -bail database.db < script.sql` runs a script and stops on error.
Enter the following commands one at a time inside the CLI.

```text
.help
.tables
.schema users
.headers on
.mode column
.output results.txt
.output
.quit
```

.output redirects results to a file.
Without an argument, .output restores stdout.
For CSV, set `.mode csv`.
Then run `.import file.csv table_name`, accounting for headers and the existing schema.
Enter dot commands without inline comments.
Run dot commands in the CLI and SQL statements through Connection.execute.

In other languages, use a suitable driver and close the connection when finished.

- [Node.js node:sqlite](https://nodejs.org/api/sqlite.html) is a built-in API in supported Node versions.
  The npm sqlite3 package exposes a different API. Use the documentation for the API you choose.
- [Xerial SQLite JDBC](https://github.com/xerial/sqlite-jdbc) provides the driver for `jdbc:sqlite:...`. Install the driver before using DriverManager.
- [Microsoft.Data.Sqlite](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/) provides SqliteConnection. Dispose of the connection with using.

These drivers may use a different SQLite version from Python or the CLI.

<a id="источники"></a>
## Sources

- [Python sqlite3 transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [functions](https://www.sqlite.org/lang_corefunc.html), [dates](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [indexes](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
- [SQLite 3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html).
