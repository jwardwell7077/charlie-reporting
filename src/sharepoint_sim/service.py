"""Orchestrator service combining generators, storage, naming, and config."""
from __future__ import annotations

from pathlib import Path
from threading import Lock

from sharepoint_sim.config import load_config

# Generators
from sharepoint_sim.datasets.acq import ACQGenerator
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.datasets.campaign_interactions import CampaignInteractionsGenerator
from sharepoint_sim.datasets.dials import DialsGenerator
from sharepoint_sim.datasets.ib_calls import IBCallsGenerator
from sharepoint_sim.datasets.productivity import ProductivityGenerator
from sharepoint_sim.datasets.qcbs import QCBSGenerator
from sharepoint_sim.datasets.resc import RESCGenerator
from sharepoint_sim.file_naming import dataset_filename
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster
from sharepoint_sim.storage import Storage

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
    """Facade service to generate, list, and reset simulated SharePoint CSVs."""

    def __init__(self, root_dir: Path | None = None, seed: int | None = None) -> None:
        """Create a generator optionally overriding output root and RNG seed."""
        cfg = load_config()
        self.seed = seed if seed is not None else cfg.seed
        self.rnd = RandomProvider(seed=self.seed)
        self._roster: Roster | None = None
        self.root_dir = root_dir or cfg.output_dir
        self.storage = Storage(self.root_dir)
        self._lock = Lock()

    def _get_roster(self) -> Roster:
        """Lazily load roster (cached)."""
        if self._roster is None:
            self._roster = Roster()  # self-loading
        return self._roster

    def _get_generator(self, dataset: str) -> DatasetGenerator:
        """Return concrete dataset generator for a dataset name.

        Parameters
        ----------
        dataset: str
            Key identifying the dataset (must exist in GENERATOR_MAP).

        Returns:
        -------
        DatasetGenerator
            Instantiated concrete generator.

        Raises:
        ------
        ValueError
            If the provided dataset key is unknown.
        """
        cls = GENERATOR_MAP.get(dataset)
        if cls is None:
            raise ValueError(f"Unknown dataset {dataset}")
        return cls(self._get_roster(), self.rnd)

    def generate(self, dataset: str, rows: int | None = None) -> Path:
        """Generate a single dataset CSV and return its path."""
        with self._lock:
            gen = self._get_generator(dataset)
            row_dicts = gen.build(rows)
            name = dataset_filename(dataset, self.rnd.now())
            return self.storage.write_csv(name, list(gen.headers), row_dicts)

    def generate_many(
        self, datasets: list[str], rows: int | dict[str, int] | None = None
    ) -> list[Path]:
        """Generate multiple datasets (optionally overriding per-dataset row counts).

        Raises:
            ValueError: If datasets is not a list of strings.
        """
        if not isinstance(datasets, list) or not all(isinstance(d, str) for d in datasets):
            raise ValueError("datasets must be a list of strings")
        outputs: list[Path] = []
        for d in datasets:
            r: int | None = None
            if isinstance(rows, int):
                r = rows
            elif isinstance(rows, dict):
                r = rows.get(d)
            outputs.append(self.generate(d, r))
        return outputs

    def list_files(self) -> list[dict[str, int | str]]:
        """Return metadata for generated CSV files."""
        return [
            {"filename": f.name, "size": f.size()} for f in self.storage.list_files()
        ]

    def reset(self) -> None:
        """Delete all generated CSVs and clear cached roster."""
        with self._lock:
            self.storage.reset()
            self._roster = None

__all__ = ["SharePointCSVGenerator"]
