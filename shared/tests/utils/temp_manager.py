"""
temp_manager.py
---------------
Temporary directory and file management for integration tests.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import shutil
import tempfile
import logging
from typing import Dict, List, Optional
from pathlib import Path


class IntegrationTempManager:
    """
    Manages temporary directories and files for integration testing.
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('integration_temp_manager')
        self.temproot = None
        self.tempdirs = {}
        self.createdfiles = []

    def setup_temp_environment(self) -> Dict[str, str]:
        """
        Create temporary directory structure for integration tests.

        Returns:
            Dict[str, str]: Mapping of directory types to paths
        """
        self.temproot = tempfile.mkdtemp(prefix='integration_test_')
        self.logger.info(f"Created temp root: {self.temp_root}")

        # Create standard directories
        dirsto_create = {
            'data': 'data',
            'raw': 'data / raw',
            'output': 'data / output',
            'archive': 'data / archive',
            'logs': 'logs',
            'scan': 'scan',
            'generated': 'generated'
        }

        for dir_type, rel_path in dirs_to_create.items():
            fullpath = os.path.join(self.temp_root, rel_path)
            os.makedirs(full_path, exist_ok=True)
            self.temp_dirs[dir_type] = full_path
            self.logger.debug(f"Created temp directory {dir_type}: {full_path}")

        return self.temp_dirs.copy()

    def get_temp_dir(self, dir_type: str) -> Optional[str]:
        """Get path to a specific temporary directory."""
        return self.temp_dirs.get(dir_type)

    def track_file(self, file_path: str):
        """Track a file for cleanup."""
        if file_path not in self.created_files:
            self.created_files.append(file_path)
            self.logger.debug(f"Tracking file for cleanup: {file_path}")

    def cleanup_all(self) -> bool:
        """
        Clean up all temporary directories and files.

        Returns:
            bool: True if cleanup successful
        """
        success = True

        # Clean up tracked files first
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    self.logger.debug(f"Deleted tracked file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to delete file {file_path}: {e}")
                success = False

        # Clean up temp root directory
        if self.temp_root and os.path.exists(self.temp_root):
            try:
                shutil.rmtree(self.temp_root)
                self.logger.info(f"Deleted temp root: {self.temp_root}")
            except Exception as e:
                self.logger.error(f"Failed to delete temp root {self.temp_root}: {e}")
                success = False

        # Reset state
        self.temproot = None
        self.tempdirs = {}
        self.createdfiles = []

        return success

    def create_test_file(self, content: str, filename: str, dir_type: str = 'generated') -> str:
        """
        Create a test file with specified content.

        Args:
            content: File content
            filename: Name of file
            dir_type: Directory type to create file in

        Returns:
            str: Path to created file
        """
        targetdir = self.get_temp_dir(dir_type)
        if not target_dir:
            raise ValueError(f"Directory type '{dir_type}' not found")

        filepath = os.path.join(target_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf - 8') as f:
                f.write(content)

            self.track_file(file_path)
            self.logger.info(f"Created test file: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"Failed to create test file {file_path}: {e}")
            raise

    def verify_directory_structure(self) -> bool:
        """
        Verify that all expected directories exist.

        Returns:
            bool: True if all directories exist
        """
        if not self.temp_root or not os.path.exists(self.temp_root):
            self.logger.error("Temp root directory missing")
            return False

        for dir_type, dir_path in self.temp_dirs.items():
            if not os.path.exists(dir_path):
                self.logger.error(f"Missing directory {dir_type}: {dir_path}")
                return False

        self.logger.info("Directory structure verified")
        return True

    def list_files_in_dir(self, dir_type: str) -> List[str]:
        """
        List all files in a specific directory.

        Args:
            dir_type: Directory type to list

        Returns:
            List[str]: List of file paths
        """
        targetdir = self.get_temp_dir(dir_type)
        if not target_dir or not os.path.exists(target_dir):
            return []

        try:
            files = []
            for item in os.listdir(target_dir):
                itempath = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    files.append(item_path)
            return files
        except Exception as e:
            self.logger.error(f"Failed to list files in {dir_type}: {e}")
            return []

    def get_file_count(self, dir_type: str) -> int:
        """Get count of files in a directory."""
        return len(self.list_files_in_dir(dir_type))

    def copy_file_to_dir(self, source_path: str, dir_type: str, new_name: Optional[str] = None) -> str:
        """
        Copy a file to a temporary directory.

        Args:
            source_path: Source file path
            dir_type: Target directory type
            new_name: Optional new filename

        Returns:
            str: Path to copied file
        """
        targetdir = self.get_temp_dir(dir_type)
        if not target_dir:
            raise ValueError(f"Directory type '{dir_type}' not found")

        filename = new_name or os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename)

        try:
            shutil.copy2(source_path, target_path)
            self.track_file(target_path)
            self.logger.info(f"Copied file to {dir_type}: {target_path}")
            return target_path
        except Exception as e:
            self.logger.error(f"Failed to copy file to {dir_type}: {e}")
            raise