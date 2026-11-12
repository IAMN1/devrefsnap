
# SQL

[Русский](../../../ru/databases/sql/README.md)

SQL is a language for querying relational data.
This reference explains common techniques.
Check the syntax and guarantees for the specific database engine you use.

[Databases](../README.md) · [PostgreSQL](../relational/postgresql/README.md) · [SQLite](../relational/sqlite/README.md)

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Construct | Where to look |
| --- | --- | --- |
| Prepare data and run your first JOIN | CREATE / INSERT / SELECT | [Quick example](queries.md#полный-пример) · [Complete example](query-lab.md#complete-example) |
| Filter and sort rows | WHERE / ORDER BY / IS NULL | [Queries](queries.md#filtering-and-joins) |
| Change rows | INSERT / UPDATE / DELETE | [CRUD](queries.md#change-data) |
| Calculate totals | GROUP BY / HAVING / CTE / OVER | [Analytics](queries.md#aggregation-ctes-and-window-functions) |
| Port a query between database engines | Row limits, identity, DDL, RETURNING | [Dialects](dialects-and-transactions.md#dialect-differences) |
| Protect changes | Transactions, savepoints, and constraints | [Transactions](dialects-and-transactions.md#transactions-and-isolation) |
| Diagnose a slow query | Query plan, indexes, statistics | [Optimization](dialects-and-transactions.md#schema-indexes-and-query-plans) |

| Item | Details |
| --- | --- |
| Dialects | Common constructs. Run examples on PostgreSQL 18 or SQLite 3.53. The reference identifies MySQL 8.4 and SQL Server 17.x differences. |
| Prerequisites | Tables, rows, primary keys, and foreign keys |

<a id="базовый-уровень"></a>

<a id="прочитать-запрос-и-выбрать-строки"></a>
## Read a query and select rows

Read SELECT in this logical order: `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`.
The query planner chooses the physical execution order.
Run the [practice example](query-lab.md#complete-example) first.
Then change one condition at a time.

Run this PostgreSQL or SQLite snippet after the example.

```sql
SELECT name FROM sql_users WHERE name LIKE 'a%' ORDER BY id;
```

The result is `alice`. LIKE case sensitivity and text comparison rules depend on the database engine and collation.
`SELECT *` is convenient when exploring data.
For application interfaces, usually list the required columns explicitly.

<a id="средний-уровень"></a>

<a id="объединить-данные-и-изменить-строки"></a>
## Combine data and change rows

Use [JOIN, EXISTS, grouping, and ordinary CTEs](queries.md) to combine tables and calculation steps.
The [INNER JOIN and LEFT JOIN diagram](queries.md#compare-inner-join-and-left-join) compares the rows each join returns from the same tables.
`WHERE` filters rows before grouping.
`HAVING` filters groups.
`COUNT(*)` counts rows.
`COUNT(column)` counts non-NULL values.
An outer JOIN preserves unmatched rows unless a later filter removes them.

Use driver parameters, constraints, and transactions when changing data.
Commands with the same name can have different guarantees.
[DDL and TRUNCATE](dialects-and-transactions.md) vary by database engine.

<a id="продвинутый-уровень"></a>

<a id="проверить-сложный-запрос"></a>
## Check a complex query

Use [window functions and recursive CTEs](queries.md#aggregation-ctes-and-window-functions) for running totals, ranks, and hierarchies.
A frame measured in rows can cover a variable span of time.
Check [isolation, query plans, and indexes](dialects-and-transactions.md) on the target database engine.
A plan for three rows cannot predict how a large production table will behave.

<a id="частые-ошибки"></a>
## Common mistakes

| Problem | What to check |
| --- | --- |
| `column = NULL` | Use IS NULL or IS NOT NULL |
| NOT IN returns unexpected results | A NULL in the subquery changes the logic. Consider NOT EXISTS. |
| LEFT JOIN drops unmatched rows | Filtering the right table in WHERE often has the same effect as INNER JOIN |
| UPDATE or DELETE affects every row | Check for a missing WHERE clause. Run a SELECT with the same condition before making changes. |
| Unstable pagination | Use ORDER BY with a unique tie-breaker as the last sort key. A large OFFSET can be expensive. |
| Assuming READ UNCOMMITTED behaves the same everywhere | PostgreSQL treats it as READ COMMITTED |
| Copied SQL mixes AUTO_INCREMENT, MODIFY, and RETURNING | Choose a dialect. See the [dialect comparison](dialects-and-transactions.md#dialect-differences). |

<a id="источники"></a>
## Sources

- [PostgreSQL 18 queries](https://www.postgresql.org/docs/18/queries.html).
- [MySQL 8.4 SELECT](https://dev.mysql.com/doc/refman/8.4/en/select.html).
- [SQL Server SELECT](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver17).
- [SQLite SQL language](https://www.sqlite.org/lang.html).
