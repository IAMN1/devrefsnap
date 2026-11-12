<a id="устранить-n1-и-выбрать-загрузку-отношений"></a>
# Eliminate N+1 and choose relationship loading

[Русский](../../../../ru/python/databases/sqlalchemy/relationship-loading.md)

Use this page when reading relationships creates additional SQL queries or returns unexpected collection contents.
Choose a technique based on the required data and query constraints.
[SQLAlchemy reference](README.md) · [Model schema](models-and-transactions.md#shared-schema-for-the-recipes).
For an introduction, open the [standalone synchronous N+1 example](n-plus-one.md#setup-and-run) with two models in one file.

<a id="быстрый-поиск"></a>
## Quick lookup

| Situation | Technique | Card / example |
| --- | --- | --- |
| Reading collections issues too many database queries | Count queries in a fresh session (`Session`) | [Find N+1](#find-n1) · [Standalone program](n-plus-one.md#full-program) |
| All posts are needed for a list of users | `selectinload` issues a separate SELECT for a group | [Choice and cost](#choose-a-strategy) · [Card](#load-collections-with-selectinload) |
| A small collection is needed without a separate SELECT | `joinedload` includes related rows in the same SELECT | [Collection and unique](#load-a-collection-with-joinedload) |
| The author of each post is needed | Compare repeated fields and SELECT counts | [Scalar relationship](#load-a-scalar-relationship) |
| Unexpected loading must raise an error | `raiseload` prevents relationship loading on attribute access | [Prevent lazy loading](#detect-unplanned-lazy-loading) |
| Filter by a child table and retrieve the complete collection | Explicit JOIN + `selectinload` | [Filter parents](filtered-relationships.md#filter-parents-and-load-complete-collections) |
| Only a selected part of the collection is needed | `contains_eager` populates the relationship from a custom JOIN | [Load a partial collection](filtered-relationships.md#load-a-partial-collection-from-a-join) |
| The collection is already loaded | `populate_existing` explicitly refreshes object state | [Refresh a loaded collection](filtered-relationships.md#refresh-an-already-loaded-collection) |
| The result does not fit in memory | Choose batch processing separately | [Large result sets](streaming.md) |

| Parameter | Value |
| --- | --- |
| Level | Intermediate. Partial collections and Session state are advanced |
| Prerequisites | For N+1, Python and SELECT basics are enough for [one file with explanations](n-plus-one.md). The other cards use SQL JOINs, Session, `demo_models.py`, and `seed()` from the [lab setup](loading-lab.md#prepare-the-examples) |
| Standalone N+1 | [Separate program, versions, and scope](n-plus-one.md#result-and-limits). The [extended set](loading-lab.md) uses the shared schema |
| Dependencies | Synchronous SQLAlchemy 2.1.8 ORM and in-memory SQLite. See [setup](loading-lab.md#prepare-the-examples) |

<a id="выбрать-стратегию"></a>
## Choose a strategy

First, identify the parents and relationships you need.
The ORM maps table rows to Python objects.
A parent here is an object from the original query, such as a user in `select(User)`.
`User.posts` is a user's post collection, and `Post.author` is a single author.
A collection can be empty. An optional scalar relationship can contain `None`.
Specify whether you need the complete collection, part of it, or one related object.
Then assess the row count, row width, and acceptable number of database round trips.
Row width depends on the selected columns and the size of their values.

The identity map within a Session associates a row identifier with an already loaded object.
Lazy loading loads a relationship when an unloaded attribute is accessed.
Eager loading loads a relationship ahead of time through the original query or additional SELECTs.
Both `selectinload` and `joinedload` perform eager loading.

| Required data and constraints | Starting point | Cost and reason to reconsider |
| --- | --- | --- |
| All collections for a list of parents, with varying or large collection sizes | `selectinload` | Additional SELECTs for batches of keys. Parent fields are not repeated for each child |
| A small, bounded set of parents and children, with a separate SELECT undesirable | Compare `joinedload` with `selectinload` | The JOIN repeats parent fields for each child. A collection requires `unique()` |
| One related object per row, with acceptable repetition of its fields | Usually `joinedload` | This relationship adds no rows, but related-object fields are repeated |
| Many rows reference the same objects with large fields | Compare scalar-relationship `selectinload` with `joinedload` | An additional SELECT may reduce repeated field transfer. Measure any improvement |
| The relationship may be unused | Lazy loading | Reading may execute SQL. For a simple many-to-one relationship, the identity map sometimes avoids a SELECT |
| Unplanned access must raise an error | `raiseload` | Raises on lazy access. SQL required during flush can still execute |
| Only a selected part of a collection is needed | Filter and `contains_eager` | Make the collection's partial nature explicit. See the [card](filtered-relationships.md#load-a-partial-collection-from-a-join) |

For a collection, one parent can correspond to several SQL result rows.
`unique()` retains one ORM object per identity in the Python result. The transferred SQL rows remain the same.
Several independent collections in one SELECT can multiply the number of rows for one parent.
Choose a strategy separately for each relationship.
One SELECT does not guarantee lower execution time, memory use, or network traffic.

<a id="учесть-ограничения-запроса"></a>
### Account for query constraints

A PK is a primary key that uniquely identifies a table row.
`LIMIT` restricts the row count, and `OFFSET` skips the beginning of the result.
`yield_per` reads the result in batches without accumulating the entire result at once.

| Condition | What to check |
| --- | --- |
| A parent page with `LIMIT` / `OFFSET` | Limit parents with a stable `ORDER BY`, such as the PK. Select-in loads the selected page's collections separately |
| The same page with collection joinedload | SQLAlchemy wraps the original SELECT in a subquery before adding the loading JOIN. Check SQL complexity and row volume. `LIMIT` permits joinedload |
| An explicit JOIN to the child table with `LIMIT` | The limit can apply to joined rows, giving fewer distinct parents. A subsequent `unique()` cannot repair the page |
| A composite primary key with several identifier columns | Select-in requires tuple IN to test a list of key tuples. SQL Server does not support this syntax. Consider further strategies |
| Batch reading with `yield_per` | Collection joinedload is incompatible. Select-in depends on independent-cursor support in the driver. See the [separate guide](streaming.md#combine-batch-processing-with-relationship-loading) |
| Row locking with `SELECT … FOR UPDATE` | The loading JOIN can cause the related table to be locked. Check database behavior before choosing joinedload |

For composite keys on SQL Server, consider [subqueryload](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#subquery-eager-loading) and its limitations.

The N+1 card uses the [standalone program](n-plus-one.md).
The other snippets use a prepared `engine` and a fresh Session for each comparison.
[Complete dependencies and setup](loading-lab.md#prepare-the-examples) are listed separately.

<a id="найти-n1"></a>
## Find N+1

**Situation** — a list of users is loaded first, then the code reads `user.posts` for each user.
With lazy loading, the first read of an unloaded collection executes a SELECT.
For N users, this produces N+1 queries, with one query for the list and N queries for the collections.

The [standalone program](n-plus-one.md#setup-and-run) contains two models, in-memory SQLite setup, and the run command.

**Example fragment from the program's `read_users` function without eager loading**

```python
stmt = select(User).order_by(User.id)
users = session.scalars(stmt).all()
rows = [(user.name, sorted(post.title for post in user.posts)) for user in users]
```

`session` is a fresh `Session` inside `read_users`. The session executes queries and maintains object state.
`select(User)` defines the query, and `session.scalars(stmt).all()` executes it and returns a list of users.

**Change** — add `.options(selectinload(User.posts))` to the user query.
This technique reads the posts for a group of users ahead of time with a separate SELECT using an `IN` condition.
This advance loading is called eager loading.
The [complete program compares both variants](n-plus-one.md#full-program) and counts SELECTs through the end of collection access.

**Practice dataset result** — `[('alice', ['Python', 'SQL']), ('bob', [])]` in both variants.
A fresh Session executes three SELECTs with lazy loading and two with `selectinload`.
Even Bob's empty collection requires loading.
Count queries through the end of relationship access, including response serialization.
State in an earlier Session can hide additional queries.
Query counts depend on data volume and loading structure. Two SELECTs are specific to these conditions.
After measuring, [choose a loading strategy](#choose-a-strategy) based on collection size and the cost of a database round trip.
The [minimal example's limitations](n-plus-one.md#result-and-limits) and [complete lab](loading-lab.md#compare-strategies-and-check-limitations) are described separately.

<a id="загрузить-коллекции-через-selectinload"></a>
## Load collections with selectinload

**Situation** — all posts are needed for a list of users, including empty collections.
Collection sizes may differ. Repeating user fields for each post is undesirable.
**Change** — start with `selectinload` if an additional SELECT is acceptable.
The model's simple foreign key supports this loading strategy.

**Example fragment using the prepared `engine`**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(selectinload(User.posts)).order_by(User.id)
    ).all()
    sizes = [len(user.posts) for user in users]
```

**Practice dataset result** — `sizes == [2, 0]`, with two SELECTs instead of three.
For a larger result set, the SELECT count depends on the number of key batches and relationship levels.
A composite key requires tuple IN, an `IN` condition with a list of key tuples. Support depends on the database system.
For example, SQL Server does not support this form of select-in loading for a composite key.
For nested comments, add `selectinload(User.posts).selectinload(Post.comments)`.
This adds a separate loading level and additional queries.
[Count and content checks](loading-lab.md#compare-strategies-and-check-limitations)

<a id="загрузить-коллекцию-через-joinedload"></a>
## Load a collection with joinedload

**Situation** — users and all their posts are required. The parent set and collections are small.
An additional database round trip is undesirable, and repeated user fields are acceptable.
**Change** — compare `joinedload` with select-in loading on the same data.
Add `unique()` when reading the collection result.

**Example fragment using the prepared `engine`**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(joinedload(User.posts)).order_by(User.id)
    ).unique().all()
    sizes = [len(user.posts) for user in users]
```

**Practice dataset result** — the same `[2, 0]`, with one SELECT.
SQL returns three rows, with two rows for Alice's posts and one for Bob without posts.
Alice's fields are transferred twice, although Python returns one Alice user object.
By default, LEFT OUTER JOIN retains users without posts.
LEFT OUTER JOIN returns a left-hand row even when a related right-hand row is absent.
Without `unique()`, SQLAlchemy requires explicit duplicate handling and raises `InvalidRequestError` when the result is read.
`unique()` does not reduce the number of rows transferred from the database.
Large collections and several JOINs can substantially increase the SQL result size.
`joinedload` cannot replace an explicit `join()` used to filter by a child table.
[Success check and failure without unique](loading-lab.md#compare-strategies-and-check-limitations)

<a id="загрузить-одиночную-связь"></a>
## Load a scalar relationship

**Situation** — each post in a list needs its author.
Repeated author fields have an acceptable size. Retrieving the data with one SELECT is preferred.
**Change** — start with `joinedload(Post.author)`.
`Post.author` is a many-to-one relationship. Many posts can reference one author.

**Example fragment using the prepared `engine`**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from demo_models import Post

with Session(engine) as session:
    posts = session.scalars(
        select(Post).options(joinedload(Post.author)).order_by(Post.id)
    ).all()
    authors = [post.author.name for post in posts]
```

**Practice dataset result** — two `alice` names and one SELECT.
A scalar relationship does not multiply rows as a collection does. This case does not require `unique()`.
By default, `joinedload` uses LEFT OUTER JOIN and retains parents without a related object.
If many posts reference one author with large fields, compare select-in loading.
In the same snippet, replace the option with `selectinload(Post.author)` and import `selectinload` from `sqlalchemy.orm`.
For the two practice posts, this retrieves the same authors through two SELECTs.
The first SELECT reads posts. The second reads their shared author once, avoiding repeated author fields in every post row.
With joinedload, SQL transfers Alice's fields twice, although the identity map creates one author object.
The identity map itself does not reduce the SQL result data.
For a simple lazy many-to-one relationship, an already loaded author sometimes avoids an additional SELECT.

Avoid enabling `innerjoin=True` solely to reduce the row count.
INNER JOIN retains only rows with a matching related object.
For an optional relationship, this JOIN excludes parents without that object.
Use it only when the related object's presence is guaranteed or excluding such parents is intentional.
[Complete check](loading-lab.md#compare-strategies-and-check-limitations)

<a id="обнаружить-незапланированную-lazy-загрузку"></a>
## Detect unplanned lazy loading

**Situation** — unexpected SQL during response construction must fail a test.
Allow the required relationship and prevent other lazy loads.

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, raiseload, selectinload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(selectinload(User.posts), raiseload("*")).order_by(User.id)
    ).all()
    sizes = [len(user.posts) for user in users]
    # Accessing the unloaded users[0].profile raises InvalidRequestError.
```

**Result** — posts are available. Accessing an unloaded profile raises an error without issuing a SELECT.
The `"*"` wildcard also applies to relationships of loaded child objects.
`raiseload` applies to relationships. It does not cover all scalar columns.
An internal flush can perform required loads while bypassing `raiseload`.
[Check the error and verify that no SELECT runs](loading-lab.md#compare-strategies-and-check-limitations)

## Filtering and collection state

<a id="отфильтровать-родителей-и-загрузить-полные-коллекции"></a>
<a id="filter-parents-and-load-complete-collections"></a>

- [Filter parents and load complete collections](filtered-relationships.md#filter-parents-and-load-complete-collections)

<a id="загрузить-частичную-коллекцию-из-join"></a>
<a id="load-a-partial-collection-from-a-join"></a>

- [Load a partial collection from a JOIN](filtered-relationships.md#load-a-partial-collection-from-a-join)

<a id="обновить-уже-загруженную-коллекцию"></a>
<a id="refresh-an-already-loaded-collection"></a>

- [Refresh an already loaded collection](filtered-relationships.md#refresh-an-already-loaded-collection)

<a id="проверить-выбор"></a>

[Run the complete lab with loading comparisons and failure checks](loading-lab.md).
The practice SELECT count does not measure application speed improvements.

<a id="источники"></a>
## Sources

- [Choosing relationship loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#what-kind-of-loading-to-use), [select-in](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#select-in-loading), [joined loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#joined-eager-loading).
- [Raiseload](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#preventing-unwanted-lazy-loads-using-raiseload).
- [Batch reading and limitations](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#fetching-large-result-sets-with-yield-per).
- [Release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
