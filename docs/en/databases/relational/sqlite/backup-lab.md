<a id="проверить-копию-sqlite-в-учебном-окружении"></a>
# Verify a SQLite backup in a practice environment

[Русский](../../../../ru/databases/relational/sqlite/backup-lab.md)

Practice backup and restore with the Python API or CLI.
Each example creates and removes only its own temporary directory with synthetic data.
[Backup and restore reference](backup-and-restore.md) · [Schema migration](backup-and-migrations.md).

| Task | Example | Checks |
| --- | --- | --- |
| Verify a backup of an open WAL database | [Python API](#verify-the-backup-api) | Snapshot, schema, constraints, trigger, and expected failures |
| Verify binary and SQL backups | [CLI](#verify-a-cli-backup-and-sql-dump) | `.backup`, `.restore`, `.dump`, integrity, foreign keys, and behavior |

| Item | Details |
| --- | --- |
| Level | Intermediate. WAL limitations and failure handling are advanced. |
| Prerequisites | Python 3.14 with sqlite3, or Bash and the sqlite3 CLI. The STRICT schema requires SQLite 3.37. |

<a id="проверить-backup-api"></a>
## Verify the backup API

Save the complete example as `backup.py`.
Run `python3.14 backup.py`.
The dependencies are part of the Python standard library.

The source remains open in WAL mode with no competing writer.
After creating the backup, the script changes the source.
The restored database should contain the earlier snapshot.
The script reserves destination files with `touch(exist_ok=False)` to avoid replacing existing files.
If the backup fails, the destination may be incomplete. The script removes it with its temporary directory.

[`sqlite/backup.py`](../../../../../examples/databases/relational/sqlite/backup.py)

The output is `Python backup/restore OK; SQLite ...`.
The backup preserves `alice`, and the source contains `alice-live` after the backup.
The trigger check rolls back its changes to the restored database.
An existing destination, a missing source, and an invalid file format cause the expected failures.
The example covers restoration from a backup of a working database.

<a id="проверить-cli-копию-и-sql-dump"></a>
## Verify a CLI backup and SQL dump

Save the complete example as `backup-cli.sh`.
Run `bash backup-cli.sh`.
Use Bash and the sqlite3 CLI with STRICT support.
The script creates its own source database and needs no external files or server.

`set -C` prevents redirection from overwriting existing destinations.
On their own, `.backup` and `.restore` can overwrite an existing destination.
All paths in this example are inside the temporary directory it creates.

[`sqlite/backup-cli.sh`](../../../../../examples/databases/relational/sqlite/backup-cli.sh)

The output is `CLI backup/restore OK`.
Both restored databases contain the expected rows, the index, and a working trigger.
The checks confirm that foreign key and CHECK constraints reject invalid data and that the source file remains intact.
A separate practice database shows a foreign key violation despite a successful `integrity_check`.
Check the CLI version with `sqlite3 --version`.

<a id="источники"></a>
## Sources

- [Backup API](https://www.sqlite.org/backup.html), [Python Connection.backup](https://docs.python.org/3.14/library/sqlite3.html#sqlite3.Connection.backup), [CLI and dump](https://www.sqlite.org/cli.html).
- [Integrity check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign key check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check), [WAL](https://www.sqlite.org/wal.html).
- [3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html), [3.54.0 release notes](https://www.sqlite.org/releaselog/3_54_0.html).
