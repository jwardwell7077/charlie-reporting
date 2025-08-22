"""Shared pytest fixtures for simulator and DB API clients."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from sharepoint_sim.server import app as sim_app
from db_service_api import app as db_app


@pytest.fixture()
def sim_client() -> TestClient:
    client = TestClient(sim_app)
    client.post("/sim/reset")
    return client


@pytest.fixture()
def db_client() -> TestClient:
    return TestClient(db_app)
