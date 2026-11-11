
# PostgreSQL

[Русский](../../../../ru/databases/relational/postgresql/README.md)

PostgreSQL is a relational database server.
This section provides a concise reference.
Separate pages cover queries, schema design, and operations.

[Databases](../../README.md) · [Repository catalog](../../../README.md)

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Construct | Details |
| --- | --- | --- |
| Connect and check the version | `psql`, `SHOW server_version` | [Connections](operations.md#connections-and-psql-commands) |
| Create practice data | `CREATE SCHEMA`, `INSERT` | [Complete queries.sql example](query-lab.md#complete-practice-database-example) |
| Select and change rows | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `RETURNING` | [Queries](queries.md) |
| Calculate grouped and running totals | `GROUP BY`, CTEs, `OVER` | [Analytical queries](queries.md#groups-ctes-and-window-functions) |
| Choose a type or constraint | Identity, `numeric`, `timestamptz`, foreign keys | [Schema and types](schema-and-indexes.md#types-and-constraints) |
| Speed up searches | B-tree, GIN, `EXPLAIN` | [Indexes and query plans](schema-and-indexes.md#indexes-and-query-plans) |
| Query JSONB or search text | `->>`, `@>`, `to_tsvector` | [JSONB and full-text search](schema-and-indexes.md#jsonb-and-full-text-search) |
| Grant read access | `GRANT`, default privileges | [Roles and access](operations.md#roles-and-access) |
| Diagnose concurrency and server state | Transactions, locks, `pg_stat_activity` | [Operations](operations.md) |
| Choose a format and create a backup | `pg_dump -Fc` or plain SQL | [Formats](backup-and-restore.md#choose-a-format-and-check-versions) · [Backups](backup-and-restore.md#create-a-logical-backup) |
| Restore and verify a backup | New database, restore, verification | [Restore](backup-and-restore.md#restore-a-logical-backup-to-a-new-database) · [Verification](backup-and-restore.md#verify-the-restored-database) |
| Understand replication and PITR | Base backup and an unbroken WAL chain | [PITR scope](backup-and-restore.md#pitr-and-replication) |

| Item | Details |
| --- | --- |
| Target release series | PostgreSQL 18 |
| Prerequisites | Basic SQL, a PostgreSQL 18 server, and PostgreSQL 18 client utilities |

<a id="базовый-уровень"></a>

<a id="выполнить-первый-запрос"></a>
## Run your first query

Start with [connecting](operations.md#connections-and-psql-commands).
Then run the [shared practice example](query-lab.md#complete-practice-database-example).
It creates three tables in the `demo` schema, demonstrates a JOIN, and verifies rollback.

Run this SQL snippet in `cheatsheet_demo` after the example.

```sql
SELECT name, price
FROM demo.products
WHERE price >= 100
ORDER BY price DESC, id;
```

Expect `Monitor | 300.00` and `Keyboard | 100.00`, in the order set by `ORDER BY`.
In an application, pass user-supplied values through driver parameters.
Keep the values out of the SQL text.

<a id="средний-уровень"></a>

<a id="работать-с-данными-и-схемой"></a>
## Work with data and schemas

- [CRUD with RETURNING and upsert](queries.md#change-data-and-check-the-result) rolls back the changes made by the practice snippets.
- [Groups, CTEs, and window functions](queries.md#groups-ctes-and-window-functions) cover joins that preserve users without orders, totals, and ranking.
- [Types, ALTER TABLE, and indexes](schema-and-indexes.md) cover data constraints, partial and composite indexes, and query plans.
- [Privileges and backups](operations.md#roles-and-access) cover a separate read role. [Restoration](backup-and-restore.md#restore-a-logical-backup-to-a-new-database) targets a new database.

<a id="продвинутый-уровень"></a>

<a id="разобрать-конкуренцию-и-эксплуатацию"></a>
## Understand concurrency and operations

- [Isolation and locks](operations.md#transactions-isolation-and-locks) explain lock lifetimes and transaction retries after serialization failures.
- [JSONB, full-text search, and partitioning](schema-and-indexes.md#jsonb-and-full-text-search) cover operators, search configurations, and partition bounds.
- [Monitoring, VACUUM, and extensions](operations.md#monitoring-and-maintenance) explain diagnostic queries and the effects of maintenance commands.
- [PITR and replication](backup-and-restore.md#pitr-and-replication) outline the process and prerequisites. Production configuration requires a separate procedure.

<a id="частые-ошибки"></a>
## Common mistakes

| Symptom or misconception | Explanation and action |
| --- | --- |
| `\dt` fails in a driver | Run it inside `psql`. See the [command contexts](operations.md#connections-and-psql-commands). |
| Assuming READ UNCOMMITTED allows dirty reads | PostgreSQL treats it as READ COMMITTED |
| Pagination returns changing row sets | Use a stable `ORDER BY` with `LIMIT/OFFSET`. A large OFFSET can also be expensive. |
| `GRANT … ON ALL TABLES` gives no access to a new table | Set default privileges for the role that creates future objects |
| Treating `CHECKPOINT` as an integrity check | It forces a WAL checkpoint |
| Assuming `TRUNCATE` bypasses WAL or rollback | Truncating a normal table is logged and can be rolled back. It takes ACCESS EXCLUSIVE. `CASCADE` affects related tables. |
| Using `recovery.conf` for restoration | PostgreSQL removed support in version 12. Version 18 uses normal configuration parameters and signal files. |

<a id="источники"></a>
## Sources

- [PostgreSQL 18 documentation](https://www.postgresql.org/docs/18/) and [18.6 release notes](https://www.postgresql.org/docs/18/release-18-6.html).
- [SELECT](https://www.postgresql.org/docs/18/sql-select.html), [transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html).
- [TRUNCATE](https://www.postgresql.org/docs/18/sql-truncate.html), [WAL and PITR](https://www.postgresql.org/docs/18/continuous-archiving.html).
- Each detailed page also links to topic-specific documentation.
