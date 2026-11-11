<a id="выбрать-диалект-и-гарантии-операции"></a>
# Choose a SQL dialect and operation guarantees

[Русский](../../../ru/databases/sql/dialects-and-transactions.md)

Use this page to port SQL or decide which guarantees a data change requires.
Choose the database engine and release series first. The same command can have different effects.

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Port key generation or a DML statement | Compare syntax by database engine | [Dialects](#dialect-differences) |
| Choose a constraint or inspect a query plan | Constraints, indexes, and EXPLAIN | [Schema and query plans](#schema-indexes-and-query-plans) |
| Apply several changes atomically | Transactions, savepoints, and isolation | [Guarantees](#transactions-and-isolation) |
| Pass values and restrict access | Driver parameters and privileges | [Security](#security-and-maintainability) |

[SQL](README.md)

| Item | Details |
| --- | --- |
| Levels | Intermediate for DDL and dialects. Advanced for isolation and plans. |
| Prerequisites | Basic SQL. For practice, use a separate test database on the relevant engine. |

<a id="различия-диалектов"></a>
## Dialect differences

When porting a query, choose the target engine's column before changing the syntax.
The cells use placeholder names t, c, and i.
Replace the placeholders.
Check types and constraints.
Use the cells as individual syntax references.

| Task | PostgreSQL 18 | MySQL 8.4 | SQL Server | SQLite |
| --- | --- | --- | --- | --- |
| Generate a key | `GENERATED ALWAYS AS IDENTITY` + PK | `AUTO_INCREMENT` + index | `IDENTITY(1,1)` + PK | `INTEGER PRIMARY KEY`. Use AUTOINCREMENT when you require its ID reuse policy. |
| Return the first rows | `ORDER BY id LIMIT 10` | `ORDER BY id LIMIT 10` | `TOP (10)` with ORDER BY | `ORDER BY id LIMIT 10` |
| Skip rows | `LIMIT 10 OFFSET 20` or OFFSET/FETCH | `LIMIT 10 OFFSET 20` | `ORDER BY id OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` | `LIMIT 10 OFFSET 20` |
| Return changed values | `RETURNING id` | Use LAST_INSERT_ID for AUTO_INCREMENT. MySQL lacks a general DML RETURNING clause. | `OUTPUT inserted.id` / `deleted.id`, with different placement in the statement | `RETURNING id` since 3.35.0, with different restrictions from PostgreSQL |
| Change a type | `ALTER TABLE t ALTER COLUMN c TYPE ...` | `ALTER TABLE t MODIFY COLUMN c ...` | `ALTER TABLE t ALTER COLUMN c ...` | Limited ALTER support. Rebuild the table for complex changes. |
| Drop an index | `DROP INDEX i` | `DROP INDEX i ON t` | `DROP INDEX i ON t` | `DROP INDEX i` |
| UPDATE from another table | `UPDATE ... SET ... FROM ...` | `UPDATE ... JOIN ... SET ...` | `UPDATE ... SET ... FROM ...` with its own alias rules | UPDATE FROM since 3.33.0. Some PostgreSQL forms require adaptation. |
| Create a partial index | `CREATE INDEX ... WHERE ...` | No general WHERE equivalent | Filtered index with restrictions on the predicate | `CREATE INDEX ... WHERE ...` |
| Search full text | tsvector + GIN/GiST | FULLTEXT + MATCH/AGAINST | FULLTEXT INDEX with a suitable catalog and key | FTS5 if enabled in the build |

Modern Oracle uses FETCH FIRST or OFFSET/FETCH to limit rows.
ROWNUM has its own evaluation order.
Oracle uses a separate dialect.
NULL sort order, identifier quoting, Boolean values, dates, string functions, and case sensitivity also vary.

<a id="структура-индексы-и-план"></a>
## Schema, indexes, and query plans

Use constraints to enforce data rules. Check the cost of accessing data for each query.
Assess schema correctness and performance separately.

**Intermediate.** SQL syntax outline for reference.

```text
CREATE TABLE t (id INTEGER PRIMARY KEY, value INTEGER NOT NULL CHECK (value >= 0));
ALTER TABLE t ADD COLUMN note ...;
ALTER TABLE t ADD CONSTRAINT ...;  -- support and syntax depend on the database engine
CREATE [UNIQUE] INDEX i ON t (value, id);
DROP TABLE t;                    -- drops the table and its data on commit or autocommit
```

NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, and CHECK enforce different rules.
A CHECK expression can permit NULL. Use NOT NULL to forbid it.
Check dialect support before using DROP TABLE CASCADE.
Adding or dropping a constraint or rebuilding a table can block database activity.
Prepare a migration plan before making changes.
Verify the backup.

**Advanced.** An index takes storage space and adds work to writes.
Choose indexes for the filters, JOINs, and sorts your queries actually use.
Column order matters in a composite index.
The query planner uses statistics and can choose another access path even when an index exists.
Partial, expression, and full-text indexes serve different purposes.

| Database engine | Inspect indexes or query plans |
| --- | --- |
| PostgreSQL | `pg_indexes`, psql `\d`, EXPLAIN, EXPLAIN ANALYZE |
| MySQL | SHOW INDEX FROM t, EXPLAIN, EXPLAIN ANALYZE |
| SQL Server | sys.indexes, estimated or actual execution plan. ALTER INDEX ... REBUILD is a maintenance operation. |
| SQLite | PRAGMA index_list(t), index_info(i), EXPLAIN QUERY PLAN |

An actual execution plan or EXPLAIN ANALYZE can run the query.
Account for side effects if the statement changes data.
Compare estimates with actual values.
Check the indexes and statistics.
Estimate the size of the result.
Use the plan to decide whether to replace a JOIN with a subquery or investigate a sequential scan.

<a id="транзакции-и-изоляция"></a>
## Transactions and isolation

When several changes must succeed or roll back together, choose the boundary of the entire operation before creating a savepoint.

**Intermediate.** Begin a transaction.
Run every step of the atomic operation.
Check the result.
On success, run COMMIT.
On error, run ROLLBACK for the entire operation.
ROLLBACK TO SAVEPOINT undoes only the changes after that savepoint.
If you set a savepoint after debiting an account, rolling back the credit and then committing leaves the debit in place.

| Database engine | Begin and use a savepoint | Guarantees |
| --- | --- | --- |
| PostgreSQL | BEGIN; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Most DDL is transactional. You can roll back TRUNCATE. Sequence changes persist after rollback. |
| MySQL InnoDB | START TRANSACTION; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Many DDL statements and TRUNCATE cause an implicit commit. The table's storage engine matters. |
| SQL Server | BEGIN TRANSACTION; SAVE TRANSACTION s; ROLLBACK TRANSACTION s | Error handling, XACT_STATE, and nested transactions have their own rules |
| SQLite | BEGIN [DEFERRED/IMMEDIATE/EXCLUSIVE]; SAVEPOINT s; ROLLBACK TO s | One writer at a time. Journal mode and Python autocommit affect transaction control. |

**Advanced.** Isolation levels describe which anomalies can occur. Implementations vary.
PostgreSQL treats READ UNCOMMITTED as READ COMMITTED.
READ COMMITTED is the PostgreSQL default.
REPEATABLE READ is the MySQL InnoDB default.
Check SQL Server READ COMMITTED and SNAPSHOT settings and SQLite modes in your environment.
Even at SERIALIZABLE, a conflict can cause a transaction to fail.
In that case, retry the entire transaction according to your retry policy.

<a id="безопасность-и-сопровождаемость"></a>
## Security and maintainability

Pass user-supplied values as driver parameters.
Driver parameters usually accept values only. Select table and column names through a separate, controlled mechanism.
Grant the application role the minimum privileges it needs.
Use a password-hashing library for application users' passwords. A plain SQL hash is insufficient.
Verify a backup by restoring it.
Use explicit aliases, consistent names, and short comments that explain why the SQL takes a particular approach.

<a id="источники"></a>
## Sources

- [MySQL 8.4 ALTER TABLE](https://dev.mysql.com/doc/refman/8.4/en/alter-table.html), [CREATE TABLE](https://dev.mysql.com/doc/refman/8.4/en/create-table.html), [implicit commit](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html), [InnoDB isolation](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html).
- [SQL Server DROP INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-index-transact-sql?view=sql-server-ver17), [ORDER BY / OFFSET](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql?view=sql-server-ver17), [OUTPUT](https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql?view=sql-server-ver17).
- [PostgreSQL isolation](https://www.postgresql.org/docs/18/transaction-iso.html), [TRUNCATE](https://www.postgresql.org/docs/18/sql-truncate.html).
- [SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [AUTOINCREMENT](https://www.sqlite.org/autoinc.html).
