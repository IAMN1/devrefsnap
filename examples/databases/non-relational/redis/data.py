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
