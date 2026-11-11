from fastapi.testclient import TestClient

from demo_query import app


def test_query_model():
    with TestClient(app) as client:
        assert client.get("/items", params={"q": "python"}).json() == {"q": "python", "limit": 10, "offset": 0}
        assert client.get("/items", params={"q": "python", "limit": 0}).status_code == 422
        assert client.get("/items").status_code == 422
