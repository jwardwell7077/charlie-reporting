"""Tests for error and edge cases in sharepoint_sim.api (100% coverage)."""
import pytest
from fastapi.testclient import TestClient
from sharepoint_sim.api import router as sim_router

@pytest.fixture(name="client")
def client_fixture():
    from sharepoint_sim.server import app
    # Ensure router is included (idempotent)
    if not any(getattr(r, "path", "").startswith("/sim") for r in app.router.routes):
        app.include_router(sim_router)
    return TestClient(app)

def test_generate_invalid_dataset(client):
    resp = client.post("/sim/generate", params={"types": "DOES_NOT_EXIST"})
    assert resp.status_code == 400
    assert "Unknown dataset" in resp.json()["detail"]

def test_get_dataset_404(client):
    resp = client.get("/sim/datasets/DOES_NOT_EXIST")
    assert resp.status_code == 404
    assert "Unknown dataset" in resp.json()["detail"]

def test_download_404(client):
    resp = client.get("/sim/download/DOES_NOT_EXIST.csv")
    assert resp.status_code == 404
    assert "File not found" in resp.json()["detail"]

def test_spec_addendum_not_found(client, monkeypatch):
    # Patch Path.is_file to always return False
    from pathlib import Path
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    resp = client.get("/sim/spec")
    assert resp.status_code == 200
    assert "not found" in resp.text.lower()
