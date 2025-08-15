import pytest
from httpx import ASGITransport, AsyncClient

from src.interfaces.rest.main import app

pytestmark = pytest.mark.asyncio


async def test_health_endpoint_returns_healthy():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        resp = await client.get("/health/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database-service"
    assert "timestamp" in data
