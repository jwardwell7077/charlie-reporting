"""Test that the SharePoint simulator FastAPI server launches and exposes OpenAPI schema."""
from fastapi.testclient import TestClient
from sharepoint_sim.server import app

def test_openapi_schema_available():
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "SharePoint CSV Simulator API"

def test_server_health_and_docs():
    client = TestClient(app)
    # Docs endpoints
    resp = client.get("/docs")
    assert resp.status_code == 200
    resp = client.get("/redoc")
    assert resp.status_code == 200
    # Simulator endpoint basic check
    resp = client.get("/sim/datasets")
    assert resp.status_code == 200
