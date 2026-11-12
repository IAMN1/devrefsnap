<a id="проверить-n1-и-стратегии-загрузки"></a>
# Check N+1 and loading strategies

[Русский](../../../../ru/python/databases/sqlalchemy/loading-lab.md)

Compare SELECT counts on identical data and check relationship contents.
The scenario uses only a fresh in-memory SQLite database.
[Selection cards](relationship-loading.md) · [Large result sets](streaming.md) · [Reference](README.md).
For an introduction to N+1, start with [two models in one file](n-plus-one.md#setup-and-run).
Use the extended schema below for nested relationships and the [filtering and refresh cards](filtered-relationships.md).

| Task | Check | Where |
| --- | --- | --- |
| Observe N+1 and compare eager loading | Contents and SELECT counts in fresh Sessions | [Complete test file](#compare-strategies-and-check-limitations) |
| Check failure | Joined collection without unique, and an unloaded relationship with raiseload | [Same file](#compare-strategies-and-check-limitations) |
| Check a parent page and an optional relationship | LIMIT retains complete collections. LEFT OUTER JOIN retains parents without a related object | [Same file](#compare-strategies-and-check-limitations) |
| Check a partial collection | JOIN filter, identity map, and expiration | [Same file](#compare-strategies-and-check-limitations) |

| Parameter | Value |
| --- | --- |
| Level | Intermediate. Session state and contains_eager are advanced |
| Prerequisites | Python 3.14, SQLAlchemy, and pytest. Schema from demo_models.py and data from demo_queries.py |

<a id="подготовить-примеры"></a>
## Prepare the examples

Create a separate practice directory and virtual environment.
Save the [complete schema](models-and-transactions.md#shared-schema-for-the-recipes) as `demo_models.py`.
Save the [data setup and queries](queries.md#select-join-subqueries-and-ctes) as `demo_queries.py`.
Save [`test_relationship_loading.py`](../../../../../examples/python/databases/sqlalchemy/test_relationship_loading.py) next to those files.
Install the dependencies in the practice environment.

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'pytest==9.2.0'
```

The `asyncio` extra installs greenlet, which is required to import AsyncAttrs from the shared model.
The model requires this even though the loading checks below are synchronous.
Use Python 3.14 and SQLite from the standard `sqlite3` module.

The original `seed()` creates Alice with Python and SQL posts, plus Bob without posts.
The fixture creates a separate database for each test.
Some comparisons add three more users without posts.
Two posts reference the same author, Alice.
`User.manager` is optional. Alice manages Bob, and Alice has no manager.
All compared loaders start reading in a fresh Session.
Data inserts and table creation are excluded from the SELECT counter.

For the short cards, prepare `engine` with this snippet after saving the two modules.

```python
from sqlalchemy.orm import Session
from demo_models import new_engine
from demo_queries import seed

engine = new_engine()
with Session(engine) as session, session.begin():
    seed(session)
```

After checking the cards, run `engine.dispose()`.
The complete test's fixture disposes of the engine automatically.

<a id="сравнить-стратегии-и-проверить-ограничения"></a>
## Compare strategies and check limitations

The complete `test_relationship_loading.py` counts SELECTs executed by this engine.
The counter intercepts SQL sent through the driver. It does not assess query-plan cost.
Reading `user.posts` is included in the measurement.
Relationships start unloaded, except in the explicitly named identity-map checks.

[`sqlalchemy/test_relationship_loading.py`](../../../../../examples/python/databases/sqlalchemy/test_relationship_loading.py)

Run `python -m pytest -q test_relationship_loading.py`.
**Expected result** — all checks pass.
The test for access after Session closure does not commit or expire state.
If state expired before closure, this test does not guarantee data access without a Session.

<a id="прочитать-результаты-сравнения"></a>
## Read the comparison results

The values below are checked in `test_same_collections_and_select_counts`.
Conditions include one `User.posts` collection, fresh Sessions, identical data, and complete collection access.

| Users | Lazy | Select-in | Joined |
| --- | --- | --- | --- |
| Alice and Bob | 3 SELECTs | 2 SELECTs | 1 SELECT |
| The same users plus three users without posts | 6 SELECTs | 2 SELECTs | 1 SELECT |

For the scalar `Post.author` relationship, the test compares the same two posts by one author in fresh Sessions.
Many-to-one means that many posts can reference one author.

| Author loading strategy | SELECTs including post retrieval | Resulting objects |
| --- | --- | --- |
| Lazy | 2 | Two posts and one shared Alice object |
| Select-in | 2 | The same objects. A separate SELECT reads the author |
| Joined | 1 | The same objects. Both SQL rows contain the author's fields |

The identity map stores already loaded objects by identity within a Session.
It reuses the author and avoids a second SELECT for Alice during lazy loading.
It does not eliminate repeated author fields in SQL with joinedload.
`test_joined_collection_sql_rows_repeat_parent` separately demonstrates three SQL rows for two users.
Two rows contain Alice with her posts. The third retains Bob without posts.
The SQL row count differs from the ORM object count returned after `unique()`.

The page test with `LIMIT 1` checks one user and both posts for both strategies.
A separate explicit-JOIN test shows why `LIMIT 2` does not guarantee two distinct parents.
The `User.manager` test checks that Alice with a `None` value is retained by both strategies.
In a separate test, reading a joinedload collection without `unique()` raises `InvalidRequestError`.
Nested comments loading adds a third SELECT in a separate test.
These results apply only to these conditions and versions.
They do not measure application speed improvement, memory use, or network traffic.
Other database systems, composite keys, locks, and concurrent access require separate checks.

<a id="источники"></a>
## Sources

- [Greenlet and installation in SQLAlchemy 2.1](https://docs.sqlalchemy.org/en/21/faq/installation.html#i-m-getting-an-error-about-greenlet-not-being-installed-when-i-try-to-use-asyncio).

- [Relationship loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html), [SQL execution events](https://docs.sqlalchemy.org/en/21/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute).
- [Populate existing](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#populate-existing), [release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
