# Avoid N+1 queries when loading a collection

[Русский](../../../../ru/python/databases/sqlalchemy/n-plus-one.md)

Use this example if looping over users runs a separate SQL query for each user's posts.
The program reads the same data with two loading strategies. It uses two synchronous ORM models in one file.

| Task | Approach | Where to start |
| --- | --- | --- |
| Explain the extra queries | Compare lazy and eager loading | [Why N+1 happens](#why-n1-happens) |
| Run the example from scratch | Install SQLAlchemy and save one file | [Setup and run](#setup-and-run) · [Full program](#full-program) |
| Compare more loading strategies | Try `joinedload`, `raiseload`, and partial collections | [Extended lab](loading-lab.md) |

You need Python 3.14, SQLAlchemy 2.1.8, and Python's `sqlite3` module.
The example assumes that you know Python classes, type annotations, loops, context managers, `try`/`finally`, assertions, and basic SQL `SELECT`.
The program uses synthetic data in an in-memory SQLite database. The data disappears when the program exits.

## Why N+1 happens

The first `SELECT` reads the users. Reading an unloaded `user.posts` then runs another `SELECT` for each user.
For N users, that produces N+1 queries. An empty collection still requires a query.

An ORM maps table rows to Python objects. `User` represents a user, and `Post` represents a post.
`relationship` defines `User.posts` as the collection of posts for one user. `ForeignKey` identifies the column that links the tables.

Lazy loading fetches a relationship when you first access an unloaded attribute.
Eager loading fetches the related data while loading the users. With `selectinload`, a separate `SELECT` fetches posts for a batch of users with an `IN` condition.

Use `selectinload(User.posts)` in the query. This fragment shows the change in [the full program](#full-program).

```python
stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
```

`select(User)` describes the query. `Session` executes it and tracks loaded objects.
Here, `session.scalars(stmt).all()` returns a list of `User` objects.
Each comparison starts with a new `Session` so previously loaded posts cannot hide extra queries.

For two users, `selectinload` reduces the number of `SELECT` statements from three to two and returns the same posts.
Larger selections can require several batches of keys. Composite primary keys require database support for tuple `IN`.
See the [strategy table](relationship-loading.md#choose-a-strategy) for other options.

## Setup and run

Create a directory named `sqlalchemy-n-plus-one-demo`.
Save [n_plus_one.py](../../../../../examples/python/databases/sqlalchemy/n_plus_one.py) in that directory.
Open a terminal in the directory and run these commands on macOS or Linux.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install 'sqlalchemy==2.1.8'
python n_plus_one.py
```

The synchronous example needs SQLAlchemy and the standard library.
Installing the package requires access to the package index. The program runs offline.

## Full program

The shared [n_plus_one.py](../../../../../examples/python/databases/sqlalchemy/n_plus_one.py) defines the models, creates the tables, inserts the data, and checks the result.

- `DeclarativeBase` is the base class for both models. `Mapped` annotates ORM attributes, and `mapped_column` configures table columns.
- `back_populates` connects `User.posts` and `Post.author`. The `Engine` manages database connections.
- `with session.begin()` commits the sample rows on success and rolls back if an exception occurs.

The `before_cursor_execute` listener counts `SELECT` statements while the program reads users and their posts.
The program starts counting after it creates and populates the tables.
A `finally` block removes the listener even if reading fails.

## Result and limits

The program prints the following output.

```text
lazy: 3 SELECT; [('alice', ['Python', 'SQL']), ('bob', [])]
selectinload: 2 SELECT; [('alice', ['Python', 'SQL']), ('bob', [])]
```

Both strategies read every user and post, including Bob's empty collection.
The assertions check the returned rows and the query count separately.
Run `python n_plus_one.py` to keep these checks active. The `-O` flag disables assertions.

The counter recognizes statements that start with `SELECT`. SQL that starts with a comment or a CTE needs a different counter.
The counts measure `SELECT` statements for one collection, two users, and fresh sessions on the specified versions.
Measure rows, execution time, and memory separately with your own data to assess performance.

The [extended lab](loading-lab.md) covers `joinedload`, missing `unique()`, `raiseload`, and nested and partial collections.
That lab uses a separate schema and setup.
This program tests a small sequential workload on synchronous SQLite.
Async sessions, other databases, larger data sets, and concurrent access require separate checks.

## Sources

- [SQLAlchemy 2.1 relationship loading and N+1](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#lazy-loading).
- [Select-in loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#select-in-loading).
- [ORM quick start](https://docs.sqlalchemy.org/en/21/orm/quickstart.html) · [Session basics](https://docs.sqlalchemy.org/en/21/orm/session_basics.html).
- [SQL execution events](https://docs.sqlalchemy.org/en/21/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute).
- [SQLAlchemy 2.1.8 release notes](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
