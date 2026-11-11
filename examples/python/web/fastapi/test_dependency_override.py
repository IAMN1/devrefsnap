from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


def verify_client(x_client: Annotated[str, Header()]):
    if x_client != "training-client":
        raise HTTPException(400, "Неизвестный клиент")


@app.get("/checked", dependencies=[Depends(verify_client)])
def checked():
    return {"checked": True}


def test_real_header_check():
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        assert client.get("/checked", headers={"X-Client": "wrong"}).status_code == 400
        assert client.get("/checked", headers={"X-Client": "training-client"}).status_code == 200


def test_override():
    calls = []

    def skip_client_check():
        calls.append("override")
        return None

    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = skip_client_check
        with TestClient(app) as client:
            response = client.get("/checked")
            assert response.status_code == 200
            assert response.json() == {"checked": True}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
    assert calls == ["override"]
    assert app.dependency_overrides == previous
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        assert client.get("/checked", headers={"X-Client": "wrong"}).status_code == 400
        assert client.get("/checked", headers={"X-Client": "training-client"}).status_code == 200
