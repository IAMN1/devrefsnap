from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

import async_db_app
import db_app


def test_sync_database(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'users.db'}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(db_app, "engine", engine)
    monkeypatch.setattr(db_app, "SessionLocal", sessionmaker(engine))
    with TestClient(db_app.app) as client:
        body = {"username": "alice", "email": "alice@example.com"}
        created = client.post("/users", json=body)
        assert created.status_code == 201
        assert created.json()["id"] == 1
        assert client.post("/users", json=body).status_code == 409
        assert len(client.get("/users").json()) == 1


def test_async_database(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'notes.db'}")
    monkeypatch.setattr(async_db_app, "engine", engine)
    monkeypatch.setattr(async_db_app, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    with TestClient(async_db_app.app) as client:
        created = client.post("/notes", json={"text": "Учебная заметка"})
        assert created.status_code == 201
        assert client.get("/notes").json() == [{"id": 1, "text": "Учебная заметка"}]
        assert client.post("/notes", json={"text": ""}).status_code == 422
