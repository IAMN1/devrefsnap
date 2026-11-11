<a id="создать-копию-sqlite-и-проверить-восстановление"></a>
# Back up SQLite and verify the restore

[Русский](../../../../ru/databases/relational/sqlite/backup-and-restore.md)

Choose the backup API or CLI, restore the backup to a new file, and check the result.
See [schema migration](backup-and-migrations.md) for changes to a schema.
[SQLite reference](README.md).

<a id="быстрый-поиск"></a>
## Quick reference

| Situation | Choice | Reference or example |
| --- | --- | --- |
| Back up from Python | `Connection.backup()` | [Python backup](#back-up-with-python) |
| Back up from the terminal | `.backup` | [CLI backup](#back-up-with-the-cli) |
| Restore a working database from a binary backup | Backup API or `.restore` to a new file | [Restore a backup](#restore-a-backup-to-a-new-file) |
| Get SQL for inspection or transfer | `.dump` → new file → CLI | [SQL dump](#create-and-restore-a-sql-dump) |
| Verify a restored file | Check data, integrity, foreign keys, and behavior | [Check the result](#verify-the-restored-database) |
| Back up a database that uses WAL | Make a consistent copy with the API or CLI | [WAL limitations](#account-for-wal-and-backup-scope) |
| Make a compact copy | `VACUUM INTO` | [Limitations and documentation](#account-for-wal-and-backup-scope) |

| Item | Details |
| --- | --- |
| Level | Intermediate. WAL limitations are advanced. |
| Prerequisites | Python 3.14 with sqlite3 for Python examples. The CLI examples require sqlite3 and Bash. The practice schema uses STRICT, available since SQLite 3.37. |

<a id="выбрать-вид-копии"></a>
## Choose a backup format

| Requirement | Technique | Result or limitation |
| --- | --- | --- |
| Consistent copy of one database | Backup API or `.backup` | SQLite file. An existing destination can be overwritten. |
| Readable SQL | `.dump` | Executable SQL for a logical backup |
| Smallest copy | `VACUUM INTO` | Compact file. Check the limitations of `VACUUM INTO`. |
| All application data | Plan what to include | Back up separate databases and external files explicitly |

Check that the source database exists.
A plain `sqlite3.connect()` can create an empty database if you mistype the path.
The read examples below open the source in read-only mode.
Choose a new destination name separate from the live database.
If a backup fails, treat any remaining destination file as incomplete.

<a id="создать-копию-через-python"></a>
## Back up with Python

Copy an existing `source.db` to a new `backup.db`.
Run this Python 3.14 snippet in the directory with the practice source database.

```python
import sqlite3
from contextlib import closing
from pathlib import Path

source_path = Path("source.db").resolve()
target_path = Path("backup.db")
with closing(sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True, autocommit=True)) as source:
    target_path.touch(exist_ok=False)
    with closing(sqlite3.connect(target_path, autocommit=True)) as target:
        source.backup(target)
```

`backup.db` contains a consistent copy of `main` from the source connection.
If the destination already exists, the snippet raises `FileExistsError` before writing to it.
If the source is missing, the read-only connection fails before creating the destination.
Without the setup in this snippet, `backup()` can overwrite an existing destination database.
If the attempt fails, decide separately how to retry or remove the destination file.

To monitor progress, use the `progress` callback on `backup()`.
The `pages` parameter sets the number of pages per step.
[Complete backup, restore, and failure checks](backup-lab.md#verify-the-backup-api)

<a id="создать-копию-через-cli"></a>
## Back up with the CLI

Use this Bash snippet to back up a SQLite file from the terminal.
It requires an existing `source.db` and an unused `backup.db` path.

```bash
( set -C; : > backup.db ) && \
sqlite3 -init /dev/null -batch -bail -readonly source.db ".backup backup.db"
```

`.backup` writes the backup into the empty file created in advance.
`set -C` prevents shell redirection from overwriting an existing destination.
If the destination already exists, the shell skips the command after `&&`.
If reading the source or backing up fails, the empty file may remain.

The quoted `.backup` is a CLI dot command.
Without the destination check, `.backup` can overwrite an existing database.
In the help syntax `.backup ?DB? FILE`, `?DB?` is an optional database name.
This syntax has no progress flag.
`-init /dev/null` skips the user's CLI startup file for the example.

[Complete CLI example](backup-lab.md#verify-a-cli-backup-and-sql-dump)

<a id="восстановить-копию-в-новый-файл"></a>
## Restore a backup to a new file

To verify a binary `backup.db` while preserving the source, restore it to a separate working database.
A binary backup is already a SQLite database file.

| Environment | Choice | Effect |
| --- | --- | --- |
| Python | Open the backup read-only and call `backup()` with a new destination | Use the same [snippet](#back-up-with-python) with `backup.db` as the source and `restored.db` as the destination |
| CLI | Run `.restore backup.db` into a new destination | Replaces the destination database contents. Keep the live file separate. |

This Bash snippet checks that the destination name is available.

```bash
( set -C; : > restored.db ) && \
sqlite3 -init /dev/null -batch -bail restored.db ".restore backup.db"
```

`restored.db` contains the snapshot from the binary backup.
After the command succeeds, check integrity and verify the expected data.
Open only databases and backups you trust.
Verify the restore before replacing a live database file.
Define how to stop clients and switch paths in your production procedure.

[Verify the result](#verify-the-restored-database) · [Complete examples](backup-lab.md)

<a id="создать-и-восстановить-sql-копию"></a>
## Create and restore a SQL dump

Use a SQL dump for inspection or transfer as an alternative to binary backup and `.restore`.
Use a trusted `source.db` and unused paths for `dump.sql` and `restored-sql.db`.

Run this Bash snippet.

```bash
( set -C; sqlite3 -init /dev/null -batch -bail -readonly source.db ".dump" > dump.sql ) && \
( set -C; : > restored-sql.db ) && \
sqlite3 -init /dev/null -batch -bail restored-sql.db < dump.sql
```

The CLI executes the SQL in a new database.
If a destination path already exists, that step stops.
A SQL dump contains executable code. Restore only a file you trust.
`-bail` stops the CLI on error. Transaction boundaries still depend on the SQL.
A full `.dump` of this practice database includes transaction boundaries.
Treat a dump left incomplete by an error as unusable.
After restoration, check the schema, data, indexes, and triggers.

[Complete SQL dump example](backup-lab.md#verify-a-cli-backup-and-sql-dump)

<a id="проверить-восстановленную-бд"></a>
## Verify the restored database

After restoring the backup, connect to `restored.db` and run this SQL snippet.

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
SELECT id, username FROM users ORDER BY id;
```

For the practice database, `integrity_check` returns `ok`.
`foreign_key_check` returns zero rows.
The users query returns `1 | alice`.
Inspect the outputs directly. The CLI can exit successfully even when a PRAGMA reports a problem.

- [ ] Compare the required rows with the expected snapshot.
- [ ] Check `integrity_check`.
- [ ] Run `foreign_key_check` separately.
- [ ] Check indexes and triggers.
- [ ] Check constraints and application queries.
- [ ] Confirm the checks left the live database untouched.

`integrity_check` checks structure and some constraints. Use `foreign_key_check` for foreign keys.
Check application data and business rules separately.
The [complete verification examples](backup-lab.md) include expected constraint violations and trigger behavior.

<a id="учесть-wal-и-границы-копии"></a>
## Account for WAL and backup scope

If the source database is open or uses WAL, make a consistent copy with the backup API or SQLite's own commands.
The active `-wal` file can contain important data.
Do not copy only the main file of an active database.
Leave an active `-wal` file in place.

The backup API copies one database from the connection, `main` by default.
Plan backups separately for external application files and other attached databases.
Store a backup on another disk to protect against disk loss.
Check encryption modes and extensions for your build.

The [Python practice example](backup-lab.md#verify-the-backup-api) copies an open WAL database without a competing writer.
Prepare separate restore tests for concurrent workloads and power failures.
`VACUUM INTO` creates a separate compact copy. Check its [limitations](https://www.sqlite.org/lang_vacuum.html#vacuuminto) before choosing this method.
See [concurrency and WAL](backup-and-migrations.md#concurrency-and-wal) for more.

<a id="источники"></a>
## Sources

- [SQLite backup API](https://www.sqlite.org/backup.html), [Python 3.14 Connection.backup](https://docs.python.org/3.14/library/sqlite3.html#sqlite3.Connection.backup), [CLI](https://www.sqlite.org/cli.html).
- [Integrity check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign key check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check), [WAL](https://www.sqlite.org/wal.html), [VACUUM INTO](https://www.sqlite.org/lang_vacuum.html#vacuuminto).
- [3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html), [3.54.0 release notes](https://www.sqlite.org/releaselog/3_54_0.html).
