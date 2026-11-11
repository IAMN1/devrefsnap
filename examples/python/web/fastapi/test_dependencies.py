from contextlib import contextmanager

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from header_dependency import app, verify_client


@pytest.fixture(autouse=True)
def isolated_overrides():
    previous = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@contextmanager
def overridden_client(replacement):
    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = replacement
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def test_real_header_check():
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        denied = client.get("/checked", headers={"X-Client": "wrong"})
        assert denied.status_code == 400
        assert denied.json() == {"detail": "Неизвестный клиент"}
        allowed = client.get("/checked", headers={"X-Client": "training-client"})
        assert allowed.status_code == 200
        assert allowed.json() == {"checked": True}


def test_override_is_called():
    calls = []

    def skip_client_check():
        calls.append("override")
        return None

    with overridden_client(skip_client_check) as client:
        response = client.get("/checked")
        assert response.status_code == 200
        assert response.json() == {"checked": True}
    assert calls == ["override"]
    assert app.dependency_overrides == {}
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422


@pytest.mark.parametrize("has_previous", [False, True])
@pytest.mark.parametrize("failure", [None, "assertion", "dependency"])
def test_restores_previous_overrides(has_previous, failure):
    def other_dependency():
        return "unused"

    def previous_check():
        raise HTTPException(403, "Прежняя подмена")

    def previous_other():
        return "previous"

    def replacement():
        if failure == "dependency":
            raise RuntimeError("Ошибка зависимости")
        return None

    if has_previous:
        app.dependency_overrides.update({
            verify_client: previous_check,
            other_dependency: previous_other,
        })
    previous = app.dependency_overrides.copy()

    def exercise():
        with overridden_client(replacement) as client:
            assert app.dependency_overrides[verify_client] is replacement
            assert client.get("/checked").status_code == 200
            if failure == "assertion":
                raise AssertionError("Ошибка внутри проверяемого блока")

    if failure == "assertion":
        with pytest.raises(AssertionError, match="Ошибка внутри проверяемого блока"):
            exercise()
    elif failure == "dependency":
        with pytest.raises(RuntimeError, match="Ошибка зависимости"):
            exercise()
    else:
        exercise()
    assert app.dependency_overrides == previous
    with TestClient(app) as client:
        response = client.get("/checked")
        assert response.status_code == (403 if has_previous else 422)
        if has_previous:
            assert response.json() == {"detail": "Прежняя подмена"}
