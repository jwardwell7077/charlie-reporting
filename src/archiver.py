"""
archiver.py
-----------
Handles archiving of processed files.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import shutil

from logger import LoggerFactory


class Archiver:
    """
    Archiver encapsulates the logic for moving processed files to an archive directory,
    optionally organizing by date subfolders.
    """
    def __init__(self, archive_dir: str = 'data/archive', log_file: str = 'archiver.log'):
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)
        self.logger = LoggerFactory.get_logger('archiver', log_file)

    def archive(self, filepath: str):
        """
        Move the given file to the archive directory.
        """
        if not os.path.isfile(filepath):
            self.logger.warning(f"File not found, cannot archive: {filepath}")
            return

        filename = os.path.basename(filepath)
        dest_path = os.path.join(self.archive_dir, filename)
        try:
            shutil.move(filepath, dest_path)
            self.logger.info(f"Archived file: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to archive {filename}: {e}", exc_info=True)
