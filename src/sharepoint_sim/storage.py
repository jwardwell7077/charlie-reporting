"""Simple filesystem storage for generated CSV files."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StoredFile:
    """Lightweight wrapper around a stored CSV path."""

    path: Path

    @property
    def name(self) -> str:  # pragma: no cover - trivial
        """Filename (basename)."""
        return self.path.name

    def size(self) -> int:  # pragma: no cover - trivial
        """File size in bytes."""
        return self.path.stat().st_size


class Storage:
    """Filesystem storage operations for simulator output CSVs."""

    def __init__(self, root: Path) -> None:
        """Create storage ensuring root directory exists."""
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_csv(
        self, name: str, header: list[str], rows: Iterable[dict[str, str]]
    ) -> Path:
        """Write a CSV file with the given header and row dictionaries."""
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as f:
            f.write(",".join(header) + "\n")
            for r in rows:
                f.write(",".join(r[h] for h in header) + "\n")
        return path

    def list_files(self) -> list[StoredFile]:
        """Return stored CSV files (sorted)."""
        return [StoredFile(p) for p in sorted(self.root.glob("*.csv"))]

    def reset(self) -> None:
        """Remove all CSV files in storage root."""
        for p in self.root.glob("*.csv"):
            p.unlink()

__all__ = ["Storage", "StoredFile"]
