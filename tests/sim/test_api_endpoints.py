from __future__ import annotations

from fastapi.testclient import TestClient
from pathlib import Path

from services.api import app


def test_sim_invalid_dataset():
    client = TestClient(app)
    r = client.post("/sim/generate", params={"types":"NOPE"})
    assert r.status_code >= 400
