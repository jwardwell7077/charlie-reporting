"""Tests for extended simulator API metadata and bulk generation."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sharepoint_sim.api import router as sim_router  # type: ignore


@pytest.fixture(name="client")
def client_fixture() -> TestClient:  # type: ignore[type-arg]
    try:
        from foundation.src.services.api import app as foundation_app  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - fallback
        pytest.skip("Foundation service app not available")
    if not any(getattr(r, "path", "").startswith("/sim") for r in foundation_app.router.routes):  # type: ignore[attr-defined]
        foundation_app.include_router(sim_router)  # type: ignore[arg-type]
    return TestClient(foundation_app)


def test_list_datasets(client: TestClient) -> None:  # type: ignore[type-arg]
    resp = client.get("/sim/datasets")
    assert resp.status_code == 200
    payload = resp.json()
    assert "datasets" in payload
    names = {d["name"] for d in payload["datasets"]}
    for required in {"ACQ", "Productivity"}:
        assert required in names
    for d in payload["datasets"]:
        assert isinstance(d["headers"], list)
        assert isinstance(d["roles"], list)


def test_get_dataset_known_and_unknown(client: TestClient) -> None:  # type: ignore[type-arg]
    ok = client.get("/sim/datasets/ACQ")
    assert ok.status_code == 200
    data = ok.json()
    assert data["name"] == "ACQ"
    assert isinstance(data["headers"], list)
    missing = client.get("/sim/datasets/DOES_NOT_EXIST")
    assert missing.status_code == 404


def test_generate_all_creates_files(tmp_path: Path, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[type-arg]
    monkeypatch.setenv("SP_SIM_OUTPUT_DIR", str(tmp_path))
    # Rebind underlying service to pick up new env var (module created earlier)
    from sharepoint_sim import api as sim_api  # type: ignore
    from sharepoint_sim.service import SharePointCSVGenerator  # type: ignore

    sim_api._service = SharePointCSVGenerator()  # type: ignore[attr-defined]
    resp = client.post("/sim/generate/all")
    assert resp.status_code == 200
    created = resp.json()["files"]
    assert created, "Expected files returned"
    for meta in created:
        f = tmp_path / meta["filename"]
        if not f.is_file():
            # Debug aid: list directory contents
            print("DEBUG root contents:", list(tmp_path.iterdir()))
        assert f.is_file()


def test_spec_endpoint(client: TestClient) -> None:  # type: ignore[type-arg]
    resp = client.get("/sim/spec")
    assert resp.status_code == 200
    text = resp.text
    assert text, "Spec endpoint should return text"
