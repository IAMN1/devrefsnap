<a id="создать-копию-postgresql-и-проверить-восстановление"></a>
# Back up PostgreSQL and verify the restore

[Русский](../../../../ru/databases/relational/postgresql/backup-and-restore.md)

Choose a backup format, restore to a new database, and check the result.
Use a separate PostgreSQL 18 practice server for these examples.
[PostgreSQL reference](README.md).

<a id="быстрый-поиск"></a>
## Quick reference

| Situation | Choice | Reference or example |
| --- | --- | --- |
| Back up one database | Custom archive → `pg_restore` | [Create a backup](#create-a-logical-backup) |
| Produce readable SQL | Plain SQL → `psql` | [Choose a format](#choose-a-format-and-check-versions) · [SQL file](#restore-a-sql-file) |
| Inspect an archive | `pg_restore --list` | [Inspect contents](#inspect-an-archives-contents) |
| Verify restoration | New database → restore → checks | [Restore a custom archive](#restore-a-logical-backup-to-a-new-database) |
| Verify a successful restore | Compare data and check constraints | [Check the result](#verify-the-restored-database) |
| Include roles, privileges, or selected tables | Plan backup contents separately | [Backup scope](#other-formats-and-backup-scope) |
| Restore to a point in time | Physical backup and WAL | [PITR scope](#pitr-and-replication) |

| Item | Details |
| --- | --- |
| Levels | Intermediate for logical backups and restoration. Advanced for backup scope, PITR, and replication. |
| Prerequisites | PostgreSQL 18 server and client utilities, a separate practice database, and space for the archive and a new database |

<a id="выбрать-формат-и-проверить-версии"></a>
## Choose a format and check versions

Choose compatible utilities and the restore method.
Compare server and client versions first.
Run these shell commands against your separate practice server.

```bash
pg_dump --version
pg_restore --version
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --no-psqlrc --set=ON_ERROR_STOP=1 --command="SHOW server_version;"
```

| Goal | Format or command | Restore or limitation |
| --- | --- | --- |
| Archive with selective object restoration | `pg_dump --format=custom` | Use `pg_restore`. Custom format supports no parallel dump. |
| Readable SQL | `pg_dump --format=plain` | Restore with `psql` |
| Parallel dump | `pg_dump --format=directory --jobs=4` | Creates a directory. Choose the number of processes based on resources. |
| Point-in-time recovery | Physical base backup and WAL | Requires a physical recovery chain |

The format determines the restore tool.
For the practice example, use PostgreSQL 18.6 server and clients.
`pg_dump` cannot read a server from a newer major version than its own.
Restoration to an older major version is not guaranteed.

<a id="создать-логическую-копию"></a>
## Create a logical backup

Create a consistent logical backup of the practice `cheatsheet_demo` database.
Prepare source data using [queries.sql](query-lab.md#complete-practice-database-example).
The `postgres` role below applies only to the separate practice server.
Enter the password when prompted or use a configured password file.
Define production privileges and operating procedures separately.

Run related snippets in the same shell.

```bash
umask 077
backup_dir=$(mktemp -d)
pg_dump --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --format=custom --file="$backup_dir/cheatsheet_demo.dump"
```

On successful completion, the archive contains one database.
`pg_dump` takes a consistent snapshot during normal concurrent activity.
Plan contents and locking separately for complex operations.
Discard an incomplete file if `pg_dump` fails.
The archive contains data, so give it appropriate access permissions.
A single-database archive excludes cluster roles and tablespaces.

[Complete example](backup-lab.md#verify-custom-plain-and-a-restore-failure)

<a id="посмотреть-состав-архива"></a>
## Inspect an archive's contents

Check the format and object list before restoring.
This snippet continues the [backup procedure](#create-a-logical-backup).

```bash
pg_restore --list "$backup_dir/cheatsheet_demo.dump"
```

The list includes the `demo` schema, tables, data, and constraints.
Review `pg_dump` warnings and compare the object list with your expectations.
After listing succeeds, test the full restoration to verify the data.
Restore only trusted archives.
A restore can execute SQL and code chosen by owners on the source server.

[Next, create a new database](#restore-a-logical-backup-to-a-new-database)

<a id="логическая-копия-и-восстановление-в-новую-бд"></a>
## Restore a logical backup to a new database

Verify the archive while preserving the source database.
Use the archive created above and an unused destination name, `cheatsheet_restore_check`.

`--no-owner --no-privileges` skips original owners and ACLs.
Restored objects belong to the restore role.
To transfer production permissions, plan owners and ACLs separately.
`--single-transaction` rolls back restoration changes on error and is incompatible with `--jobs`.
A single transaction may be inconvenient for a large database.

Continue in the same shell.

```bash
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_restore_check && \
pg_restore --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_check \
  --single-transaction --exit-on-error --no-owner --no-privileges \
  "$backup_dir/cheatsheet_demo.dump"
```

The new database contains the restored objects and data.
The `&&` prevents restoration if creating the destination database fails.
If restoration fails, the newly created database remains. Inspect the error before retrying.
Do not use `--clean` to work around a restore error. It drops existing objects in the destination database.
After exit code `0`, verify the restored database against application requirements.

[Verify the result](#verify-the-restored-database) · [Complete example and expected failure](backup-lab.md#verify-custom-plain-and-a-restore-failure)

<a id="восстановить-sql-файл"></a>
## Restore a SQL file

Use plain SQL as an independent alternative to a custom archive.
The destination `cheatsheet_plain_check` must be absent.

Run this shell snippet for the same practice source database.

```bash
umask 077
plain_dir=$(mktemp -d)
pg_dump --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --format=plain --no-owner --no-privileges --file="$plain_dir/backup.sql" && \
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_plain_check && \
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_plain_check \
  --no-psqlrc --set=ON_ERROR_STOP=1 --single-transaction --file="$plain_dir/backup.sql"
```

The trusted SQL file is executed in a new database.
For plain format, set the options to skip owners and ACLs when creating the dump.
`ON_ERROR_STOP` stops SQL execution on error.
`--single-transaction` suits this complete dump without `--create`.
For an arbitrary SQL file, first check that every command supports a single transaction.
Without it, an error can leave earlier changes applied.

[Complete custom and plain example](backup-lab.md#verify-custom-plain-and-a-restore-failure)

<a id="проверить-восстановленную-бд"></a>
## Verify the restored database

After restoration, check data, schema, and behavior.
Run this SQL snippet in `psql` connected to `cheatsheet_restore_check`.

```sql
SELECT
    (SELECT count(*) FROM demo.users) AS users,
    (SELECT count(*) FROM demo.products) AS products,
    (SELECT count(*) FROM demo.orders) AS orders,
    (SELECT stock FROM demo.products WHERE id = 1) AS keyboard_stock;
```

For the unchanged practice data, the result is `3 | 3 | 3 | 10`.
Check more than row counts.
Check ownership and privileges separately from data equality.

- [ ] Compare required data with the expected backup snapshot.
- [ ] Check the schema and required extensions.
- [ ] Check foreign keys and constraints.
- [ ] Check generation of the next identifier.
- [ ] Check application queries and invariants.
- [ ] Check roles and privileges according to the production procedure.

The [complete verification SQL](backup-lab.md#check-data-and-constraints) stops the practice scenario if a result is incorrect.
Insert checks roll back, but identity sequences can still advance.
Run these checks only in a separate restored database.

<a id="другие-форматы-и-границы-копии"></a>
## Other formats and backup scope

| Task | Options or tool | Limitation |
| --- | --- | --- |
| Parallel restore | `pg_restore --jobs=4` | Custom or directory format. Incompatible with `--single-transaction`. Plan how to handle partial failures. |
| Schema only or data only | `--schema-only` / `--data-only` | A data-only restore requires a compatible schema |
| Selected tables | `--table=demo.orders` | Dependencies may need explicit inclusion |
| Cluster roles and tablespaces | `pg_dumpall --globals-only` | Separate administrative export. The file can contain password hashes. |

A complete production backup may also require configuration, extensions, and external files.
Determine completeness from the system's architecture.
Store backups independently from the source storage.
Test full restores regularly.

<a id="удалить-только-проверочную-бд"></a>
## Remove only the verification database

Save the archive and check the server address. Confirm that this run created `cheatsheet_restore_check`. If `createdb` reported that the database already existed, skip cleanup.

Close connections to the verification database. The following shell command **deletes the entire `cheatsheet_restore_check` database**.

```bash
dropdb --host=127.0.0.1 --username=postgres cheatsheet_restore_check
```

For other practice databases, check separately which names this run created.

<a id="pitr-и-репликация"></a>
## PITR and replication

**Advanced conceptual outline. Production setup requires a separate procedure.**
PITR restores a cluster from a physical base backup and an unbroken WAL sequence.
Use a physical base backup for PITR.
Before setup, define acceptable data loss and recovery time.
Define storage and access rules.
Schedule regular tests on a separate server.

1. Configure WAL delivery to independent storage.
   Check repeat delivery and exit status handling.
   Monitor missing segments, free space, and retention.
2. Take a physical base backup, for example with pg_basebackup, using the required privileges and WAL.
   Save configuration, versions, tablespaces, and access keys separately under your operating procedure.
3. For practice, stop the **separate destination** instance.
   Restore a compatible base backup to its data directory.
   Provide the WAL chain from the start of the backup through the recovery target.
4. Set restore_command.
   Choose one recovery target, such as recovery_target_time with an explicit time zone.
   Configure the action on reaching the target.
   Set these parameters in the normal PostgreSQL 18 configuration.
5. Create `recovery.signal` in the destination data directory.
   Start the destination according to the documentation.
   Check logs, the recovery point reached, and the data.
   Decide separately when to finish recovery or promote the instance.

PostgreSQL removed `recovery.conf` in version 12.
Its presence prevents startup.
Use `standby.signal` for a standby.
Choose the signal file for the intended recovery mode.
Physical replication also uses base backups and WAL.
Keep independent backups because replicas can reproduce accidental deletions.
If a consumer falls behind, its replication slot can retain WAL until the disk fills.
Configure monitoring and retention limits.

For your `archive_command`, verify reliable copying, retries, filename conflicts, permissions, remote storage, and recovery in the actual environment.
For practical setup, follow the [PITR procedure](https://www.postgresql.org/docs/18/continuous-archiving.html)
and [pg_basebackup documentation](https://www.postgresql.org/docs/18/app-pgbasebackup.html).

<a id="источники"></a>
## Sources

- [Logical backups](https://www.postgresql.org/docs/18/backup-dump.html), [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html), [psql](https://www.postgresql.org/docs/18/app-psql.html).
- [Createdb](https://www.postgresql.org/docs/18/app-createdb.html), [pg_dumpall](https://www.postgresql.org/docs/18/app-pg-dumpall.html), [18.6 release notes](https://www.postgresql.org/docs/18/release-18-6.html).
- [PITR](https://www.postgresql.org/docs/18/continuous-archiving.html), [recovery parameters](https://www.postgresql.org/docs/18/runtime-config-wal.html#RUNTIME-CONFIG-WAL-RECOVERY-TARGET), [replacement for recovery.conf](https://www.postgresql.org/docs/18/recovery-config.html).
- [Replication](https://www.postgresql.org/docs/18/warm-standby.html), [replication slots](https://www.postgresql.org/docs/18/warm-standby.html#STREAMING-REPLICATION-SLOTS).
