"""Directory Processing Implementation
Production implementation of IDirectoryProcessor interface for file
system operations.
"""

import asyncio
import glob
import os
from pathlib import Path

from business.interfaces import IDirectoryProcessor


class DirectoryProcessorImpl(IDirectoryProcessor):
    """Production implementation of directory processing for CSV file discovery.

    Handles file system scanning with support for:
    - Glob pattern matching
    - Recursive directory traversal
    - File filtering and validation
    - Cross - platform path handling
    """

    def __init__(self):
        self.supported_extensions = {'.csv'}

    async def scan_directory(self, directory_path: Path) -> list[Path]:
        """Scan directory for CSV files matching expected patterns.

        Args:
            directory_path: Path to directory to scan

        Returns:
            List of CSV file paths found

        Raises:
            OSError: If directory doesn't exist or isn't accessible
        """
        if not directory_path.exists():
            raise OSError(f"Directory does not exist: {directory_path}")

        if not directory_path.is_dir():
            raise OSError(f"Path is not a directory: {directory_path}")

        # Use asyncio to avoid blocking on large directories
        loop = asyncio.get_event_loop()
        csv_files = await loop.run_in_executor(
            None,
            self.scan_directory_sync,
            directory_path
        )

        return csv_files

    def scan_directory_sync(self, directory_path: Path) -> list[Path]:
        """Synchronous directory scanning implementation."""
        csv_files = []

        # Scan for CSV files with common patterns
        patterns = [
            "*.csv",
            "**/*.csv",  # Recursive search
        ]

        for pattern in patterns:
            search_path = directory_path / pattern
            matches = glob.glob(str(search_path), recursive=True)

            for match in matches:
                file_path = Path(match)

                # Validate file
                if self.is_valid_csv_file(file_path):
                    csv_files.append(file_path)

        # Remove duplicates and sort
        unique_files = list(set(csv_files))
        unique_files.sort()

        return unique_files

    def is_valid_csv_file(self, file_path: Path) -> bool:
        """Validate if file is a processable CSV file.

        Args:
            file_path: Path to file to validate

        Returns:
            True if file is valid CSV, False otherwise
        """
        try:
            # Check extension
            if file_path.suffix.lower() not in self.supported_extensions:
                return False

            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return False

            # Check if file has content
            if file_path.stat().st_size == 0:
                return False

            # Check if file is accessible
            if not os.access(file_path, os.R_OK):
                return False

            return True

        except (OSError, PermissionError):
            return False
