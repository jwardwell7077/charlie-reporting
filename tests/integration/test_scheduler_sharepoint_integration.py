"""
Integration: scheduler <-> sharepoint_sim (in-process, no HTTP).

Flow:
1) Pre-generate sim datasets into a temp output root via env SP_SIM_OUTPUT_DIR
2) Scheduler.SyncJob lists and downloads only non-ingested files
3) Assert files are downloaded to ingestion_dir and filtering works
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

import scheduler_sharepoint_api as sp_api
from scheduler import SyncJob, SharePointClient, DBServiceClient


@pytest.fixture()
def sim_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "sim_root"
    root.mkdir()
    monkeypatch.setenv("SP_SIM_OUTPUT_DIR", str(root))
    # reset any cached sim
    sp_api._generator = None  # type: ignore[attr-defined]
    sp_api._storage = None  # type: ignore[attr-defined]
    return root


@pytest.fixture()
def scheduler_config(tmp_path: Path) -> Dict[str, Any]:
    return {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(tmp_path / "ingest"),
        "interval_minutes": 60,
    }


def test_scheduler_lists_and_downloads_new_files(sim_root: Path, scheduler_config: Dict[str, Any]) -> None:
    # 1) generate two datasets
    created = sp_api.pregenerate_datasets(["ACQ", "Dials"], rows=5)
    assert len(created) == 2

    # 2) prepare scheduler with stub DB that claims one already ingested
    sp_client = SharePointClient()
    db_client = DBServiceClient()
    db_client.get_ingested_files = lambda s, e: [created[0]]  # type: ignore[method-assign]

    job = SyncJob(config=scheduler_config, sharepoint_client=sp_client, db_service_client=db_client)

    downloaded = job.run()

    # 3) assert only the non-ingested file downloaded
    assert len(downloaded) == 1
    assert created[1] in downloaded
    dest = Path(scheduler_config["ingestion_dir"]) / created[1]
    assert dest.exists()
