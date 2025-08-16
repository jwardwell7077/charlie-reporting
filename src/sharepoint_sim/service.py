"""Orchestrator service combining generators, storage, naming, and config."""
from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Dict, List

from sharepoint_sim.config import load_config
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import load_roster, Roster
from sharepoint_sim.file_naming import dataset_filename
from sharepoint_sim.storage import Storage

# Generators
from sharepoint_sim.datasets.acq import ACQGenerator
from sharepoint_sim.datasets.productivity import ProductivityGenerator
from sharepoint_sim.datasets.qcbs import QCBSGenerator
from sharepoint_sim.datasets.resc import RESCGenerator
from sharepoint_sim.datasets.dials import DialsGenerator
from sharepoint_sim.datasets.ib_calls import IBCallsGenerator
from sharepoint_sim.datasets.campaign_interactions import CampaignInteractionsGenerator

GENERATOR_MAP = {
    "ACQ": ACQGenerator,
    "Productivity": ProductivityGenerator,
    "QCBS": QCBSGenerator,
    "RESC": RESCGenerator,
    "Dials": DialsGenerator,
    "IB_Calls": IBCallsGenerator,
    "Campaign_Interactions": CampaignInteractionsGenerator,
}


class SharePointCSVGenerator:
    def __init__(self, root_dir: Path | None = None, seed: int | None = None):
        cfg = load_config()
        self.seed = seed if seed is not None else cfg.seed
        self.rnd = RandomProvider(seed=self.seed)
        self._roster: Roster | None = None
        self.root_dir = root_dir or cfg.output_dir
        self.storage = Storage(self.root_dir)
        self._lock = Lock()

    def _get_roster(self) -> Roster:
        if self._roster is None:
            self._roster = load_roster()
        return self._roster

    def _get_generator(self, dataset: str):
        cls = GENERATOR_MAP.get(dataset)
        if cls is None:
            raise ValueError(f"Unknown dataset {dataset}")
        return cls(self._get_roster(), self.rnd)

    def generate(self, dataset: str, rows: int | None = None) -> Path:
        with self._lock:
            gen = self._get_generator(dataset)
            row_dicts = gen.build(rows)
            name = dataset_filename(dataset, self.rnd.now())
            return self.storage.write_csv(name, list(gen.headers), row_dicts)

    def generate_many(self, datasets: list[str], rows: int | Dict[str, int] | None = None) -> List[Path]:
        outputs: List[Path] = []
        for d in datasets:
            r = None
            if isinstance(rows, int):
                r = rows
            elif isinstance(rows, dict):
                r = rows.get(d)
            outputs.append(self.generate(d, r))
        return outputs

    def list_files(self):
        return [
            {"filename": f.name, "size": f.size()} for f in self.storage.list_files()
        ]

    def reset(self):
        with self._lock:
            self.storage.reset()
            self._roster = None

__all__ = ["SharePointCSVGenerator"]
