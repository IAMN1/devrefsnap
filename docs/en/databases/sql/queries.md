<a id="запросы-на-согласованном-наборе-данных"></a>
# Query a shared practice dataset

[Русский](../../../ru/databases/sql/queries.md)

Use this page to select and change rows and calculate results across related tables.
The PostgreSQL and SQLite snippets share a dataset with separate setup instructions.

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Total payments while keeping every user | LEFT JOIN with a condition in ON | [Totals per user](#total-payments-while-keeping-every-user) |
| Select rows and find missing relationships | WHERE, JOIN, NOT EXISTS | [Queries](#filtering-and-joins) |
| Change related rows and roll back | Transaction and CRUD | [Data changes](#change-data) |
| Calculate totals and rank each row | GROUP BY, CTEs, window functions | [Analytics](#aggregation-ctes-and-window-functions) |

[SQL](README.md)

| Item | Details |
| --- | --- |
| Levels | Basic for CRUD and filters. Intermediate for JOIN and grouping. Advanced for window functions and recursion. |
| Prerequisites | A new PostgreSQL 18 or SQLite 3.53 practice database with the names sql_users and sql_orders available |

<a id="полный-пример"></a>

<a id="посчитать-оплаты-без-потери-пользователей"></a>
## Total payments while keeping every user

Join users in `sql_users` to orders in `sql_orders` and keep users who have no paid orders.
Set up the tables with the [complete SQL example and commands](query-lab.md#complete-example).
Then run this snippet on PostgreSQL or SQLite.

```sql
SELECT u.name, COALESCE(SUM(o.amount_cents), 0) AS paid_cents
FROM sql_users AS u
LEFT JOIN sql_orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.name
ORDER BY u.name;
```

The result is `alice | 14000`, `bob | 0`, `carol | 0`.
The `status` condition in `ON` preserves users without paid orders.
Moving the condition to `WHERE` drops those users from the result.
Amounts use whole cents in a fictional currency.
Run all snippets that depend on these tables in the same database.

<a id="фильтрация-и-соединения"></a>
## Filtering and joins

Find orders within a range of amounts or users without orders.
These snippets read the [practice dataset](query-lab.md#complete-example) without changing it.

**Basic and intermediate.** Run the read-only queries independently.

```sql
SELECT id, amount_cents FROM sql_orders
WHERE status IN ('paid', 'pending')
  AND amount_cents BETWEEN 4000 AND 10000
ORDER BY amount_cents DESC, id;

SELECT u.name, o.amount_cents
FROM sql_users AS u JOIN sql_orders AS o ON o.user_id = u.id
WHERE NOT (o.status = 'pending') ORDER BY o.id;

SELECT u.name FROM sql_users AS u
WHERE NOT EXISTS (SELECT 1 FROM sql_orders AS o WHERE o.user_id = u.id);

SELECT id FROM sql_users
EXCEPT
SELECT user_id FROM sql_orders;
```

The first query returns orders `1 | 10000` and `2 | 4000`.
The second returns `alice | 10000` and `alice | 4000`.
The user without orders is `carol`.
The set difference contains ID `3`.
Use parentheses to clarify how AND, OR, and NOT combine.
BETWEEN includes both endpoints.
In LIKE, `%` matches any number of characters and `_` matches one character.
Check for NULL with IS NULL.

| Join or operation | Purpose and limits |
| --- | --- |
| INNER JOIN | Matching rows. Duplicates can make the result differ from a set intersection. |
| LEFT / RIGHT / FULL JOIN | Preserves unmatched rows from the left, right, or both sides, respectively. MySQL 8.4 lacks FULL JOIN. |
| CROSS JOIN | All combinations. The result can grow quickly. |
| SELF JOIN | Joins a table to itself using separate aliases |
| USING (id) | Joins on columns with the same name. SQL Server uses different syntax. |
| NATURAL JOIN | Joins on all shared column names. Adding a column can silently change the result. |
| UNION / UNION ALL | Combines rows and removes or preserves duplicates, respectively |
| INTERSECT / EXCEPT | Returns common rows or left-side rows absent from the right side. Check support in your database engine's release series. |

A subquery in WHERE supplies values for IN, tests EXISTS, or provides a value for comparison.
A subquery in FROM defines a derived table with an alias.
A scalar subquery in SELECT yields a single column value.
PostgreSQL rejects a scalar subquery that returns multiple rows.
SQLite uses the first row.
For a portable result, ensure the query can return at most one row, for example by filtering on a UNIQUE key.
An empty result yields NULL.
Inspect the query plan to determine the cost of a correlated subquery.

<a id="изменение-данных"></a>
## Change data

Add a user and an order, check the change, and restore the original data.

**Basic.** This PostgreSQL or SQLite snippet rolls back all changes.
Before running it, make sure you selected the practice database.
Without WHERE, UPDATE and DELETE affect every row.

```sql
BEGIN;
INSERT INTO sql_users (id, name) VALUES (4, 'dave');
INSERT INTO sql_orders (id, user_id, amount_cents, status)
SELECT 4, id, 500, 'pending' FROM sql_users WHERE name = 'dave';
UPDATE sql_orders SET status = 'paid', amount_cents = 600 WHERE id = 4;
SELECT amount_cents, status FROM sql_orders WHERE id = 4;
DELETE FROM sql_orders WHERE id = 4;
DELETE FROM sql_users WHERE id = 4;
ROLLBACK;
```

The SELECT inside the transaction returns `600 | paid`.
After rollback, each table still contains three rows.
See [dialects](dialects-and-transactions.md#dialect-differences) for returning changed rows with `RETURNING` or `OUTPUT` and using UPDATE with a join.
ON DELETE CASCADE takes effect when the foreign key declares that action and the engine enforces foreign key checks.

<a id="агрегация-cte-и-окна"></a>
## Aggregation, CTEs, and window functions

Calculate totals per user and a running total while keeping individual result rows.

**Intermediate.** Run these PostgreSQL or SQLite snippets on the practice data.

```sql
WITH totals AS (
    SELECT user_id, COUNT(*) AS orders, SUM(amount_cents) AS total
    FROM sql_orders
    GROUP BY user_id HAVING COUNT(*) >= 2
)
SELECT u.name, t.orders, t.total
FROM totals AS t JOIN sql_users AS u ON u.id = t.user_id;

SELECT id, amount_cents,
       ROW_NUMBER() OVER (ORDER BY amount_cents DESC, id) AS position,
       SUM(amount_cents) OVER (
           ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_cents,
       LAG(amount_cents) OVER (ORDER BY id) AS previous_cents
FROM sql_orders ORDER BY id;
```

The first query returns `alice | 2 | 14000`. The second returns the following rows.

| id | amount_cents | position | running_cents | previous_cents |
| --- | --- | --- | --- | --- |
| 1 | 10000 | 2 | 10000 | NULL |
| 2 | 4000 | 3 | 14000 | 10000 |
| 3 | 30000 | 1 | 44000 | 4000 |

COUNT, SUM, AVG, MIN, and MAX operate on groups.
Most aggregate functions skip NULL values.
A CTE names an intermediate query. The engine can choose whether to materialize it, and performance depends on the plan.
Give a subquery in FROM an explicit alias, for example `FROM (...) AS totals`.

**Advanced.** PARTITION BY divides rows into groups.
ORDER BY inside OVER sets the calculation order.
The outer SELECT needs its own ORDER BY to control output order.
RANK leaves gaps after ties.
DENSE_RANK assigns consecutive ranks.
LEAD reads a subsequent row.
FIRST_VALUE and LAST_VALUE depend on the frame.
`ROWS 6 PRECEDING` measures the frame in rows.
To get LAST_VALUE for the whole partition, end the frame at UNBOUNDED FOLLOWING.
Guard against division by zero when calculating a share of the total.
Choose a numeric type that can represent fractions.
Integer division rules vary by database engine.

This standalone PostgreSQL or SQLite snippet requires no tables.

```sql
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 3
)
SELECT n FROM numbers ORDER BY n;
```

The result is `1`, `2`, `3`. For graphs, add cycle detection and a depth limit.
SQL Server omits the RECURSIVE keyword and imposes its own restrictions on recursive CTEs.

<a id="источники"></a>
## Sources

- [PostgreSQL joins and grouping](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTEs](https://www.postgresql.org/docs/18/queries-with.html), [window functions](https://www.postgresql.org/docs/18/functions-window.html).
- [SQLite SELECT](https://www.sqlite.org/lang_select.html), [WITH](https://www.sqlite.org/lang_with.html), [window functions](https://www.sqlite.org/windowfunctions.html).
- [SQLite scalar subqueries](https://www.sqlite.org/lang_expr.html#subquery_expressions), [PostgreSQL scalar subqueries](https://www.postgresql.org/docs/18/sql-expressions.html#SQL-SYNTAX-SCALAR-SUBQUERIES).
- [MySQL 8.4 JOIN](https://dev.mysql.com/doc/refman/8.4/en/join.html), [SQL Server CTEs](https://learn.microsoft.com/en-us/sql/t-sql/queries/with-common-table-expression-transact-sql?view=sql-server-ver17).
- [PostgreSQL 18.6 release notes](https://www.postgresql.org/docs/18/release-18-6.html), [SQLite 3.53.4 release notes](https://www.sqlite.org/releaselog/3_53_4.html).
