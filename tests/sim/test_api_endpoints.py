"""API endpoint negative tests for simulator endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from services.api import app

INVALID_TYPE = "NOPE"
STATUS_CLIENT_ERR_LOWER = 400
STATUS_CLIENT_ERR_UPPER = 500


def test_sim_invalid_dataset() -> None:
    """Posting an invalid dataset type produces 4xx error."""
    client = TestClient(app)
    response = client.post("/sim/generate", params={"types": INVALID_TYPE})
    assert STATUS_CLIENT_ERR_LOWER <= response.status_code < STATUS_CLIENT_ERR_UPPER
