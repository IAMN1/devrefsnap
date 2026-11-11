<a id="проверить-копию-postgresql-в-учебном-окружении"></a>
# Verify a PostgreSQL backup in a practice environment

[Русский](../../../../ru/databases/relational/postgresql/backup-lab.md)

Run a complete custom and plain backup cycle and check a restore failure.
Use a separate server with synthetic data.
[Backup and restore reference](backup-and-restore.md) · [PostgreSQL reference](README.md).

| Task | Where to run it | Example |
| --- | --- | --- |
| Check data and constraints | `psql` connected to the restored database | [Verification SQL](#check-data-and-constraints) |
| Create and restore both backups | Shell connected to the practice server | [Complete example](#verify-custom-plain-and-a-restore-failure) |
| Remove practice resources | After inspecting the result | [Cleanup](#remove-practice-resources) |

| Item | Details |
| --- | --- |
| Level | Intermediate. Rollback on restore failure is advanced. |
| Prerequisites | Bash, PostgreSQL 18, psql, pg_dump, pg_restore, createdb, and a separate server with a postgres role |
| Scope | Synthetic demo schema, custom and plain formats, data equality, constraints, identity, an existing destination name, and data-only restore rollback after a CHECK error |

<a id="подготовить-входные-файлы"></a>
## Prepare the input files

Save [`queries.sql`](../../../../../examples/databases/relational/postgresql/queries.sql).
Save the linked files below as `verify-backup.sql` and `backup-lab.sh` in the same directory.
The script creates the `cheatsheet_demo` practice database.
Check that server and clients use PostgreSQL 18.
The example connects to `127.0.0.1` as `postgres`.
Set the address and role separately for a different installation.
Use a practice server.

The example creates four databases with fixed practice names.
If any new database name already exists, `createdb` stops the script.
Existing databases remain intact.
The script creates a backup directory with `mktemp` and prints its path.
Resources remain available for inspection afterward.

<a id="проверить-данные-и-ограничения"></a>
## Check data and constraints

Run the complete `verify-backup.sql` only in the restored practice database.
It compares the data against the known dataset from `queries.sql`.
It also checks order relationships, UNIQUE, CHECK, and the next identity value.
An incorrect result raises an exception and stops `psql` with `ON_ERROR_STOP`.
The checks end with rollback, but sequences can still advance.

[`postgresql/verify-backup.sql`](../../../../../examples/databases/relational/postgresql/verify-backup.sql)

Expect `DO` and `ROLLBACK` without errors.
Before repeating the identity check, restore the database again because the sequence may have advanced.
For a production database, define your own invariants and application checks.

<a id="проверить-custom-plain-и-отказ-восстановления"></a>
## Verify custom, plain, and a restore failure

The complete Bash script uses the three prepared files in one directory.
Run `bash backup-lab.sh` from that directory.
The archive and SQL file are trusted because the script creates them from the practice schema.

`--no-owner --no-privileges` deliberately skips owners and ACLs.
Use a separate procedure to restore ownership and ACLs.
The data-only restore deliberately targets an incompatible synthetic schema to verify rollback.
For an ordinary restore, use a new empty database as shown in the [restore reference](backup-and-restore.md#restore-a-logical-backup-to-a-new-database).

[`postgresql/backup-lab.sh`](../../../../../examples/databases/relational/postgresql/backup-lab.sh)

The output is `PostgreSQL backup/restore OK`.
Both restored databases contain the original dataset.
The CHECK error leaves none of the previously loaded rows in `cheatsheet_restore_error`.
A comparison confirms that the source `cheatsheet_demo` data remain intact.
For production, add checks for RLS, extensions, and role privileges.
Assess data volume and the effects of concurrent DDL separately.

<a id="очистить-учебные-ресурсы"></a>
## Remove practice resources

Inspect the restored databases and save any archives you need first.
The following snippet **deletes all four practice databases in full**.
Check the server and each database name before running it.

```bash
dropdb --host=127.0.0.1 --username=postgres cheatsheet_restore_check
dropdb --host=127.0.0.1 --username=postgres cheatsheet_plain_check
dropdb --host=127.0.0.1 --username=postgres cheatsheet_restore_error
dropdb --host=127.0.0.1 --username=postgres cheatsheet_demo
```

Remove the archive directory separately after saving the backup you need.

<a id="источники"></a>
## Sources

- [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html), [psql](https://www.postgresql.org/docs/18/app-psql.html).
- [Identity](https://www.postgresql.org/docs/18/ddl-identity-columns.html), [constraints](https://www.postgresql.org/docs/18/ddl-constraints.html), [18.6 release notes](https://www.postgresql.org/docs/18/release-18-6.html).
