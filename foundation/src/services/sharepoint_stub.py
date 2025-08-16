"""SharePoint API stub.

Future replacement with real Graph integration. For now, simulates upload
and listing of files by interacting with a configured local directory.
"""
from __future__ import annotations

from pathlib import Path


class SharePointStub:
    """Very small local directory abstraction simulating SharePoint library."""
    def __init__(self, library_root: Path) -> None:
        """Create stub wrapper around a local directory.

        Args:
            library_root: Directory acting as the pseudo SharePoint library.
        """
        self.library_root = library_root
        self.library_root.mkdir(parents=True, exist_ok=True)

    def upload(self, local_file: Path) -> Path:
        """Copy (simulate upload) a file into the library.

        Args:
            local_file: Source file on local filesystem.

        Returns:
            Destination path inside library.
        """
        target = self.library_root / local_file.name
        target.write_bytes(local_file.read_bytes())
        return target

    def list_files(self) -> list[Path]:
        """List all regular files currently in the library."""
        return sorted([p for p in self.library_root.iterdir() if p.is_file()])
