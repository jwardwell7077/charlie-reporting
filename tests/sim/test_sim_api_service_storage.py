"""Targeted tests for uncovered lines in sharepoint_sim.api, service, and storage."""
import pytest
from fastapi.testclient import TestClient
from sharepoint_sim.api import router
from sharepoint_sim.server import app
from sharepoint_sim.service import SharePointCSVGenerator
from sharepoint_sim.storage import Storage
from pathlib import Path

client = TestClient(app)

def test_api_generate_invalid_dataset():
    resp = client.post("/sim/generate", params={"types": "NotARealDataset"})
    assert resp.status_code == 400
    assert "Unknown dataset" in resp.json()["detail"]

def test_api_get_dataset_not_found():
    resp = client.get("/sim/datasets/NotARealDataset")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Unknown dataset"

def test_api_spec_addendum_missing(tmp_path, monkeypatch):
    # Patch Path to a temp dir with no spec addendum
    monkeypatch.chdir(tmp_path)
    resp = client.get("/sim/spec")
    assert resp.status_code == 200
    assert "not found" in resp.text.lower()

def test_api_download_file_not_found():
    resp = client.get("/sim/download/does_not_exist.csv")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "File not found"

def test_service_generate_many_dict_and_int():
    svc = SharePointCSVGenerator()
    # Should not raise for valid dict/int
    import pytest
    with pytest.raises(ValueError):
        svc.generate_many({"ACQ": 12, "Productivity": 13})
    with pytest.raises(ValueError):
        svc.generate_many(15)

def test_service_reset_and_list_files(tmp_path):
    storage = Storage(tmp_path)
    # Create a dummy file
    f = tmp_path / "dummy.csv"
    f.write_text("a,b,c\n1,2,3\n")
    assert len(storage.list_files()) == 1
    storage.reset()
    assert len(storage.list_files()) == 0
