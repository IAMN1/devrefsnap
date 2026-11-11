<a id="обработать-большую-выборку-по-частям"></a>
# Process a large result set in batches

[Русский](../../../../ru/python/databases/sqlalchemy/streaming.md)

Use this page to limit the number of ORM objects created at once while reading a result.
Relationship-loading choices are covered [separately](relationship-loading.md).
[Reference](README.md) · [Model schema](models-and-transactions.md#shared-schema-for-the-recipes).

| Situation | Technique | Example |
| --- | --- | --- |
| The result must be read in batches | `yield_per` and `partitions()` | [Processing card](#read-a-result-in-batches) |
| Collections are needed along with parents | Check loader and driver compatibility | [Limitations table](#combine-batch-processing-with-relationship-loading) |
| The checks need to be repeated | Practice SQLite database and pytest | [Complete test file](#check-processing-and-incompatible-combinations) |

| Parameter | Value |
| --- | --- |
| Level | Advanced |
| Prerequisites | Session and iterators. demo_models.py and demo_queries.py from the [setup](loading-lab.md#prepare-the-examples) |
| Dependencies | Python 3.14, SQLAlchemy 2.1.8, and SQLite. See [setup](loading-lab.md#prepare-the-examples) |

<a id="читать-результат-партиями"></a>
## Read a result in batches

**Situation** — process users without assembling the entire result into a list.
The snippet uses the prepared `engine` from the [practice dataset](loading-lab.md#prepare-the-examples).

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from demo_models import User

with Session(engine) as session:
    result = session.scalars(
        select(User).order_by(User.id).execution_options(yield_per=100)
    )
    for batch in result.partitions():
        for user in batch:
            print(user.name)
```

**Practice dataset result** — `alice` and `bob` are printed.
`100` is the batch size in this snippet. Choose a suitable size for your workload.
Avoid `.all()`, which collects the entire result in memory again.
Avoid accumulating processed objects in a shared list unless required.
Cursor behavior and driver buffering affect memory use.
The [complete check](#check-processing-and-incompatible-combinations) uses batch size `1` to check batch boundaries.

<a id="совместить-с-загрузкой-отношений"></a>
## Combine batch processing with relationship loading

| Combination | Application | Limitation |
| --- | --- | --- |
| `yield_per` without eager collections | Item-by-item or batch processing | Does not guarantee a memory bound for the entire application |
| `yield_per` + `selectinload` | Possible with driver support for independent cursors | Secondary queries run per batch. SELECT counts can increase |
| `yield_per` + collection `joinedload` | Incompatible | The ORM needs to accumulate collection rows |
| `yield_per` + collection `subqueryload` | Incompatible | Choose a different reading approach |
| `yield_per` + `Result.unique()` | Incompatible | Unique stores a set of identities encountered |

The SQLite example checks `selectinload` with batches.
This does not verify equivalent cursor support in another driver.
For N+1, first [choose the relationships to load](relationship-loading.md#choose-a-strategy).
Then check batch processing separately on the required database system and driver.

<a id="проверить-обработку-и-несовместимые-сочетания"></a>
## Check processing and incompatible combinations

The complete `test_streaming.py` uses the same models and original `seed()`.
Save the file next to `demo_models.py` and `demo_queries.py`.
Install `sqlalchemy[asyncio]==2.1.8` and `pytest==9.2.0` in a separate environment.
The fixture creates and disposes of an in-memory SQLite database for each test.

[`sqlalchemy/test_streaming.py`](../../../../../examples/python/databases/sqlalchemy/test_streaming.py)

Run `python -m pytest -q test_streaming.py`.
**Result** — all checks pass.
The test's `names` list checks the complete result. The practical card processes objects immediately.
The exceptions verify incompatible combinations. They do not provide load-test results.

<a id="источники"></a>
## Sources

- [ORM yield_per and limitations](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#fetching-large-result-sets-with-yield-per), [buffering and server-side cursors](https://docs.sqlalchemy.org/en/21/core/connections.html#using-server-side-cursors-a-k-a-stream-results).
- [Release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
