import io
import json

from fastapi.testclient import TestClient

from demo_logging import configure_logging
from demo_web import app


def test_request_context_and_failure():
    stream = io.StringIO()
    configure_logging(stream)
    with TestClient(app, raise_server_exceptions=False) as client:
        first = client.get("/")
        assert first.status_code == 200
        assert client.get("/fail").status_code == 500
        second = client.get("/")
        assert second.status_code == 200
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    ids = [item["request_id"] for item in events if item["event"] == "request_started"]
    assert len(ids) == len(set(ids)) == 3
    assert first.headers["X-Request-ID"] == ids[0]
    assert second.headers["X-Request-ID"] == ids[2]
    failed = [item for item in events if item["event"] == "request_failed"]
    assert len(failed) == 1
    assert failed[0]["request_id"] == ids[1]
    assert "RuntimeError" in failed[0]["exception"]
