<a id="миграция-схемы-и-конкуренция-sqlite"></a>
# SQLite schema migration and concurrency

[Русский](../../../../ru/databases/relational/sqlite/backup-and-migrations.md)

Use this page to rebuild a table with a known schema or diagnose WAL and locking.
For backups and recovery, see the [separate reference](backup-and-restore.md).
[SQLite](README.md).

| Task | Technique | Example |
| --- | --- | --- |
| Add a constraint by rebuilding a table | Transaction, data copy, dependency recreation | [Complete example](#rebuild-a-table-with-a-known-schema) |
| Make and verify a backup | Backup API or CLI | [Backup and restore](backup-and-restore.md) |
| Diagnose SQLITE_BUSY and WAL behavior | Short transactions and a checkpoint plan | [Concurrency](#concurrency-and-wal) |

| Item | Details |
| --- | --- |
| Level | Advanced |
| Prerequisites | Python 3.14 with SQLite 3.37 or later, plus familiarity with foreign keys and transactions |

<a id="полный-пример-перестроение-таблицы"></a>

<a id="перестроить-известную-таблицу"></a>
## Rebuild a table with a known schema

Use this approach when your version of ALTER TABLE lacks the required change or you need to rebuild a known schema.
A rebuild can remove dependencies. First obtain a [verified backup](backup-and-restore.md#verify-the-restored-database).
In the [complete program](migration-lab.md#complete-example-of-a-table-rebuild), `users` already contains `alice`, an index, and a trigger.
The `posts` table references `users`.

The outline shows the program steps.

```text
Before: users(id, username NOT NULL) accepts an empty name
Change: record dependencies → create users_new with CHECK(username <> '')
Transaction: copy rows → replace users → recreate the index and trigger
Before COMMIT: check foreign_key_check
After commit: enable foreign keys outside a transaction → check the data, the trigger, and rejection by CHECK
```

The rebuilt table preserves rows and relationships and rejects empty names.
The complete program creates its own temporary database and rolls back if the migration fails.
For an arbitrary schema, inspect views and other dependencies as well.

SQLite 3.53.0 and later also support changes to NOT NULL and CHECK through ALTER TABLE.
Check [support for your version](https://www.sqlite.org/lang_altertable.html) before making those changes.
The rebuild in the complete example shows a general approach for changes your version cannot make directly.
[Complete code, setup, and checks](migration-lab.md#complete-example-of-a-table-rebuild).

<a id="конкуренция-и-wal"></a>
## Concurrency and WAL

**Advanced.** SQLite allows multiple readers and one writer.
BEGIN IMMEDIATE acquires the write lock at the start of the transaction.
Under contention, BEGIN IMMEDIATE can return SQLITE_BUSY.
Keep transactions short.
Keep network waits outside transactions.
A timeout or busy handler controls how long SQLite waits.
The one-writer limit still applies.

WAL usually allows readers to work concurrently with a writer.
WAL requires a compatible filesystem and checkpointing.
Check filesystem requirements before sharing a WAL database over a network.
Long reads can delay checkpoints and cause the WAL to grow.
Monitor transaction duration and file sizes.
The synchronous setting affects durability during failures and performance.
Choose a mode based on your data requirements.

`PRAGMA journal_mode=WAL` changes the database file's journal mode.
The setting persists across connections.
The active `-wal` file can contain important data. Do not copy only the main file of an active database.
Leave an active `-wal` file in place.
Use the backup API or SQLite's own commands to obtain a consistent backup while the database is active.
`PRAGMA integrity_check` checks the database structure.
`PRAGMA foreign_key_check` checks references.
Run each check independently.

<a id="источники"></a>
## Sources

- [Schema changes](https://www.sqlite.org/lang_altertable.html), [transactions](https://www.sqlite.org/lang_transaction.html), [foreign_keys](https://www.sqlite.org/pragma.html#pragma_foreign_keys).
- [WAL](https://www.sqlite.org/wal.html), [integrity_check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign_key_check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check).
- [3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html).
