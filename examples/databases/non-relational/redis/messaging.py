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
