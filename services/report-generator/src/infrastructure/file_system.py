"""File system infrastructure implementations.

Provides concrete implementations for directory scanning and file operations used by the
business layer. Aligns method signatures with declared interfaces while offering
additional helper operations (read/write/move/copy/delete).
"""

import asyncio
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from ..business.exceptions import DirectoryException, FileException
from ..business.interfaces import IDirectoryProcessor, IFileManager


class DirectoryProcessorImpl(IDirectoryProcessor):
    """Real implementation of directory scanning and processing."""

    def __init__(self) -> None:
        self.supported_extensions = {".csv", ".txt", ".tsv"}

    # Interface compliance (expects Path + date_filter) – simplified implementation
    async def scan_directory(self, directory_path: Path, date_filter: str) -> list[Path]:  # type: ignore[override]
        """Scan a directory for CSV-like files containing the date filter substring."""
        try:
            if not directory_path.exists():
                raise DirectoryException(f"Directory does not exist: {directory_path}")
            if not directory_path.is_dir():
                raise DirectoryException(f"Path is not a directory: {directory_path}")

            candidates = [
                p for p in directory_path.iterdir() if p.is_file() and p.suffix.lower() in self.supported_extensions
            ]
            filtered = [p for p in candidates if date_filter in p.name]
            filtered.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return filtered
        except PermissionError:
            raise DirectoryException(f"Permission denied accessing directory: {directory_path}")
        except Exception as e:  # noqa: BLE001
            raise DirectoryException(f"Error scanning directory {directory_path}: {e}") from e

    async def validate_directory(self, directory_path: Path) -> dict[str, Any]:  # type: ignore[override]
        """Validate directory accessibility (interface method)."""
        if not directory_path.exists():
            return {"valid": False, "error": "not_found"}
        if not directory_path.is_dir():
            return {"valid": False, "error": "not_directory"}
        return {"valid": True}

    # Backwards-compatible helper retaining pattern-based scan
    async def scan_directory_pattern(self, directory_path: str, pattern: str = "*.csv") -> list[str]:
        """Legacy pattern-based scan retained for compatibility."""
        try:
            path = Path(directory_path)
            if not path.exists():
                raise DirectoryException(f"Directory does not exist: {directory_path}")
            if not path.is_dir():
                raise DirectoryException(f"Path is not a directory: {directory_path}")
            glob_pattern = pattern or "*.csv"
            matching_files: list[str] = []
            for file_path in path.glob(glob_pattern):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    matching_files.append(str(file_path.absolute()))
            matching_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            return matching_files
        except PermissionError:
            raise DirectoryException(f"Permission denied accessing directory: {directory_path}")
        except Exception as e:  # noqa: BLE001
            raise DirectoryException(f"Error scanning directory {directory_path}: {e}") from e

    async def get_directory_stats(self, directory_path: str) -> dict[str, Any]:
        """Get statistics about directory contents

        Args:
            directory_path: Path to analyze

        Returns:
            Dictionary with directory statistics
        """
        try:
            path = Path(directory_path)

            if not path.exists() or not path.is_dir():
                return {"error": "Directory not found or not accessible"}

            stats: dict[str, Any] = {
                "total_files": 0,
                "csv_files": 0,
                "total_size_bytes": 0,
                "last_modified": None,  # datetime | None
                "file_extensions": {},  # dict[str, int]
                "directory_path": str(path.absolute()),
            }

            for file_path in path.rglob("*"):
                if file_path.is_file():
                    stats["total_files"] += 1

                    # Track file size
                    try:
                        file_size = file_path.stat().st_size
                        stats["total_size_bytes"] += file_size

                        # Track modification time
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        last_mod = stats["last_modified"]
                        if last_mod is None or (isinstance(last_mod, datetime) and mtime > last_mod):
                            stats["last_modified"] = mtime

                        # Track extensions
                        ext = file_path.suffix.lower()
                        if ext:
                            fe: dict[str, int] = stats["file_extensions"]
                            fe[ext] = fe.get(ext, 0) + 1

                            # Count CSV files specifically
                            if ext in {".csv", ".tsv"}:
                                stats["csv_files"] += 1

                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue

            return stats

        except Exception as e:
            return {"error": f"Error analyzing directory: {str(e)}"}


class FileManagerImpl(IFileManager):
    """Real implementation of file operations."""

    def __init__(self) -> None:
        self.max_file_size = 100 * 1024 * 1024  # 100MB

    # Interface-required methods -------------------------------------------------
    async def save_file(self, content: bytes, file_path: Path) -> bool:  # type: ignore[override]
        return await self.write_file(str(file_path), content)

    async def archive_file(self, source_path: Path, archive_path: Path) -> bool:  # type: ignore[override]
        return await self.move_file(str(source_path), str(archive_path))

    async def file_exists(self, file_path: Path) -> bool:  # type: ignore[override]
        return Path(file_path).exists()

    # Extended operations ---------------------------------------------------------
    async def read_file(self, file_path: str) -> bytes:
        """Read file contents as bytes."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileException(f"File does not exist: {file_path}")
            if not path.is_file():
                raise FileException(f"Path is not a file: {file_path}")
            file_size = path.stat().st_size
            if file_size > self.max_file_size:
                raise FileException(f"File too large: {file_size} bytes (max: {self.max_file_size})")

            def read_file_sync() -> bytes:
                with open(path, "rb") as f:
                    return f.read()

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, read_file_sync)
        except PermissionError:
            raise FileException(f"Permission denied reading file: {file_path}")
        except Exception as e:  # noqa: BLE001
            raise FileException(f"Error reading file {file_path}: {e}") from e

    async def write_file(self, file_path: str, content: bytes) -> bool:
        """Write content to file."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            def write_file_sync() -> bool:
                with open(path, "wb") as f:
                    f.write(content)
                return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, write_file_sync)
        except PermissionError:
            raise FileException(f"Permission denied writing file: {file_path}")
        except Exception as e:  # noqa: BLE001
            raise FileException(f"Error writing file {file_path}: {e}") from e

    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move file from source to destination."""
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            if not source.exists():
                raise FileException(f"Source file does not exist: {source_path}")
            if not source.is_file():
                raise FileException(f"Source is not a file: {source_path}")
            destination.parent.mkdir(parents=True, exist_ok=True)

            def move_file_sync() -> bool:
                shutil.move(str(source), str(destination))
                return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, move_file_sync)
        except PermissionError:
            raise FileException(f"Permission denied moving file from {source_path} to {destination_path}")
        except Exception as e:  # noqa: BLE001
            raise FileException(f"Error moving file from {source_path} to {destination_path}: {e}") from e

    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy file from source to destination."""
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            if not source.exists():
                raise FileException(f"Source file does not exist: {source_path}")
            if not source.is_file():
                raise FileException(f"Source is not a file: {source_path}")
            destination.parent.mkdir(parents=True, exist_ok=True)

            def copy_file_sync() -> bool:
                shutil.copy2(str(source), str(destination))
                return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, copy_file_sync)
        except PermissionError:
            raise FileException(f"Permission denied copying file from {source_path} to {destination_path}")
        except Exception as e:  # noqa: BLE001
            raise FileException(f"Error copying file from {source_path} to {destination_path}: {e}") from e

    async def delete_file(self, file_path: str) -> bool:
        """Delete file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return True
            if not path.is_file():
                raise FileException(f"Path is not a file: {file_path}")

            def delete_file_sync() -> bool:
                path.unlink()
                return True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, delete_file_sync)
        except PermissionError:
            raise FileException(f"Permission denied deleting file: {file_path}")
        except Exception as e:  # noqa: BLE001
            raise FileException(f"Error deleting file {file_path}: {e}") from e

    async def get_file_info(self, file_path: str) -> dict[str, Any]:
        """Get file information."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": "File not found"}
            if not path.is_file():
                return {"error": "Path is not a file"}
            stat = path.stat()
            return {
                "path": str(path.absolute()),
                "name": path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "extension": path.suffix.lower(),
                "is_readable": os.access(path, os.R_OK),
                "is_writable": os.access(path, os.W_OK),
            }
        except Exception as e:  # noqa: BLE001
            return {"error": f"Error getting file info: {e}"}
