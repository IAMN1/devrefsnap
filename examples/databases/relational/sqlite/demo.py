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
