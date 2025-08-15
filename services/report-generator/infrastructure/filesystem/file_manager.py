"""File Management Implementation
Production implementation of IFileManager interface for file operations.
"""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from business.interfaces import IFileManager


class FileManagerImpl(IFileManager):
    """Production implementation of file management operations.

    Handles:
    - Atomic file writing with temporary files
    - Cross - platform path handling
    - File validation and permissions
    - Safe file operations with rollback capability
    """

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "charlie - reporting"
        self.temp_dir.mkdir(exist_ok=True)

    async def save_file(self, content: str | bytes, file_path: Path) -> str:
        """Save content to file using atomic operations.

        Args:
            content: File content as string or bytes
            file_path: Target file path

        Returns:
            Absolute path of saved file

        Raises:
            OSError: If file cannot be written
            PermissionError: If insufficient permissions
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Use asyncio for non - blocking file operations
        loop = asyncio.get_event_loop()
        result_path = await loop.run_in_executor(
            None,
            self.save_file_sync,
            content,
            file_path
        )

        return result_path

    def save_file_sync(self, content: str | bytes, file_path: Path) -> str:
        """Synchronous atomic file writing implementation."""
        # Create temporary file in same directory for atomic move
        temp_path = file_path.parent / f".tmp_{file_path.name}_{os.getpid()}"

        try:
            # Write to temporary file first
            if isinstance(content, str):
                temp_path.write_text(content, encoding='utf-8')
            else:
                temp_path.write_bytes(content)

            # Atomic move to final location
            shutil.move(str(temp_path), str(file_path))

            return str(file_path.absolute())

        except Exception as e:
            # Cleanup temporary file if it exists
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise OSError(f"Failed to save file {file_path}: {e}") from e

    async def read_file(self, file_path: Path) -> bytes:
        """Read file content as bytes.

        Args:
            file_path: Path to file to read

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file isn't readable
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise OSError(f"Path is not a file: {file_path}")

        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            None,
            file_path.read_bytes
        )

        return content

    async def delete_file(self, file_path: Path) -> bool:
        """Delete file if it exists.

        Args:
            file_path: Path to file to delete

        Returns:
            True if file was deleted, False if it didn't exist

        Raises:
            PermissionError: If insufficient permissions to delete
        """
        if not file_path.exists():
            return False

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            file_path.unlink
        )

        return True

    async def file_exists(self, file_path: Path) -> bool:
        """Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists and is a file
        """
        return file_path.exists() and file_path.is_file()
