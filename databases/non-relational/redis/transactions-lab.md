# Проверить транзакцию и доставку Redis

Откройте страницу для полного запуска конфликта WATCH, ошибки команды и доставки сообщений.
Используйте отдельный standalone Redis 8.2; все ключи получают случайный namespace.
[К карточкам транзакций и сообщений](transactions-and-messaging.md) · [К Redis](README.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Проверить конфликт и отсутствие runtime rollback | WATCH и MULTI/EXEC | [Полная программа](#полный-пример-конфликт-и-ошибка-команды) |
| Проверить pending, ACK и временное уведомление | Stream и Pub/Sub | [Полная программа](#полный-пример-stream-и-pubsub) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний — транзакции; продвинутый — доставка |
| Предпосылки | [Подготовленные redis-py 8.1.0 и REDIS_URL](data-lab.md#подготовка); Python 3.14 |

## Полный пример: конфликт и ошибка команды

Сохраните пример как `transactions.py`.
Выполните `python transactions.py` в подготовленном окружении.
Скрипт намеренно вызывает конфликт WATCH и ошибку INCR.
Скрипт проверяет оба результата и удаляет только свои ключи.

<!-- example: redis/transactions.py -->
```python
import os
import uuid
from redis import Redis
from redis.exceptions import ResponseError, WatchError

client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True, socket_timeout=3)
prefix = f"cheatsheet:{{{uuid.uuid4().hex}}}:"
counter, bad, after = [prefix + name for name in ("counter", "bad", "after")]
try:
    with client.pipeline(transaction=False) as pipe:
        pipe.incr(counter)
        pipe.incr(counter)
        pipe.get(counter)
        assert pipe.execute() == [1, 2, "2"]

    client.set(counter, 0)
    with client.pipeline() as pipe:
        pipe.watch(counter)
        observed = int(pipe.get(counter))
        client.incr(counter)  # Другой запрос через другое соединение пула.
        pipe.multi()
        pipe.set(counter, observed + 10)
        try:
            pipe.execute()
        except WatchError:
            pass
        else:
            raise AssertionError("WATCH должен отклонить изменение")
    assert client.get(counter) == "1"

    with client.pipeline(transaction=True) as pipe:
        pipe.incr(counter)
        pipe.expire(counter, 60)
        assert pipe.execute() == [2, True]

    client.set(bad, "not-an-integer")
    with client.pipeline(transaction=True) as pipe:
        pipe.incr(bad)
        pipe.set(after, "applied")
        results = pipe.execute(raise_on_error=False)
    assert isinstance(results[0], ResponseError)
    assert results[1] is True
    assert client.get(after) == "applied"
    print("OK: pipeline, WATCH conflict, MULTI/EXEC and no runtime rollback")
finally:
    client.unlink(counter, bad, after)
    client.close()
```

**Результат:** `OK: pipeline, WATCH conflict, MULTI/EXEC and no runtime rollback`.
Конфликт WATCH оставляет значение `1`.
Ошибка INCR не отменяет успешный SET того же EXEC.
Ключи удаляются в finally.

## Полный пример: stream и Pub/Sub

**Продвинутый уровень.** Сохраните пример как `messaging.py`.
Выполните `python messaging.py`.
Пример создаёт stream с собственной группой.
Pub/Sub-подписка ограничена одной доставкой без бесконечного цикла.

<!-- example: redis/messaging.py -->
```python
import os
import uuid
from redis import Redis

client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True, socket_timeout=3)
prefix = f"cheatsheet:{{{uuid.uuid4().hex}}}:"
stream, channel = prefix + "stream", prefix + "channel"
try:
    client.xgroup_create(stream, "workers", id="0", mkstream=True)
    message_id = client.xadd(stream, {"order_id": "42"})
    deliveries = client.xreadgroup("workers", "worker-1", {stream: ">"}, count=1, block=500)
    assert deliveries == [[stream, [(message_id, {"order_id": "42"})]]]
    assert client.xpending(stream, "workers")["pending"] == 1
    # Здесь должна завершиться прикладная обработка; только затем ACK.
    assert client.xack(stream, "workers", message_id) == 1
    assert client.xpending(stream, "workers")["pending"] == 0

    with client.pubsub() as subscriber:
        subscriber.subscribe(channel)
        confirmation = subscriber.get_message(timeout=1)
        assert confirmation is not None and confirmation["type"] == "subscribe"
        assert client.publish(channel, "updated") == 1
        notification = subscriber.get_message(timeout=1)
        assert notification is not None
        assert notification["type"] == "message" and notification["data"] == "updated"
    print("OK: stream delivery/pending/ACK and bounded Pub/Sub notification")
finally:
    client.unlink(stream)
    client.close()
```

**Результат:** `OK: stream delivery/pending/ACK and bounded Pub/Sub notification`.
После XACK pending равен нулю; это не удаляет запись stream.
Pub/Sub проверяет одно уведомление уже подключённого подписчика.
Программы не моделируют сбой обработчика или внешний побочный эффект.

## Источники

- [Транзакции / WATCH / ошибки](https://redis.io/docs/latest/develop/using-commands/transactions/), [pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/).
- [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XACK](https://redis.io/docs/latest/commands/xack/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/).
- [Pub/Sub и гарантии](https://redis.io/docs/latest/develop/pubsub/), [redis-py pipeline](https://redis.readthedocs.io/en/v8.1.0/advanced_features.html).
- [Redis 8.2.11: release notes](https://github.com/redis/redis/releases/tag/8.2.11).
