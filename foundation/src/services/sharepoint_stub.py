"""SharePoint API stub.

Future replacement with real Graph integration. For now, simulates upload
and listing of files by interacting with a configured local directory.
"""
from __future__ import annotations

from pathlib import Path
from typing import List


class SharePointStub:
    def __init__(self, library_root: Path):
        self.library_root = library_root
        self.library_root.mkdir(parents=True, exist_ok=True)

    def upload(self, local_file: Path) -> Path:
        target = self.library_root / local_file.name
        target.write_bytes(local_file.read_bytes())
        return target

    def list_files(self) -> List[Path]:
        return sorted([p for p in self.library_root.iterdir() if p.is_file()])
