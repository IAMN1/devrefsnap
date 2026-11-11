
# SQLite

[Русский](../../../../ru/databases/relational/sqlite/README.md)

SQLite is an embedded relational database.
The application uses the SQLite library directly without a separate server.
A database file works well for local applications, tests, and embedded storage.
Consider write concurrency separately.

[Databases](../../README.md) · [General SQL](../../sql/README.md) · [PostgreSQL](../postgresql/README.md)

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Command or API | Where to look |
| --- | --- | --- |
| Connect and perform CRUD | sqlite3.connect, execute, parameters | [Short example](python-and-queries.md#pass-a-value-as-a-parameter) · [Complete blog example](query-lab.md#complete-in-memory-blog-example) |
| Enable foreign keys | PRAGMA foreign_keys=ON | [Schema and foreign key check](query-lab.md#complete-in-memory-blog-example) |
| Choose a type | Affinity or STRICT | [Types and functions](python-and-queries.md#types-functions-and-indexes) |
| Inspect tables in the CLI | .tables / .schema | [CLI](python-and-queries.md#cli-and-other-languages) |
| Make a consistent backup | Connection.backup / .backup | [Python](backup-and-restore.md#back-up-with-python) · [CLI](backup-and-restore.md#back-up-with-the-cli) |
| Restore and verify a backup | New file, integrity and foreign key checks, data | [Restore](backup-and-restore.md#restore-a-backup-to-a-new-file) · [Verification](backup-and-restore.md#verify-the-restored-database) |
| Change a schema while preserving relationships | Transaction and table rebuild | [Migration](backup-and-migrations.md#полный-пример-перестроение-таблицы) |
| Diagnose SQLITE_BUSY or WAL behavior | BEGIN IMMEDIATE, timeout, checkpoint | [Concurrency](backup-and-migrations.md#concurrency-and-wal) |

| Item | Details |
| --- | --- |
| Python examples | Python 3.14 with the built-in sqlite3 module. Shell commands require the sqlite3 CLI and Bash. |
| API requirements | STRICT requires SQLite 3.37 or later. RETURNING requires SQLite 3.35 or later. |
| Environment | Check build options and driver behavior separately from the installed CLI |

<a id="базовый-уровень"></a>

<a id="подключиться-и-выбрать-тип-данных"></a>
## Connect and choose a data type

Start with the [complete Python example](query-lab.md#complete-in-memory-blog-example).
It creates users, posts, and comments, runs a JOIN, and checks that SQLite rejects an invalid foreign key.
`INTEGER PRIMARY KEY` usually generates the rowid automatically.
Use AUTOINCREMENT when previously assigned rowids must never be reused.
AUTOINCREMENT adds overhead.

SQLite stores values as NULL, INTEGER, REAL, TEXT, or BLOB.
BOOLEAN, DATETIME, and JSON have no separate built-in storage classes.
The column declaration determines affinity.
Use STRICT for stricter type checks. STRICT accepts a limited set of type names.

<a id="средний-уровень"></a>

<a id="обеспечить-ограничения-и-транзакции"></a>
## Enforce constraints and use transactions

Use [parameterized queries, RETURNING, indexes, and explicit transaction control](python-and-queries.md).
Enable foreign key enforcement for each connection **before** starting a transaction.
`CHECK(age >= 0)` allows NULL.
Add NOT NULL if the value is required.
Express complex constraints in the schema so the database enforces them independently of the application interface.

<a id="продвинутый-уровень"></a>

<a id="учесть-wal-и-восстановление"></a>
## Account for WAL and recovery

See [backup and restore](backup-and-restore.md) for recovery and [migration and WAL](backup-and-migrations.md) for schema changes and concurrency.
WAL often allows readers to work while a writer is active.
SQLite still allows only one writer at a time.
An open database can use `-wal` and `-shm` files.
Use the backup API or SQLite's own tools to obtain a consistent copy. The main file alone can omit data.

<a id="частые-ошибки"></a>
## Common mistakes

| Symptom | Cause or action |
| --- | --- |
| Foreign key enforcement or CASCADE has no effect | Check PRAGMA foreign_keys on each connection outside a transaction |
| A numeric column accepts a string | Ordinary affinity is flexible. Consider STRICT and CHECK. |
| database is locked | Keep transactions short and limit wait time. A timeout only controls how long SQLite waits. |
| DELETE ... LIMIT gives a syntax error | This requires SQLITE_ENABLE_UPDATE_DELETE_LIMIT. A portable option uses a subquery to select IDs with LIMIT. |
| .tables fails in execute | Run dot commands in the CLI. Dot commands lack inline comment syntax. |
| Expecting `with connection` to close the database | The context manager controls transactions. Close the connection with close or closing. |
| Indexes or triggers disappear after migration | Preserve and recreate them when rebuilding the table |

<a id="источники"></a>
## Sources

- [About SQLite](https://www.sqlite.org/about.html), [data types](https://www.sqlite.org/datatype3.html), [STRICT](https://www.sqlite.org/stricttables.html).
- [Foreign keys](https://www.sqlite.org/foreignkeys.html), [AUTOINCREMENT](https://www.sqlite.org/autoinc.html), [DELETE LIMIT](https://www.sqlite.org/lang_delete.html#optional_limit_and_order_by_clauses).
- [Python 3.14 sqlite3](https://docs.python.org/3.14/library/sqlite3.html), [SQLite version history](https://www.sqlite.org/changes.html).
