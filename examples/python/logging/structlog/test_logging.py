import io
import json
import logging
import sys

import pytest

from demo_logging import configure_logging


def test_json_bind_redaction_and_exception():
    stream = io.StringIO()
    parent = configure_logging(stream)
    child = parent.bind(user_id=1)
    child.info("login", payload=[{"password": "secret"}], token="secret-token")
    parent.info("parent")
    child.unbind("user_id").info("unbound")
    try:
        1 / 0
    except ZeroDivisionError:
        child.exception("failed")
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert events[0]["user_id"] == 1
    assert events[0]["payload"] == [{"password": "***"}]
    assert events[0]["token"] == "***"
    assert "user_id" not in events[1]
    assert "user_id" not in events[2]
    assert "ZeroDivisionError" in events[3]["exception"]
    with pytest.raises(KeyError):
        child.unbind("missing")


def test_level_guard_and_output_modes():
    stream = io.StringIO()
    log = configure_logging(stream, level=logging.INFO)
    evaluated = []
    if log.is_enabled_for(logging.DEBUG):
        evaluated.append("expensive")
        log.debug("debug", value=evaluated)
    assert evaluated == []
    assert stream.getvalue() == ""
    for output in ("console", "keyvalue"):
        stream = io.StringIO()
        configure_logging(stream, output=output).info("visible", answer=42)
        assert "visible" in stream.getvalue()
        assert "42" in stream.getvalue()
    with pytest.raises(ValueError):
        configure_logging(stream, output="unknown")


@pytest.mark.parametrize("output", ["json", "console"])
def test_saved_exception_tuple_outside_except(output):
    stream = io.StringIO()
    log = configure_logging(stream, output=output)
    try:
        1 / 0
    except ZeroDivisionError:
        saved = sys.exc_info()
    log.error("saved_failure", exc_info=saved)
    assert "ZeroDivisionError" in stream.getvalue()
    if output == "json":
        assert "Traceback" in json.loads(stream.getvalue())["exception"]
    else:
        assert "Traceback" in stream.getvalue()
