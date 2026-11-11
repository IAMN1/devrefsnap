import pytest
from fastapi.testclient import TestClient

from main import app, items


@pytest.fixture
def client():
    items.clear()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    items.clear()


def test_crud(client):
    created = client.post("/items", json={"name": "Book", "price": 25, "tags": ["python"]})
    assert created.status_code == 201
    item_id = created.json()["id"]
    assert client.get(f"/items/{item_id}").json()["name"] == "Book"
    listed = client.get("/items", params={"q": "Book", "tags": "python"})
    assert len(listed.json()) == 1
    changed = client.patch(f"/items/{item_id}", json={"price": 30})
    assert changed.status_code == 200
    assert changed.json()["name"] == "Book"
    assert changed.json()["price"] == 30
    replaced = client.put(f"/items/{item_id}", json={"name": "New", "price": 40})
    assert replaced.status_code == 200
    assert replaced.json()["tags"] == []
    deleted = client.delete(f"/items/{item_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/items/{item_id}").status_code == 404


def test_invalid_input(client):
    assert client.post("/items", json={"name": "Book", "price": -1}).status_code == 422
    assert client.post("/items", json={"name": "premium", "price": 1}).status_code == 422
    assert client.get("/items/not-an-integer").status_code == 422
    assert client.get("/items", params={"limit": 0}).status_code == 422


@pytest.mark.parametrize("method", ["POST", "PATCH"])
@pytest.mark.parametrize("field", ["price", "tax"])
@pytest.mark.parametrize("raw_value", ["1e999", "-1e999", '"Infinity"', '"-Infinity"', '"NaN"'])
def test_nonfinite_numbers_are_rejected_without_state_change(client, method, field, raw_value):
    original = client.post("/items", json={"name": "Book", "price": 25, "tax": 2}).json()
    if field == "price":
        raw = f'{{"name":"Book","price":{raw_value},"tax":2}}'
    else:
        raw = f'{{"name":"Book","price":25,"tax":{raw_value}}}'
    path = "/items" if method == "POST" else f'/items/{original["id"]}'
    response = client.request(method, path, content=raw, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["detail"]
    assert client.get("/items").json() == [original]


def test_patch_revalidates_whole_model(client):
    item_id = client.post("/items", json={"name": "premium", "price": 100}).json()["id"]
    assert client.patch(f"/items/{item_id}", json={"price": 1}).status_code == 422
    assert client.patch(f"/items/{item_id}", json={"name": None}).status_code == 422
    assert client.get(f"/items/{item_id}").json()["price"] == 100


def test_query_cookie_and_nested_path(client):
    client.post("/items", json={"name": "Book", "price": 25, "tags": ["python", "web"]})
    client.cookies.set("last_query", "Book")
    assert len(client.get("/items").json()) == 1
    assert client.get("/items", params={"q": "Other"}).json() == []
    repeated = client.get("/items", params=[("tags", "python"), ("tags", "web")])
    assert len(repeated.json()) == 1
    nested = client.get("/users/2/items/3", params={"short": "true"})
    assert nested.json() == {"user_id": 2, "item_id": 3, "short": True}


def test_output_does_not_expose_password(client):
    response = client.post("/user-preview", json={
        "username": "alice", "email": "alice@example.com", "password": "secret123",
    })
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "password" not in response.json()


def test_custom_responses(client):
    assert client.get("/stock/6").status_code == 409
    assert client.get("/custom").headers["X-Custom"] == "demo"
    assert "text/html" in client.get("/html").headers["content-type"]
    redirect = client.get("/redirect", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "/docs"
