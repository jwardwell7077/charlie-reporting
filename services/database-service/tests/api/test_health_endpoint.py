from httpx import AsyncClient
import pytest

from src.interfaces.rest.main import app

pytestmark = pytest.mark.asyncio


async def test_health_endpoint_returns_healthy():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database-service"
    assert "timestamp" in data
