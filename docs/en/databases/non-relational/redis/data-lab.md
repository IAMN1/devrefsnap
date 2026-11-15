<a id="проверить-структуры-и-ttl-redis"></a>
# Verify Redis data structures and TTL

[Русский](../../../../ru/databases/non-relational/redis/data-lab.md)

Run operations on a string, profile, queue, set of tags, and ranking.
Use a dedicated Redis 8.2 instance with synthetic data.
[Data and caching](data-and-caching.md) · [Redis](README.md).

Use Redis 8.2, Python 3.14, and redis-py 8.1.0.

<a id="подготовка"></a>
## Setup

Install the client in a separate temporary or practice environment with `python -m pip install 'redis==8.1.0'`.
First set up an [isolated Redis instance](operations.md#practice-instance).
Check its address.
Set REDIS_URL.
For a private Unix socket, use `export REDIS_URL='unix:///path/to/redis.sock?db=0'` with your own socket path.
For a dedicated TCP instance, replace `PORT` in `redis://127.0.0.1:PORT/0` with the actual port.
Use the practice instance for the examples.

<a id="полный-пример-структуры-и-ttl"></a>
## Complete data structures and TTL example

Save the example as `data.py`.
Run `python data.py`.
All keys use a unique namespace.
The finally block deletes only the keys the program created, whether it succeeds or fails.

[`redis/data.py`](../../../../../examples/databases/non-relational/redis/data.py)

The example prints an OK line and exits without exceptions.
The checks verify operation results. Timing and performance require separate measurements.
The list example uses LPOP to demonstrate order.
LPOP removes the item immediately, with no acknowledgment or redelivery.
For reliable task delivery, use a protocol such as a [stream](transactions-and-messaging.md#полный-пример-stream-и-pubsub).

<a id="источники"></a>
## Sources

- [Data structures](https://redis.io/docs/latest/develop/data-types/), [SET](https://redis.io/docs/latest/commands/set/), [EXPIRE](https://redis.io/docs/latest/commands/expire/), [TTL](https://redis.io/docs/latest/commands/ttl/).
- [SCAN](https://redis.io/docs/latest/commands/scan/), [eviction](https://redis.io/docs/latest/develop/reference/eviction/), [cache-aside](https://redis.io/tutorials/howtos/solutions/microservices/caching/).
- [Redis 8.2.11 release notes](https://github.com/redis/redis/releases/tag/8.2.11).
