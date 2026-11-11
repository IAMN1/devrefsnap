import sqlite3

import pytest

from flask_app import create_app
from flask_db import get_db, init_app


def test_connection_lifecycle_and_rollback(tmp_path):
    path = tmp_path / "demo.sqlite"
    app = create_app({"TESTING": True, "DATABASE": str(path)})
    init_app(app)
    with app.app_context():
        connection = get_db()
        assert get_db() is connection
        connection.execute("CREATE TABLE items (name TEXT NOT NULL)")
        connection.execute("INSERT INTO items VALUES (?)", ("saved",))
        connection.commit()
        connection.execute("INSERT INTO items VALUES (?)", ("rolled back",))
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")
    with app.app_context():
        next_connection = get_db()
        assert next_connection is not connection
        assert next_connection.execute("SELECT name FROM items").fetchall() == [("saved",)]
