"""Simple filesystem storage for generated CSV files."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class StoredFile:
    path: Path

    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return self.path.name

    def size(self) -> int:  # pragma: no cover - trivial
        return self.path.stat().st_size


class Storage:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_csv(self, name: str, header: list[str], rows: Iterable[dict[str, str]]) -> Path:
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as f:
            f.write(",".join(header) + "\n")
            for r in rows:
                f.write(",".join(r[h] for h in header) + "\n")
        return path

    def list_files(self) -> list[StoredFile]:
        return [StoredFile(p) for p in sorted(self.root.glob("*.csv"))]

    def reset(self) -> None:
        for p in self.root.glob("*.csv"):
            p.unlink()

__all__ = ["Storage", "StoredFile"]
