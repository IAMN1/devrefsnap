import io
import json

import pytest

from demo_context import run_tasks
from demo_logging import configure_logging


@pytest.mark.asyncio
async def test_task_context_isolation_and_cleanup():
    stream = io.StringIO()
    configure_logging(stream)
    await run_tasks()
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    for item_id in (1, 2):
        selected = [item for item in events if item.get("item_id") == item_id]
        assert [item["event"] for item in selected] == ["item_started", "item_completed"]
        assert all(item["request_id"] == "training-request" for item in selected)
    assert events[-1]["event"] == "outside"
    assert "item_id" not in events[-1]
    assert "request_id" not in events[-1]
