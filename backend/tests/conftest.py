import asyncio
import sys
from pathlib import Path

import httpx
import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import database
from main import app


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()

    async def send(method, url, **kwargs):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, url, **kwargs)

    def request(method, url, **kwargs):
        return asyncio.run(send(method, url, **kwargs))

    return request


@pytest.fixture
def database_path(tmp_path, monkeypatch):
    path = tmp_path / "db_ops.sqlite"
    monkeypatch.setattr(database, "DB_PATH", path)
    return path
