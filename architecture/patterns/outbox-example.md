# Проверить атомарность Outbox и повтор публикации

Используйте пример, если заказ и намерение отправить событие должны сохраняться вместе.
Отдельный отправитель может завершиться после публикации и до отметки об отправке.

| Что проверить | Приём | Результат |
| --- | --- | --- |
| Ошибка второй записи не оставляет заказ | Запишите заказ и событие в одной транзакции | Заказ `43` отсутствует после отказа `UNIQUE` |
| Повтор отправителя допускает дубликат | Смоделируйте сбой до отметки `sent` | Событие `event-42` опубликовано дважды |

[Карточка и схема Outbox](distributed-systems.md#transactional-outbox-сохранить-заказ-и-намерение-публикации) · [К паттернам](README.md)

**Предпосылки:** Python 3.14, транзакции SQLite, исключения.
Внешние зависимости и сетевые службы не нужны.

## Полный пример: Outbox и дубликат публикации

**Продвинутый уровень.** Сохраните код как `outbox.py`.
Выполните `python3.14 outbox.py`.
Пример использует sqlite3 из стандартной библиотеки.
Пример использует только БД в памяти.
Список заменяет брокер.
Проверяются атомарность локальной записи и возможный повтор внешней публикации.

<!-- example: architecture/outbox.py -->
```python
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
```

**Результат:** OK.
После ошибки записи события заказ 43 не сохранился.
После смоделированного сбоя событие заказа 42 опубликовано дважды.
Это ожидаемая граница Outbox.
Пример не даёт exactly-once гарантию.

См. [схему вызовов Outbox](distributed-systems.md#transactional-outbox-сохранить-заказ-и-намерение-публикации).

Для production relay нужны блокировка или lease для workers.
Нужно подтверждение брокера.
Нужна обработка неизвестного исхода.
Нужно управление порядком, повторами и мёртвыми сообщениями.
Нужна уборка outbox.
Исключение в примере моделирует точку отказа.
БД в памяти не моделирует сохранность на диске или восстановление после завершения процесса.
Consumer здесь не реализован.

## Источники

- [Python 3.14: sqlite3](https://docs.python.org/3.14/library/sqlite3.html).
- [Microsoft: Transactional Outbox](https://learn.microsoft.com/en-us/azure/architecture/databases/guide/transactional-out-box-cosmos).
