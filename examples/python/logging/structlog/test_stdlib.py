import io
import json
import logging

from demo_stdlib import configure_stdlib


def test_foreign_and_structlog_share_json_format():
    stream = io.StringIO()
    structured, plain = configure_stdlib(stream)
    try:
        structured.info("structured_event", count=2)
        plain.info("plain %s", "event")
        events = [json.loads(line) for line in stream.getvalue().splitlines()]
        assert [item["event"] for item in events] == ["structured_event", "plain event"]
        assert events[0]["count"] == 2
        assert events[1]["logger"] == "training.plain"
        assert all("_record" not in item and "_from_structlog" not in item for item in events)
    finally:
        logging.getLogger("training").handlers.clear()
