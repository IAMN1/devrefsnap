import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory


def copy_to_new(source_path: Path, target_path: Path) -> None:
    source_uri = source_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(source_uri, uri=True, autocommit=True)) as source:
        target_path.touch(exist_ok=False)
        with closing(sqlite3.connect(target_path, autocommit=True)) as target:
            source.backup(target)


def verify_restored(db: sqlite3.Connection) -> None:
    db.execute("PRAGMA foreign_keys = ON")
    assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
    assert db.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    assert db.execute("SELECT id, username FROM users").fetchall() == [(1, "alice")]
    assert db.execute("SELECT id, user_id, title FROM posts").fetchall() == [(1, 1, "SQLite")]
    objects = dict(db.execute("SELECT name, type FROM sqlite_schema WHERE sql IS NOT NULL"))
    assert objects["users_username_idx"] == "index"
    assert objects["users_audit"] == "trigger"
    db.execute("BEGIN")
    try:
        db.execute("UPDATE users SET username = 'alice-check' WHERE id = 1")
        assert db.execute("SELECT username FROM audit").fetchall() == [("alice-check",)]
    finally:
        db.execute("ROLLBACK")
    assert db.execute("SELECT username FROM users").fetchall() == [("alice",)]
    assert db.execute("SELECT username FROM audit").fetchall() == []
    for sql in (
        "INSERT INTO posts VALUES (2, 999, 'invalid reference')",
        "UPDATE users SET username = '' WHERE id = 1",
    ):
        try:
            db.execute(sql)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Restored constraint must reject invalid data")
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []


with TemporaryDirectory(prefix="sqlite-backup-") as directory:
    folder = Path(directory)
    source_path = folder / "source.db"
    backup_path = folder / "backup.db"
    restored_path = folder / "restored.db"
    with closing(sqlite3.connect(source_path, autocommit=True)) as source:
        assert source.execute("PRAGMA journal_mode = WAL").fetchone() == ("wal",)
        source.execute("PRAGMA wal_autocheckpoint = 0")
        source.execute("PRAGMA foreign_keys = ON")
        source.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL CHECK (username <> '')
            ) STRICT;
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL
            ) STRICT;
            CREATE TABLE audit (username TEXT NOT NULL) STRICT;
            CREATE INDEX users_username_idx ON users(username);
            CREATE TRIGGER users_audit AFTER UPDATE ON users
            BEGIN INSERT INTO audit VALUES (NEW.username); END;
            INSERT INTO users VALUES (1, 'alice');
            INSERT INTO posts VALUES (1, 1, 'SQLite');
        """)
        assert Path(str(source_path) + "-wal").stat().st_size > 0
        copy_to_new(source_path, backup_path)
        source.execute("UPDATE users SET username = 'alice-live' WHERE id = 1")
        copy_to_new(backup_path, restored_path)
        with closing(sqlite3.connect(restored_path, autocommit=True)) as restored:
            verify_restored(restored)
        assert source.execute("SELECT username FROM users").fetchall() == [("alice-live",)]
        assert source.execute("SELECT username FROM audit").fetchall() == [("alice-live",)]

    saved = backup_path.read_bytes()
    try:
        copy_to_new(source_path, backup_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Existing backup must not be replaced")
    assert backup_path.read_bytes() == saved

    missing = folder / "missing.db"
    missing_target = folder / "missing-target.db"
    try:
        copy_to_new(missing, missing_target)
    except sqlite3.OperationalError:
        pass
    else:
        raise AssertionError("Missing source must not become an empty backup")
    assert not missing.exists()
    assert not missing_target.exists()

    invalid = folder / "invalid.db"
    invalid.write_bytes(b"not a SQLite database")
    try:
        copy_to_new(invalid, folder / "invalid-target.db")
    except sqlite3.DatabaseError:
        pass
    else:
        raise AssertionError("Invalid source must not be accepted")
    print("Python backup/restore OK; SQLite", sqlite3.sqlite_version)
