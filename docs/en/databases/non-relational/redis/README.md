
# Redis

[Русский](../../../../ru/databases/non-relational/redis/README.md)

Redis is an in-memory data structure server.
Use it for caching, counters, sets, rankings, and messaging.
Use a relational database when you need relational constraints.
Durability depends on configuration and verified restores.

[Databases](../../README.md)

<a id="навигация"></a>

<a id="быстрый-поиск"></a>
## Quick reference

| Task | Commands or concepts | Where to look |
| --- | --- | --- |
| Store a value with an expiration | SET EX/PX, TTL/PTTL, EXPIRE | [Data and caching](data-and-caching.md) |
| Store counters, profiles, queues, tags, or rankings | INCR, HSET, list, set, sorted set | [Choose a data structure](data-and-caching.md#choose-a-data-structure-for-the-operation) · [Complete example](data-lab.md#complete-data-structures-and-ttl-example) |
| Reduce network round trips | Pipeline | [Compare with transactions](transactions-and-messaging.md#atomicity-transactions-and-pipelining) |
| Run commands as a group without interleaving | MULTI/EXEC, WATCH | [Quick example](transactions-and-messaging.md#полный-пример-конфликт-и-ошибка-команды) · [Complete example](transactions-lab.md#complete-example-of-a-conflict-and-command-error) |
| Deliver a task and track acknowledgment | Stream, XREADGROUP/XACK | [Messaging](transactions-and-messaging.md#полный-пример-stream-и-pubsub) |
| Send a transient notification to a subscriber | Pub/Sub | [Compare with streams](transactions-and-messaging.md#полный-пример-stream-и-pubsub) |
| Back up RDB and verify the restore | BGSAVE, PTTL, PEXPIRETIME | [Quick reference](operations.md#create-and-restore-an-rdb-backup) · [Script and setup](backup-and-restore.md#setup) |
| Back up AOF and verify the restore | Manifest, BASE, INCR, TTL | [Quick reference](operations.md#create-and-restore-an-aof-backup) · [Script and setup](aof-backup-and-restore.md#setup) |
| Manage durability, memory, and security | RDB/AOF, eviction, ACL/TLS | [Operations](operations.md) |

| Item | Details |
| --- | --- |
| Target release series | Redis Open Source 8.2 |
| Example clients | Python 3.14 and redis-py 8.1.0. The RDB and AOF examples use redis-cli 8.2.11 and need no redis-py. |

<a id="базовый-уровень"></a>

<a id="выбрать-структуру"></a>
## Choose a data structure

Choose the structure based on the operation.
Use a string for a value or counter.
Use a hash for object fields.
Use a list for order, a set for uniqueness, or a sorted set for score order.
The [first example](data-lab.md#complete-data-structures-and-ttl-example) creates only unique practice keys and deletes them in finally.
Set REDIS_URL explicitly. The example has no default local connection.

<a id="средний-уровень"></a>

<a id="согласовать-кеш-и-изменения"></a>
## Coordinate cache reads and updates

For a [cache](data-and-caching.md#cache-aside), define an invalidation policy, a memory limit, and acceptable staleness.
The application or eviction can delete a key before its TTL expires.
A single INCR is atomic.
GET → calculate → SET spans multiple operations.
Use [WATCH, a script, or another coordination protocol](transactions-and-messaging.md) for a read-modify-write operation.

<a id="продвинутый-уровень"></a>

<a id="выбрать-гарантии-доставки-и-сохранности"></a>
## Choose delivery and durability guarantees

[Streams and Pub/Sub](transactions-and-messaging.md) offer different delivery guarantees.
[RDB/AOF, replication, and Cluster](operations.md) serve different purposes.
Keep backups even if you have a replica.
Transaction durability depends on persistence settings.
Cluster can lose an acknowledged write after a failure.
The examples use standalone Redis.
Test Cluster and failover separately.

<a id="частые-ошибки"></a>
## Common mistakes

| Problem | What to do |
| --- | --- |
| SET removes the TTL | Replacing a value usually removes its TTL. Specify EX/PX or KEEPTTL as needed. |
| TTL returns -1 or -2 | -1 means the key has no expiration. -2 means the key is absent. |
| Treating a pipeline as a transaction | Pipelining reduces network round trips. Use a transaction to prevent interleaving. |
| Expecting EXEC to roll everything back after an error | Successful commands remain applied when another command fails at runtime |
| Using Pub/Sub as a reliable queue | Disconnected subscribers have no history. Consider a stream and pending-entry handling. |
| Using KEYS or FLUSHALL in a shared environment | Use bounded SCAN and delete only your own keys. These examples require no FLUSHALL. |
| Exposing Redis to the internet without ACLs or TLS | First restrict network access, allowed commands and keys, and secure the connection |

<a id="источники"></a>
## Sources

- [Supported Redis release series](https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/), [data structures](https://redis.io/docs/latest/develop/data-types/).
- [Commands](https://redis.io/docs/latest/commands/), [redis-py](https://redis.readthedocs.io/en/stable/).
- The detailed pages link to additional official documentation.
