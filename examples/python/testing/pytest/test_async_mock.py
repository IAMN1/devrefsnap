import asyncio

import pytest
import pytest_asyncio

import demo_service


def test_status_label(mocker):
    adapter = mocker.patch(
        "demo_service.read_remote", autospec=True, return_value={"status": "ready"}
    )
    assert demo_service.status_label(7) == "order 7: ready"
    adapter.assert_called_once_with(7)


def test_remote_error_is_not_hidden(mocker):
    mocker.patch("demo_service.read_remote", side_effect=TimeoutError("slow"))
    with pytest.raises(TimeoutError, match="slow"):
        demo_service.status_label(7)


def test_environment_isolated(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "test")
    import os
    assert os.environ["DEMO_MODE"] == "test"


@pytest_asyncio.fixture
async def inbox():
    queue = asyncio.Queue()
    await queue.put("hello")
    yield queue
    assert queue.empty()


@pytest.mark.asyncio
async def test_async_result(inbox):
    value = await inbox.get()
    assert await demo_service.uppercase(value) == "HELLO"
