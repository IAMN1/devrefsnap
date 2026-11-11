<a id="подключение-права-и-эксплуатация"></a>
# Connections, privileges, and operations

[Русский](../../../../ru/databases/relational/postgresql/operations.md)

Use this page for PostgreSQL 18 connections, privileges, concurrency, and diagnostics.
Run examples that make changes on a separate practice server. Each example states any administrative privileges it requires.

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Choose an installation method or create a database | Package, container, CREATE DATABASE | [Setup](#installation-and-database-management) |
| Check the connection and inspect objects | psql, SHOW, and meta-commands | [Connections](#connections-and-psql-commands) |
| Allow reads on existing and future tables | GRANT and default privileges | [Privileges](#roles-and-access) |
| Protect an update to a shared row | FOR UPDATE, isolation, and retries | [Concurrency](#transactions-isolation-and-locks) |
| Find a wait or maintain a table | pg_stat_activity, locks, VACUUM | [Monitoring](#monitoring-and-maintenance) |
| Check extension availability | pg_available_extensions and installation requirements | [Extensions](#extensions-and-diagnostics) |

[PostgreSQL reference](README.md)

| Item | Details |
| --- | --- |
| Levels | Basic for connections. Intermediate for privileges. Advanced for concurrency and monitoring. |
| Prerequisites | PostgreSQL 18 and the [practice schema](query-lab.md#complete-practice-database-example) for demo queries. Examples state administrative privileges separately. |

<a id="установка-и-управление-бд"></a>
## Installation and database management

**Basic.** Installation depends on the operating system and package repository.
Use the [official platform selector](https://www.postgresql.org/download/).
An Ubuntu or Debian release's standard repository may lack `postgresql-18`.
Use systemd commands only for Linux installations managed by systemd.
Check the service or cluster name in the package documentation.

For containers, use the [official image documentation](https://hub.docker.com/_/postgres).
It defines initialization variables and the volume path for the chosen major version.
Before upgrading from 16 to 18, check data layout and the upgrade procedure.
Use a loopback port binding for local-only access.

Use the SQL forms below individually as a reference.
Run each command with a role that has the required privileges.
Run CREATE DATABASE and DROP DATABASE outside ordinary transaction blocks.

```text
CREATE DATABASE database_name OWNER owner_role TEMPLATE template0 ENCODING 'UTF8';
ALTER DATABASE database_name RENAME TO new_name;
ALTER DATABASE database_name OWNER TO new_owner;
CREATE DATABASE copy_name TEMPLATE source_name;  -- other sessions must stay disconnected from the source
DROP DATABASE database_name;  -- deletes the entire database; check its name and backup first
```

The locale and collation provider must be available in your environment.
A value such as `en_US.UTF-8` may differ across operating systems.
Keep regular backups even if you copy databases through TEMPLATE.

<a id="подключение-и-команды-psql"></a>
## Connections and psql commands

**Basic.** Run this shell command for an existing database.

```bash
psql --host=127.0.0.1 --port=5432 --username=postgres \
  --dbname=cheatsheet_demo --no-psqlrc --set=ON_ERROR_STOP=1
```

Keep passwords out of URLs and command lines.
For repeated connections, configure a [password file](https://www.postgresql.org/docs/18/libpq-pgpass.html) with appropriate permissions.
Give the application its own role.
This example uses postgres only in an isolated practice environment.

Run this SQL in the database connection.

```sql
SELECT current_database(), current_user;
SHOW server_version;
SELECT pg_size_pretty(pg_database_size(current_database()));
```

The expected database is `cheatsheet_demo`.
The version should belong to the 18 release series.
Database size depends on the environment.

Enter the following meta-commands **inside psql**.

```text
\conninfo
\l
\dn
\dt demo.*
\d demo.users
\di demo.*
\du
\dp demo.*
\dx
\timing on
\x auto
\q
```

`\di` filters index names.
Use `\d demo.users` to inspect a specific table's indexes.
`\c` switches databases.
`\df` lists functions.
`\dv` lists views.
`\i file.sql` reads a file.
`\o file.txt` redirects output.
`\?` and `\h SELECT` open help.

<a id="роли-и-доступ"></a>
## Roles and access

Create a role that can read existing and future demo tables while lacking INSERT privileges.

**Intermediate.** Run this one-time SQL snippet in `cheatsheet_demo` as the demo object owner with CREATEROLE.
In a practice cluster, postgres can serve as that role.
The snippet creates a persistent role and changes privileges.
A second CREATE ROLE with the same name fails.

```sql
CREATE ROLE cheatsheet_reader NOLOGIN;
GRANT CONNECT ON DATABASE cheatsheet_demo TO cheatsheet_reader;
GRANT USAGE ON SCHEMA demo TO cheatsheet_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA demo TO cheatsheet_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA demo
GRANT SELECT ON TABLES TO cheatsheet_reader;

SELECT has_table_privilege('cheatsheet_reader', 'demo.users', 'SELECT') AS can_read,
       has_table_privilege('cheatsheet_reader', 'demo.users', 'INSERT') AS can_insert;
```

Expect `can_read = t` and `can_insert = f` in the original practice environment without additional grants.
Default privileges apply to future objects created by **the role that ran ALTER DEFAULT PRIVILEGES**.
For another owner, configure FOR ROLE separately.
ALL TABLES affects existing objects.
Reading a table requires SELECT on the table as well as USAGE on its schema.
Database privileges and object privileges are separate.

For an individual login, create a role with LOGIN.
Grant it membership in cheatsheet_reader.
Set its password with the psql command `\password role_name`.
Keep password literals out of published scripts.
REVOKE removes a grant.
Before DROP ROLE, resolve ownership and dependencies.

For password authentication, prefer `scram-sha-256`.
MD5 passwords are deprecated.
Configure pg_hba.conf for your addresses, roles, and TLS requirements.
Assess a rule such as `host all all 0.0.0.0/0 ...` before allowing broad network access.
The server applies the first matching rule.
`SHOW ssl` shows the server setting.
Use this query to check encryption for the current connection.

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

The result depends on the connection method.
For remote TLS clients, configure certificate and server-name verification, for example libpq `sslmode=verify-full`.

<a id="транзакции-изоляция-и-блокировки"></a>
## Transactions, isolation, and locks

When several connections update stock, read and update the row in the same transaction.

**Advanced.** This SQL snippet in the demo database holds a row lock until ROLLBACK.
Close the transaction promptly in a shared environment.

```sql
BEGIN;
SELECT id, stock FROM demo.products WHERE id = 1 FOR UPDATE;
UPDATE demo.products SET stock = stock - 1 WHERE id = 1 AND stock > 0
RETURNING stock;
ROLLBACK;
```

Expect stock `10` on read and `9` from RETURNING.
After rollback, stock is `10` again.
Another connection updating that row may wait for the lock.
FOR SHARE and FOR KEY SHARE serve different purposes.
LOCK TABLE selects a table-wide lock mode.
In autocommit, a standalone SELECT releases its lock when its transaction ends.

| PostgreSQL isolation level | Behavior |
| --- | --- |
| READ UNCOMMITTED | Behaves as READ COMMITTED and prevents dirty reads |
| READ COMMITTED, the default | New snapshot for every command. A repeated SELECT can see a different result. |
| REPEATABLE READ | Transaction snapshot. PostgreSQL also prevents phantom reads. An update conflict can occur. |
| SERIALIZABLE | Checks compatibility with serial execution. A serialization failure can occur. |

Set the isolation level in BEGIN or with SET TRANSACTION before the first read or write.
On SQLSTATE `40001`, retry **the entire transaction** from the beginning.
For a deadlock, `40P01`, define an application recovery or retry policy as well.
Sequence changes persist after transaction rollback.
Gaps in IDs are normal.

ROLLBACK TO SAVEPOINT undoes only work after the savepoint.
For an atomic business operation, roll back the entire operation on failure.
Committing only the first half breaks its atomicity.

<a id="мониторинг-и-обслуживание"></a>
## Monitoring and maintenance

If a query waits or a table accumulates dead rows, inspect sessions, locks, and table state first.

**Advanced.** Run these diagnostic SQL snippets in the demo database.

```sql
SELECT pid, state, now() - query_start AS duration,
       wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND state = 'active'
ORDER BY query_start;

SELECT schemaname, relname,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       n_live_tup, n_dead_tup
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

SELECT pid, pg_blocking_pids(pid) AS blocked_by
FROM pg_stat_activity
WHERE datname = current_database();
```

They return real sessions and sizes, so row counts vary.
An ordinary role can see only some details about other sessions.
Monitoring may require special roles.
Check `idle in transaction` sessions separately.
They can hold locks and delay cleanup.
`pg_stat_user_indexes` shows index usage statistics.
`pg_statio_user_tables` shows I/O statistics.
`pg_locks` shows locks.
An index with no accesses during a short interval may still be needed.

Run each SQL command below separately as the owner or a role with the required privileges.

```sql
ANALYZE demo.orders;
VACUUM (ANALYZE) demo.orders;
```

The commands update statistics and maintain the table.
Run VACUUM outside an explicit transaction block.
Ordinary VACUUM makes space reusable within the table.
VACUUM FULL rewrites the table and takes ACCESS EXCLUSIVE.
Reserve disk space and a maintenance window for VACUUM FULL.
Usually leave autovacuum enabled.
Tune it based on measured workload.

`CHECKPOINT` forces a WAL checkpoint.
For physical checks, consider [pg_amcheck](https://www.postgresql.org/docs/18/app-pgamcheck.html) and offline checksum verification.
Each has its own prerequisites.
Verify restoration separately.
REINDEX also creates load and locks.
See [indexes](schema-and-indexes.md#indexes-and-query-plans) for CONCURRENTLY variants.

<a id="расширения-и-диагностика"></a>
## Extensions and diagnostics

A feature may require a server package or a restart.
Check availability and installation requirements first.

**Advanced.** This SQL snippet lists available and installed extensions.

```sql
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('pg_trgm', 'unaccent', 'pgcrypto', 'uuid-ossp', 'pg_stat_statements')
ORDER BY name;
SELECT extname, extversion FROM pg_extension ORDER BY extname;
```

The result depends on installed server packages.
CREATE EXTENSION enables an available extension in one database.
Install the operating system package separately if needed.
Check privileges and availability before enabling the extension.

| Task | Feature or limitation |
| --- | --- |
| Similar strings | [pg_trgm](https://www.postgresql.org/docs/18/pgtrgm.html), with `similarity`, operators, and index operator classes |
| Remove diacritics | [unaccent](https://www.postgresql.org/docs/18/unaccent.html) |
| Cryptographic functions | [pgcrypto](https://www.postgresql.org/docs/18/pgcrypto.html). Design application data protection separately. |
| Additional UUID algorithms | [uuid-ossp](https://www.postgresql.org/docs/18/uuid-ossp.html). Built-in `gen_random_uuid()` needs no extension. |
| Aggregated query statistics | [pg_stat_statements](https://www.postgresql.org/docs/18/pgstatstatements.html). Configure shared_preload_libraries, restart, then run CREATE EXTENSION in the database. |
| Geospatial data | [PostGIS](https://postgis.net/documentation/), a separate package with its own compatibility matrix |
| Partition management | [pg_partman](https://github.com/pgpartman/pg_partman), with a separate installation and operating procedure |
| Logical replication, repacking, or debugging | Check third-party pglogical, pg_repack, and pldbgapi versions and limits in their project documentation |
| Compression | Choose storage, TOAST, and third-party extensions for your workload. A standard installation may lack `CREATE EXTENSION zstd`. |

Preserve existing entries when changing shared_preload_libraries.
Resetting statistics discards accumulated measurements.
Coordinate resets with monitoring.
`log_statement = 'all'` can record sensitive values and increase load.
Choose a justified `log_min_duration_statement` threshold for slow queries.
Use `RAISE NOTICE/EXCEPTION` inside PL/pgSQL.
The configuration files postgresql.conf, pg_hba.conf, and pg_ident.conf have separate purposes.
ALTER SYSTEM manages postgresql.auto.conf.

<a id="источники"></a>
## Sources

- [psql](https://www.postgresql.org/docs/18/app-psql.html), [CREATE DATABASE](https://www.postgresql.org/docs/18/sql-createdatabase.html), [schemas](https://www.postgresql.org/docs/18/ddl-schemas.html).
- [Privileges](https://www.postgresql.org/docs/18/ddl-priv.html), [default privileges](https://www.postgresql.org/docs/18/sql-alterdefaultprivileges.html), [SCRAM and MD5](https://www.postgresql.org/docs/18/auth-password.html), [pg_hba.conf](https://www.postgresql.org/docs/18/auth-pg-hba-conf.html).
- [Isolation](https://www.postgresql.org/docs/18/transaction-iso.html), [locks](https://www.postgresql.org/docs/18/explicit-locking.html), [serialization retries](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html).
- [Statistics](https://www.postgresql.org/docs/18/monitoring-stats.html), [VACUUM](https://www.postgresql.org/docs/18/sql-vacuum.html), [CHECKPOINT](https://www.postgresql.org/docs/18/sql-checkpoint.html).
