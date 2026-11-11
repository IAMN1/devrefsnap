import sqlite3
import warnings

import pytest

from demo_service import subtotal


@pytest.fixture
def connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (name TEXT NOT NULL)")
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(params=["utf-8", "utf-16"])
def encoding(request):
    return request.param


@pytest.mark.parametrize("quantity, price, expected", [
    (0, 2.5, 0.0),
    (1, 2.5, 2.5),
    (3, 2.5, 7.5),
])
def test_subtotal(quantity, price, expected):
    assert subtotal(quantity, price) == pytest.approx(expected)


@pytest.mark.parametrize("quantity", [-1, 1.5, True])
def test_invalid_quantity(quantity):
    with pytest.raises(ValueError, match="quantity") as error:
        subtotal(quantity, 2.5)
    assert "non-negative integer" in str(error.value)


def test_database_write(connection):
    connection.execute("INSERT INTO items VALUES (?)", ("apple",))
    assert connection.execute("SELECT name FROM items").fetchall() == [("apple",)]


def test_database_starts_empty(connection):
    assert connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_file_roundtrip(tmp_path, encoding):
    path = tmp_path / "note.txt"
    path.write_text("Привет", encoding=encoding)
    assert path.read_text(encoding=encoding) == "Привет"


def test_print_output(capsys):
    print("ready")
    assert capsys.readouterr().out == "ready\n"


def test_float_sum():
    assert 0.1 + 0.2 == pytest.approx(0.3, rel=1e-9)


def test_warning():
    with pytest.warns(UserWarning, match="old format"):
        warnings.warn("old format", UserWarning)
