# Подготовить блог SQLite и проверить запросы

Пример проверяет JOIN, параметры, ограничения, каскадное удаление и откат.
БД существует только в памяти и не открывает пользовательские файлы.
[К карточкам запросов](python-and-queries.md) · [К SQLite](README.md).

Нужен Python 3.14 со штатным sqlite3 и SQLite 3.37 или новее для STRICT.

## Полный пример: блог в памяти

Сохраните блок как `demo.py`.
Выполните `python3.14 demo.py`.
Зависимостей из pip нет.
Параметр autocommit=True выбран явно.
SQL-команды BEGIN/COMMIT/ROLLBACK ниже управляют транзакцией.

<!-- example: sqlite/demo.py -->
```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:", autocommit=True)) as db:
    db.execute("PRAGMA foreign_keys = ON")
    assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
    db.executescript("""
        BEGIN;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            age INTEGER CHECK (age >= 0),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) STRICT;
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) STRICT;
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            body TEXT NOT NULL
        ) STRICT;
        CREATE INDEX posts_user_created_idx ON posts(user_id, created_at);
        CREATE INDEX users_active_idx ON users(username) WHERE is_active = 1;
        COMMIT;
    """)
    db.executemany(
        "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
        [("alice", "alice@example.test", 30),
         ("bob", "bob@example.test", 25),
         ("carol", "carol@example.test", None)],
    )
    db.executemany("INSERT INTO posts (user_id, title) VALUES (?, ?)",
                   [(1, "SQLite"), (2, "SQL")])
    db.execute("INSERT INTO comments (post_id, user_id, body) VALUES (?, ?, ?)",
               (1, 2, "Useful"))

    rows = db.execute("""
        SELECT u.username, COUNT(p.id)
        FROM users AS u LEFT JOIN posts AS p ON p.user_id = u.id
        GROUP BY u.id, u.username ORDER BY u.username
    """).fetchall()
    assert rows == [("alice", 1), ("bob", 1), ("carol", 0)]

    for sql, params in [
        ("INSERT INTO posts (user_id, title) VALUES (?, ?)", (999, "Invalid")),
        ("INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
         ("bad", "bad@example.test", "not-an-integer")),
    ]:
        try:
            db.execute(sql, params)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Ожидался отказ ограничения")

    db.execute("BEGIN IMMEDIATE")
    try:
        user_id = db.execute(
            "INSERT INTO users (username, email) VALUES (?, ?) RETURNING id",
            ("dave", "dave@example.test"),
        ).fetchone()[0]
        assert user_id == 4
        db.execute("UPDATE users SET age = ? WHERE username = ?", (31, "alice"))
        db.execute("DELETE FROM users WHERE id = ?", (2,))
        assert db.execute("SELECT COUNT(*) FROM comments").fetchone() == (0,)
    finally:
        db.execute("ROLLBACK")
    assert db.execute("SELECT age FROM users WHERE id = 1").fetchone() == (30,)
    assert db.execute("SELECT COUNT(*) FROM users").fetchone() == (3,)
    assert db.execute("SELECT COUNT(*) FROM comments").fetchone() == (1,)
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    print("SQLite", sqlite3.sqlite_version)
    print("OK: JOIN, parameters, FK/STRICT refusal, RETURNING, cascade and rollback")
```

Пример проверяет успешный JOIN.
Пример проверяет отказ для неизвестного пользователя и неверного типа.
Пример также проверяет каскадное удаление и полный откат удаления.
Прочитайте результат RETURNING до фиксации.
`last_insert_rowid()` / cursor.lastrowid относятся к последней соответствующей вставке в соединении.
RETURNING часто яснее связывает id с конкретной командой.

## Источники

- [Python sqlite3 / transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [функции](https://www.sqlite.org/lang_corefunc.html), [даты](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [индексы](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
- [SQLite 3.53.4: release notes](https://www.sqlite.org/releaselog/3_53_4.html).
