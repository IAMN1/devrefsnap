import json
import sqlite3
from collections.abc import Callable
from contextlib import closing

Publisher = Callable[[str, str], None]


class SimulatedCrash(Exception):
    pass


with closing(sqlite3.connect(":memory:", autocommit=True)) as db:
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE orders (id TEXT PRIMARY KEY NOT NULL);
        CREATE TABLE outbox (
            event_id TEXT PRIMARY KEY NOT NULL,
            order_id TEXT NOT NULL REFERENCES orders(id),
            payload TEXT NOT NULL,
            sent INTEGER NOT NULL DEFAULT 0 CHECK (sent IN (0, 1))
        );
    """)

    def create_order(order_id: str, event_id: str) -> None:
        db.execute("BEGIN")
        try:
            db.execute("INSERT INTO orders VALUES (?)", (order_id,))
            db.execute("INSERT INTO outbox (event_id, order_id, payload) VALUES (?, ?, ?)",
                       (event_id, order_id, json.dumps({"type": "OrderCreated", "order_id": order_id})))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise

    create_order("42", "event-42")
    try:
        create_order("43", "event-42")  # Ошибка второй записи: event_id уже занят.
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("Ожидался отказ UNIQUE")
    assert db.execute("SELECT id FROM orders").fetchall() == [("42",)]
    assert db.execute("SELECT COUNT(*) FROM outbox").fetchone() == (1,)

    published: list[str] = []

    def publish(event_id: str, payload: str) -> None:
        assert json.loads(payload)["order_id"] == "42"
        published.append(event_id)

    def publish_then_crash(event_id: str, payload: str) -> None:
        publish(event_id, payload)
        raise SimulatedCrash("Брокер принял, отметка sent ещё не записана")

    def relay_once(publisher: Publisher) -> bool:
        row = db.execute("SELECT event_id, payload FROM outbox WHERE sent = 0 ORDER BY event_id LIMIT 1").fetchone()
        if row is None:
            return False
        event_id, payload = row
        publisher(event_id, payload)
        db.execute("UPDATE outbox SET sent = 1 WHERE event_id = ?", (event_id,))
        return True

    try:
        relay_once(publish_then_crash)
    except SimulatedCrash:
        pass
    else:
        raise AssertionError("Ожидался сбой между публикацией и отметкой")
    assert db.execute("SELECT sent FROM outbox").fetchone() == (0,)
    assert relay_once(publish)
    assert not relay_once(publish)
    assert published == ["event-42", "event-42"]
    print("OK: atomic order/outbox, rollback on refusal and duplicate after relay failure")
