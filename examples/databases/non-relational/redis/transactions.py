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
