from fastapi.testclient import TestClient

from middleware_app import app as middleware_app
from uploads import MAX_BYTES, app as uploads_app


def test_form_and_files():
    with TestClient(uploads_app) as client:
        assert client.post("/form", data={"username": "alice"}).json() == {"username": "alice"}
        response = client.post("/upload", files={"file": ("demo.txt", b"abc", "text/plain")})
        assert response.status_code == 200
        assert response.json() == {"filename": "demo.txt", "size": 3}
        multiple = client.post("/uploads", files=[
            ("files", ("a.txt", b"a", "text/plain")),
            ("files", ("b.txt", b"bb", "text/plain")),
        ])
        assert [item["size"] for item in multiple.json()] == [1, 2]
        assert client.post("/upload").status_code == 422
        too_big = client.post("/upload", files={"file": ("large.txt", b"x" * (MAX_BYTES + 1))})
        assert too_big.status_code == 413


def test_cors_and_timing():
    with TestClient(middleware_app) as client:
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert float(response.headers["X-Process-Time"]) >= 0
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        preflight = client.options("/", headers={
            "Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET",
        })
        assert preflight.status_code == 200
        denied = client.get("/", headers={"Origin": "http://untrusted.example"})
        assert "Access-Control-Allow-Origin" not in denied.headers
