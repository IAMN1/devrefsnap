<a id="выбирать-изменять-и-анализировать-данные"></a>
# Select, change, and analyze data

[Русский](../../../../ru/databases/relational/postgresql/queries.md)

Use this page to select, change, and analyze orders in PostgreSQL 18.
Dependent snippets use the `demo` practice schema. Set it up with the separate complete example.

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Total paid orders for all users | LEFT JOIN with the filter in ON | [Short example](#total-paid-orders-for-all-users) |
| Filter products and find a user without orders | WHERE, JOIN, NOT EXISTS | [Queries](#select-rows-and-join-tables) |
| Return a changed row or perform an upsert | RETURNING and ON CONFLICT | [Changes](#change-data-and-check-the-result) |
| Calculate totals, ranks, and the previous amount | GROUP BY, CTEs, and windows | [Analytics](#groups-ctes-and-window-functions) |
| Traverse a known tree | WITH RECURSIVE | [Traversal](#recursive-traversal) |
| Choose a string, numeric, or time function | Expressions with results | [Functions](#functions-for-everyday-queries) |

[PostgreSQL reference](README.md)

| Item | Details |
| --- | --- |
| Levels | Basic for the complete example and CRUD. Intermediate for groups and windows. Advanced for recursion. |
| Prerequisites | PostgreSQL 18, `createdb`, `psql`, and a role that can create the practice database |

<a id="полный-пример-учебная-база"></a>

<a id="посчитать-оплаты-всех-пользователей"></a>
## Total paid orders for all users

Calculate order totals for all users, including users without orders.
Prepare `demo.users`, `demo.products`, and `demo.orders` using the [complete SQL example and commands](query-lab.md#complete-practice-database-example).
Then run this PostgreSQL 18 snippet.

```sql
SELECT u.username, COALESCE(SUM(o.amount), 0) AS paid_total
FROM demo.users AS u
LEFT JOIN demo.orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.username
ORDER BY u.username;
```

The result is `alice | 140.00`, `bob | 300.00`, `carol | 0`.
The condition in `ON` preserves users without paid orders.
The schema demonstrates queries and constraints. A complete sales workflow requires additional logic.
Run every dependent snippet on this page in `cheatsheet_demo` after setup.

<a id="выбрать-строки-и-объединить-таблицы"></a>
## Select rows and join tables

Find products within a price range, order details, or users without orders.

**Basic.** Run these independent SQL snippets on the practice schema.

```sql
SELECT id, name, price
FROM demo.products
WHERE price BETWEEN 40 AND 100
ORDER BY price, id
LIMIT 10 OFFSET 0;

SELECT o.id, u.username, p.name, o.amount
FROM demo.orders AS o
JOIN demo.users AS u ON u.id = o.user_id
JOIN demo.products AS p ON p.id = o.product_id
WHERE o.status = 'paid'
ORDER BY o.id;

SELECT u.username
FROM demo.users AS u
WHERE NOT EXISTS (SELECT 1 FROM demo.orders AS o WHERE o.user_id = u.id);
```

The first query returns `Mouse` and `Keyboard`.
The second returns three orders sorted by ID.
The user without orders is `carol`.
`INNER JOIN` keeps matches.
`LEFT JOIN` preserves rows from the left.
`RIGHT JOIN` preserves rows from the right.
`FULL JOIN` preserves rows from both sides.
`CROSS JOIN` produces all combinations.
After LEFT JOIN, a WHERE filter on the right table can remove unmatched rows.
The complete example therefore puts the `status` filter in ON.

`UNION` removes duplicates.
`UNION ALL` preserves duplicates.
`INTERSECT` keeps rows common to both results.
`EXCEPT` keeps rows from the first result that are absent from the second.
The results must have the same number of columns with compatible types.
Use `IS NULL` to check for a missing value.

<a id="изменить-данные-и-проверить-результат"></a>
## Change data and check the result

Change a specific row and return its actual new value.

**Basic and intermediate.** The SQL snippets run independently and end in ROLLBACK.
They change data temporarily.
An identity sequence can advance even when the transaction rolls back.

```sql
BEGIN;
INSERT INTO demo.users (username, email)
VALUES ('dave', 'dave@example.test')
RETURNING id, username;
ROLLBACK;

BEGIN;
INSERT INTO demo.users (username, email)
VALUES ('alice', 'alice@example.test')
ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
RETURNING username, email;
ROLLBACK;

BEGIN;
UPDATE demo.products SET price = price * 1.10
WHERE id = 2 RETURNING name, price;
ROLLBACK;

BEGIN;
DELETE FROM demo.users AS u
WHERE u.username = 'carol'
  AND NOT EXISTS (SELECT 1 FROM demo.orders AS o WHERE o.user_id = u.id)
RETURNING username;
ROLLBACK;
```

Expect `dave` with a new ID, `alice | alice@example.test`, `Mouse | 44.00`, and `carol`.
After each rollback, the data return to their original state.
An upsert needs a suitable UNIQUE constraint or primary key.
A conflict with another constraint, such as email, can still cause an error.
The general INSERT from SELECT form is `INSERT INTO target (col1, col2) SELECT col1, col2 FROM source`.
Substitute your own tables and columns.

Before a bulk UPDATE or DELETE, check the same WHERE condition with SELECT.
Without WHERE, the statement affects every row.
`TRUNCATE` removes all rows and locks the table exclusively.
You can roll it back.
With CASCADE, it also truncates related tables.
The examples require none of these cleanup commands.

<a id="группы-cte-и-оконные-функции"></a>
## Groups, CTEs, and window functions

Calculate totals per user and each order's position while preserving individual rows.

**Intermediate.** Run these independent read-only SQL snippets.

```sql
WITH totals AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
    FROM demo.orders
    GROUP BY user_id
    HAVING COUNT(*) >= 2
)
SELECT u.username, t.order_count, t.total
FROM totals AS t JOIN demo.users AS u ON u.id = t.user_id;

SELECT id, amount,
       ROW_NUMBER() OVER (ORDER BY amount DESC, id) AS position,
       SUM(amount) OVER (
           ORDER BY ordered_at, id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total,
       LAG(amount) OVER (ORDER BY ordered_at, id) AS previous_amount
FROM demo.orders
ORDER BY ordered_at, id;
```

The first query returns `alice | 2 | 140.00`. The second returns the following rows.

| id | amount | position | running_total | previous_amount |
| --- | --- | --- | --- | --- |
| 1 | 100.00 | 2 | 100.00 | NULL |
| 2 | 40.00 | 3 | 140.00 | 100.00 |
| 3 | 300.00 | 1 | 440.00 | 40.00 |

`PARTITION BY user_id` calculates results separately for each user.
`RANK` leaves gaps after ties.
`DENSE_RANK` assigns consecutive ranks.
Additional sort keys affect which rows tie.
`LEAD` reads a subsequent row.
`AVG(...) OVER (...)` calculates a window average.
For a share of the total, use `amount / NULLIF(SUM(amount) OVER (), 0)`.
Here amount is numeric.

`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` covers seven rows.
For a time interval, choose a suitable RANGE and time column.
For neighboring groups with equal sort keys, use GROUPS.
`LAST_VALUE` depends on the frame.
To read the last value in the entire partition, use `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

<a id="рекурсивный-обход"></a>
## Recursive traversal

For a known manager hierarchy without cycles, return each employee and their depth from the root.

**Advanced.** This standalone SQL snippet requires no additional tables.

```sql
WITH RECURSIVE employees(id, name, manager_id) AS (
    VALUES (1, 'Lead', NULL::integer), (2, 'Developer', 1), (3, 'Intern', 2)
), tree AS (
    SELECT id, name, manager_id, 1 AS depth
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees AS e JOIN tree AS t ON e.manager_id = t.id
)
SELECT name, depth FROM tree ORDER BY depth, id;
```

The result is `Lead | 1`, `Developer | 2`, `Intern | 3`.
For an arbitrary graph, add a depth limit or cycle detection, for example with `CYCLE`.
The simple recursion here assumes a known tree.

<a id="функции-для-повседневных-запросов"></a>
## Functions for everyday queries

**Basic and intermediate.** The table contains standalone SELECT expressions and function forms.
Replace fields in the general forms with your own.

| Task | Example or form | Result or limitation |
| --- | --- | --- |
| Find a string | `SELECT POSITION('SQL' IN 'PostgreSQL');` | `8`. Positions start at 1. |
| Extract a substring | `SELECT SUBSTRING('PostgreSQL' FROM 1 FOR 4);` | `Post` |
| Process text | `LOWER`, `UPPER`, `TRIM`, `REPLACE`, `CONCAT`, `STRING_TO_ARRAY`, `UNNEST` | `CONCAT` and `||` handle NULL differently |
| Round an exact value | `SELECT ROUND(123.456, 2);` | `123.46`. The two-argument overload accepts numeric. |
| Calculate | `ABS`, `CEIL`, `FLOOR`, `POWER`, `SQRT`, `LN`, `LOG`, `MOD` | Check argument types. Integer division truncates the fractional part. |
| Generate a pseudorandom number | `SELECT RANDOM();` | `0 <= x < 1`. Use a cryptographic source for secrets. |
| Get the start of a month | `SELECT DATE_TRUNC('month', TIMESTAMP '2026-11-06 14:30');` | `2026-11-01 00:00:00` |
| Get the current time | `CURRENT_DATE`, `CURRENT_TIMESTAMP`, `NOW()` | The timestamp refers to the start of the transaction. Use `clock_timestamp()` for the current instant. |
| Parse or format | `EXTRACT`, `TO_CHAR`, `TO_DATE`, `TO_TIMESTAMP`, `AGE` | Account for the type and time zone |
| Handle conditions and NULL | `CASE`, `COALESCE`, `NULLIF`, `GREATEST`, `LEAST` | `COALESCE` chooses the first non-NULL value |

<a id="источники"></a>
## Sources

- [INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html), [UPDATE](https://www.postgresql.org/docs/18/sql-update.html), [DELETE](https://www.postgresql.org/docs/18/sql-delete.html).
- [Joins and grouping](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTEs and recursion](https://www.postgresql.org/docs/18/queries-with.html).
- [Window functions](https://www.postgresql.org/docs/18/functions-window.html), [window frames](https://www.postgresql.org/docs/18/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).
- [String functions](https://www.postgresql.org/docs/18/functions-string.html), [math](https://www.postgresql.org/docs/18/functions-math.html), [dates and times](https://www.postgresql.org/docs/18/functions-datetime.html).
