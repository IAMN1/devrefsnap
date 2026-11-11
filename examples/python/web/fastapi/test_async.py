import pytest
from httpx2 import ASGITransport, AsyncClient

from main import app, items


@pytest.mark.asyncio
async def test_async_request():
    items.clear()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/items", json={"name": "Async book", "price": 20})
            assert response.status_code == 201
            item_id = response.json()["id"]
            assert (await client.get(f"/items/{item_id}")).json()["name"] == "Async book"
    finally:
        items.clear()
