<a id="проектировать-схему-индексы-и-поиск"></a>
# Design schemas, indexes, and search

[Русский](../../../../ru/databases/relational/postgresql/schema-and-indexes.md)

Use this page to define data constraints, change a schema, and choose indexes in PostgreSQL 18.
Runnable snippets use the `demo` practice schema. Query plans and locking behavior depend on the workload.

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Technique | Example or details |
| --- | --- | --- |
| Choose a data representation and valid values | Types, identity, foreign keys, and CHECK | [Types and constraints](#types-and-constraints) |
| Change a schema and check rollback | ALTER TABLE in a transaction | [Schema changes](#change-a-table-or-schema) |
| Choose an index for filtering and sorting | B-tree, partial index, and EXPLAIN | [Indexes](#indexes-and-query-plans) |
| Search JSON fields or text | JSONB and full-text search with GIN | [Search](#jsonb-and-full-text-search) |
| Distribute data by date range | RANGE partitions | [Partitioning](#partitioning) |
| Store a query result snapshot or prepare a session query | MATERIALIZED VIEW and PREPARE | [Views](#views-and-prepared-statements) |

[PostgreSQL reference](README.md)

| Item | Details |
| --- | --- |
| Levels | Basic for types and constraints. Intermediate for DDL and indexes. Advanced for JSONB, full-text search, and partitions. |
| Prerequisites | PostgreSQL 18, `cheatsheet_demo` and the schema from [queries.sql](query-lab.md#complete-practice-database-example), connected as the owner |

<a id="типы-и-ограничения"></a>
## Types and constraints

Choose types and constraints to preserve numerical precision, time semantics, and valid relationships.

**Basic.** The complete example already defines the main schema.
Use this type reference when adapting it.

| Data | Type or construct | Important property |
| --- | --- | --- |
| Integers | `smallint`, `integer`, `bigint` | 2, 4, and 8 bytes. Choose based on range. |
| Generated key | `bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | Identity generates values. PRIMARY KEY enforces uniqueness and NOT NULL. |
| Older schemas | `serial`, `bigserial` | Shorthand for a column with a sequence |
| Exact numbers | `numeric(10, 2)` / `decimal(10, 2)` | Exact decimal arithmetic, with precision and scale limited by the declaration |
| Approximate numbers | `real`, `double precision` | Use an exact type when monetary arithmetic requires decimal precision |
| Text and bytes | `text`, `varchar(n)`, `char(n)`, `bytea` | `varchar(n)` limits length. `char(n)` adds padding spaces. |
| Boolean | `boolean` | true, false, or NULL unless NOT NULL is specified |
| Instant | `timestamptz` | Stores an instant. Output depends on TimeZone, and the original zone name is lost. |
| Local date or time | `date`, `time`, `timestamp`, `interval` | A timestamp without time zone alone cannot identify a global instant |
| Structured data | `json`, `jsonb`, `integer[]`, `text[]` | JSONB has dedicated operators and GIN support. Assess relational modeling separately from arrays. |
| Identifiers | `uuid` | Built-in `gen_random_uuid()` needs no uuid-ossp extension |
| Specialized data | Enums, ranges, `inet`/`cidr`, geometry types | See the [type catalog](https://www.postgresql.org/docs/18/datatype.html) for details and supported operators |

`CHECK (price >= 0)` permits NULL.
Add NOT NULL when a value is required.
PRIMARY KEY and UNIQUE create indexes to enforce uniqueness.
Avoid manually duplicating those indexes.
A foreign key leaves indexing of the referencing column to you.
Assess the need based on queries and deletes.
`ON DELETE CASCADE` deletes related rows.
`RESTRICT` prevents deletion of a referenced row.

<a id="изменить-таблицу-и-схему"></a>
## Change a table or schema

Add a column, change price precision, and forbid empty names in the practice schema.
Check the changes with rollback first.

**Intermediate.** Run this SQL snippet in `cheatsheet_demo`.
It rolls back the changes to the practice table.

```sql
BEGIN;
ALTER TABLE demo.users ADD COLUMN phone text;
ALTER TABLE demo.products ALTER COLUMN price TYPE numeric(12, 2);
ALTER TABLE demo.products ADD CONSTRAINT products_name_nonempty CHECK (name <> '');
ALTER TABLE demo.users RENAME COLUMN phone TO phone_number;
ROLLBACK;
```

After rollback, phone and phone_number are absent, and price remains numeric(10, 2).
ALTER TABLE can block access and rewrite data.
Assess conversion safety separately for a large table.
Once committed, dropping a column or constraint permanently removes data or protection.
CASCADE can remove dependent objects.

A schema is a namespace inside a database.
Explicit names such as `demo.users` avoid reliance on an implicit search_path.
Use the following DDL forms individually as a reference.

```text
CREATE SCHEMA schema_name AUTHORIZATION owner_role;
ALTER TABLE schema_name.table_name SET SCHEMA other_schema;
ALTER TABLE schema_name.table_name OWNER TO other_owner;
ALTER TABLE schema_name.table_name ALTER COLUMN col SET DEFAULT expression;
DROP SCHEMA schema_name CASCADE;  -- also removes its contents and dependencies
```

<a id="индексы-и-план-запроса"></a>
## Indexes and query plans

A query selects a user's orders and sorts by date. Another query searches unpaid orders.
Assess composite and partial indexes using actual query plans.

**Intermediate.** Run this SQL snippet after queries.sql.
It creates two persistent practice indexes once.

```sql
CREATE INDEX orders_user_date_idx ON demo.orders (user_id, ordered_at);
CREATE INDEX orders_pending_idx ON demo.orders (ordered_at) WHERE status = 'pending';

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, amount FROM demo.orders
WHERE user_id = 1 ORDER BY ordered_at;
```

Inspect the indexes in `psql` with `\d demo.orders`.
The plan depends on statistics, table size, and settings.
A sequential scan is normal for three rows.
EXPLAIN ANALYZE **executes** the query.
A statement that changes data produces real side effects.
Start optimization with a query plan and measurements.
Measure sequential scans before changing planner settings.

| Method or variant | When to consider it |
| --- | --- |
| B-tree, the default | Equality, ranges, and compatible ORDER BY clauses |
| hash | Equality. Measure its benefit compared with B-tree. |
| GIN | JSONB, arrays, and full-text search with a suitable operator class |
| GiST / SP-GiST | Specialized operators, geometry, ranges, and other supported structures |
| BRIN | Large tables whose values correlate with physical row order |
| Composite | Benefit depends on column order and query conditions. Some queries may still need single-column indexes. |
| Partial | The query condition must allow the planner to apply the index predicate |
| Expression | For example, `lower(username)`. The query must use a corresponding expression. |
| `varchar_pattern_ops` / `text_pattern_ops` | Support for accelerating prefix LIKE depends on the type, operator, and collation |

**Advanced.** Substitute your names into the forms below.
CONCURRENTLY allows ordinary writes during index construction.
It takes longer, has restrictions, and can wait for transactions.
Concurrent construction and parallel construction are separate concepts.
Run CONCURRENTLY outside an explicit transaction block.
After a failure, check for an invalid index.

```text
CREATE INDEX CONCURRENTLY index_name ON schema_name.table_name (column_name);
REINDEX INDEX schema_name.index_name;
REINDEX INDEX CONCURRENTLY schema_name.index_name;
ALTER INDEX schema_name.index_name RENAME TO new_index_name;
DROP INDEX schema_name.index_name;  -- removes the index; check dependencies and workload
```

<a id="jsonb-и-полнотекстовый-поиск"></a>
## JSONB and full-text search

A profile contains nested fields, and a product description contains searchable words.
Choose an operator suited to the data structure.

**Advanced.** Run these SQL snippets on the demo schema.
The first queries leave the data intact.

```sql
SELECT username, profile->>'city' AS city
FROM demo.users
WHERE profile @> '{"tags":["vip"]}'::jsonb;

SELECT username FROM demo.users WHERE profile ? 'city' ORDER BY username;

SELECT name FROM demo.products
WHERE to_tsvector('english', description) @@ plainto_tsquery('english', 'keyboard');
```

The first query returns `alice | Moscow`.
The second returns `alice` and `bob`.
The third returns `Keyboard`.
`->` returns JSON or JSONB.
`->>` returns text.
Here `?`, `@>`, and concatenation with `||` are JSONB operations.
Check operator support separately for json.
Use `jsonb_set` to update a nested value.
Use `jsonb_build_object`, `jsonb_agg`, or `jsonb_object_agg` to construct or aggregate values.

The following snippet creates persistent practice indexes once.

```sql
CREATE INDEX users_profile_gin ON demo.users USING GIN (profile);
CREATE INDEX products_fts_gin ON demo.products
USING GIN (to_tsvector('english', description));
```

Inspect them with `\d demo.users` and `\d demo.products` in psql.
To use the full-text index, the query expression and search configuration must match the index.
Choose a suitable configuration for the language, such as `russian` for Russian text.
The practice data use `english`.
Full-text search is built in.
unaccent and pg_trgm provide additional features.

<a id="партиционирование"></a>
## Partitioning

Measurements arrive by date, and November's rows should go into a separate partition.

**Advanced.** Run this standalone SQL snippet in `cheatsheet_demo`.
It creates a new table in demo.

```sql
BEGIN;
CREATE TABLE demo.measurements (
    measured_on date NOT NULL,
    city_id integer NOT NULL,
    temperature numeric(5, 2),
    PRIMARY KEY (measured_on, city_id)
) PARTITION BY RANGE (measured_on);

CREATE TABLE demo.measurements_2026_11 PARTITION OF demo.measurements
FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

INSERT INTO demo.measurements VALUES ('2026-11-06', 1, 5.50);
SELECT tableoid::regclass AS partition, measured_on FROM demo.measurements;
ROLLBACK;
```

Expect `demo.measurements_2026_11 | 2026-11-06`.
After rollback, the tables are absent.
The lower bound is inclusive and the upper bound is exclusive.
Without a matching or default partition, an out-of-range row causes an error.
Declarative partitioning and `INHERITS` inheritance are separate mechanisms.
Plan how to create and remove partitions.
Measure each query to determine whether partitioning helps.

<a id="представления-и-подготовленные-запросы"></a>
## Views and prepared statements

Store order totals as a refreshable snapshot and repeat a user query within one session.

**Intermediate and advanced.** This SQL snippet uses the demo schema and rolls back schema changes.

```sql
BEGIN;
CREATE MATERIALIZED VIEW demo.sales_summary AS
SELECT user_id, SUM(amount) AS total FROM demo.orders GROUP BY user_id;
REFRESH MATERIALIZED VIEW demo.sales_summary;
SELECT user_id, total FROM demo.sales_summary ORDER BY user_id;
ROLLBACK;

PREPARE demo_user_query (bigint) AS
SELECT username FROM demo.users WHERE id = $1;
EXECUTE demo_user_query(1);
DEALLOCATE demo_user_query;
```

Expect totals of `1 | 140.00` and `2 | 300.00`, plus the name `alice`.
A materialized view stores a result snapshot and needs refreshing.
An ordinary VIEW stores the query.
A TEMP table lasts for the session or until transaction end, depending on ON COMMIT.
PREPARE is session-scoped.
Application code usually uses driver parameters or driver-managed prepared statements.

<a id="источники"></a>
## Sources

- [Types](https://www.postgresql.org/docs/18/datatype.html), [identity](https://www.postgresql.org/docs/18/ddl-identity-columns.html), [constraints](https://www.postgresql.org/docs/18/ddl-constraints.html), [ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html).
- [Index types](https://www.postgresql.org/docs/18/indexes-types.html), [CREATE INDEX / CONCURRENTLY](https://www.postgresql.org/docs/18/sql-createindex.html), [EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html).
- [JSON and JSONB](https://www.postgresql.org/docs/18/functions-json.html), [full-text search indexes](https://www.postgresql.org/docs/18/textsearch-tables.html).
- [Partitioning](https://www.postgresql.org/docs/18/ddl-partitioning.html), [materialized views](https://www.postgresql.org/docs/18/rules-materializedviews.html).
