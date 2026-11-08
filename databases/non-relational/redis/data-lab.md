# Проверить структуры и TTL Redis

Откройте страницу для полного запуска операций со строкой, профилем, очередью, тегами и рейтингом.
Используйте отдельный Redis 8.2 с синтетическими данными.
[К карточкам данных и кеша](data-and-caching.md) · [К Redis](README.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Подготовить клиент и адрес | redis-py и обязательный REDIS_URL | [Подготовка](#подготовка) |
| Проверить структуры и истечение | Случайный namespace и assert | [Полная программа](#полный-пример-структуры-и-ttl) |

| Параметр | Значение |
| --- | --- |
| Уровень | Базовый; выбор кеширования описан в карточках среднего уровня |
| Зависимости | Redis 8.2, Python 3.14, redis-py 8.1.0 |

## Подготовка

Установите клиент в отдельное временное/учебное окружение: `python -m pip install 'redis==8.1.0'`.
Сначала подготовьте [изолированный Redis](operations.md#учебный-экземпляр).
Проверьте адрес Redis.
Задайте REDIS_URL.
Для собственного Unix socket используйте форму `export REDIS_URL='unix:///путь/redis.sock?db=0'`.
Для выделенного TCP-экземпляра используйте форму `redis://127.0.0.1:порт/0`.
Не направляйте примеры в рабочую БД.

## Полный пример: структуры и TTL

Сохраните пример как `data.py`.
Выполните `python data.py`.
Все ключи получают уникальный namespace.
finally удаляет только явно созданные ключи.
Пример очищает временные данные и при успешном запуске.

<!-- example: redis/data.py -->
```python
import os
import time
import uuid
from redis import Redis

client = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True, socket_timeout=3)
prefix = f"cheatsheet:{{{uuid.uuid4().hex}}}:"
cache, counter, profile, tags, queue, ranking = [
    prefix + name for name in ("cache", "counter", "profile", "tags", "queue", "ranking")
]
keys = [cache, counter, profile, tags, queue, ranking]
try:
    assert client.ping()
    assert client.set(cache, '{"name":"Ada"}', ex=60, nx=True)
    assert 0 < client.ttl(cache) <= 60
    client.set(cache, '{"name":"Ada Lovelace"}', keepttl=True)
    assert 0 < client.ttl(cache) <= 60
    assert client.pexpire(cache, 0)
    assert client.ttl(cache) == -2
    client.set(cache, "temporary", px=40)
    time.sleep(0.08)
    assert client.get(cache) is None

    assert client.incrby(counter, 2) == 2
    client.hset(profile, mapping={"name": "Ada", "language": "Python"})
    assert client.hgetall(profile) == {"name": "Ada", "language": "Python"}
    client.sadd(tags, "sql", "python", "sql")
    assert client.smembers(tags) == {"sql", "python"}
    client.rpush(queue, "first", "second")
    assert client.lpop(queue) == "first"
    assert client.lrange(queue, 0, -1) == ["second"]
    client.zadd(ranking, {"Ada": 10, "Bob": 20})
    assert client.zrevrange(ranking, 0, 0, withscores=True) == [("Bob", 20.0)]
    print("OK: structures, atomic counter, TTL preservation and expiry")
finally:
    client.unlink(*keys)
    client.close()
```

**Результат:** пример выводит строку OK без исключений.
Пример удаляет только собственные ключи.
Проверки оценивают корректность.
Проверки не измеряют скорость или точность таймера.
List с LPOP выше показывает порядок.
Этот list не реализует надёжную очередь задач.
После извлечения нет ACK или повторной доставки.
Для такого протокола нужен другой дизайн, например [stream](transactions-and-messaging.md#полный-пример-stream-и-pubsub).

## Источники

- [Структуры](https://redis.io/docs/latest/develop/data-types/), [SET](https://redis.io/docs/latest/commands/set/), [EXPIRE](https://redis.io/docs/latest/commands/expire/), [TTL](https://redis.io/docs/latest/commands/ttl/).
- [SCAN](https://redis.io/docs/latest/commands/scan/), [eviction](https://redis.io/docs/latest/develop/reference/eviction/), [cache-aside](https://redis.io/tutorials/howtos/solutions/microservices/caching/).
- [Redis 8.2.11: release notes](https://github.com/redis/redis/releases/tag/8.2.11).
