<a id="проверить-транзакцию-и-доставку-redis"></a>
# Verify Redis transactions and delivery

[Русский](../../../../ru/databases/non-relational/redis/transactions-lab.md)

Run complete examples that exercise a WATCH conflict, a command error, and message delivery.
Use a dedicated standalone Redis 8.2 instance. Each example uses a random namespace for its keys.
[Transactions and messaging](transactions-and-messaging.md) · [Redis](README.md).

| Task | Technique | Example |
| --- | --- | --- |
| Check a conflict and behavior after a runtime error | WATCH and MULTI/EXEC | [Complete program](#complete-example-of-a-conflict-and-command-error) |
| Check pending entries, acknowledgment, and transient notification | Stream and Pub/Sub | [Complete program](#complete-stream-and-pubsub-example) |

| Item | Details |
| --- | --- |
| Level | Intermediate for transactions. Advanced for delivery. |
| Prerequisites | [redis-py 8.1.0 and REDIS_URL setup](data-lab.md#setup), plus Python 3.14 |

<a id="полный-пример-конфликт-и-ошибка-команды"></a>
## Complete example of a conflict and command error

Save the example as `transactions.py`.
Run `python transactions.py` in the prepared environment.
The script deliberately triggers a WATCH conflict and an INCR error.
It checks both results and deletes only its own keys.

[`redis/transactions.py`](../../../../../examples/databases/non-relational/redis/transactions.py)

The output is `OK: pipeline, WATCH conflict, MULTI/EXEC and no runtime rollback`.
The WATCH conflict leaves the value at `1`.
The INCR error leaves the successful SET from the same EXEC in effect.
The finally block removes the keys.

<a id="полный-пример-stream-и-pubsub"></a>
## Complete stream and Pub/Sub example

**Advanced.** Save the example as `messaging.py`.
Run `python messaging.py`.
The example creates a stream with its own consumer group.
The Pub/Sub subscription handles one delivery and exits.

[`redis/messaging.py`](../../../../../examples/databases/non-relational/redis/messaging.py)

The output is `OK: stream delivery/pending/ACK and bounded Pub/Sub notification`.
After XACK, the pending count is zero and the stream entry still exists.
The Pub/Sub example checks one notification to an already connected subscriber.
The examples cover successful handling without external side effects or handler failure.

<a id="источники"></a>
## Sources

- [Transactions, WATCH, and errors](https://redis.io/docs/latest/develop/using-commands/transactions/), [pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/).
- [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [XACK](https://redis.io/docs/latest/commands/xack/), [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/).
- [Pub/Sub and delivery guarantees](https://redis.io/docs/latest/develop/pubsub/), [redis-py pipeline](https://redis.readthedocs.io/en/v8.1.0/advanced_features.html).
- [Redis 8.2.11 release notes](https://github.com/redis/redis/releases/tag/8.2.11).
