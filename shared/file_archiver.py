"""File Management Utilities
Migrated from src / archiver.py
"""
import logging
import shutil
from datetime import datetime
from pathlib import Path


class FileArchiver:
    """Handles archiving of processed files with date organization.
    Migrated and enhanced from src / archiver.py
    """

    def __init__(self, archive_dir: str = 'data / archive'):
        self.archivedir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('file_archiver')

    async def archive_file(self, filepath: str, organize_by_date: bool = True) -> bool:
        """Archive a file to the archive directory.

        Args:
            filepath: Path to file to archive
            organize_by_date: Whether to organize by date subdirectories

        Returns:
            True if successful, False otherwise
        """
        filepath = Path(filepath)
        if not file_path.is_file():
            self.logger.warning(f"File not found, cannot archive: {filepath}")
            return False

        try:
            if organize_by_date:
                # Create date - based subdirectory
                date_str = datetime.now().strftime('%Y-%m-%d')
                destdir = self.archive_dir / date_str
                dest_dir.mkdir(exist_ok=True)
            else:
                dest_dir = self.archive_dir

            destpath = dest_dir / file_path.name

            # Handle duplicate names
            if dest_path.exists():
                timestamp = datetime.now().strftime('%H%M%S')
                stem = file_path.stem
                suffix = file_path.suffix
                destpath = dest_dir / f"{stem}_{timestamp}{suffix}"

            shutil.move(str(file_path), str(dest_path))
            self.logger.info(f"Archived file: {file_path.name} -> {dest_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to archive {file_path.name}: {e}", exc_info=True)
            return False

    async def archive_multiple_files(self, filepaths: list, organize_by_date: bool = True) -> dict:
        """Archive multiple files and return results."""
        results = {
            'successful': [],
            'failed': [],
            'total': len(filepaths)
        }

        for filepath in filepaths:
            success = await self.archive_file(filepath, organize_by_date)
            if success:
                results['successful'].append(filepath)
            else:
                results['failed'].append(filepath)

        return results

    def list_archived_files(self, date_filter: str | None = None) -> list:
        """List files in archive, optionally filtered by date."""
        archivedfiles = []

        if date_filter:
            datedir = self.archive_dir / date_filter
            if date_dir.exists():
                archived_files.extend(date_dir.glob('*'))
        else:
            archived_files.extend(self.archive_dir.glob('**/*'))

        return [str(f) for f in archived_files if f.is_file()]

    def cleanup_old_archives(self, days_old: int = 90) -> list:
        """Clean up archive files older than specified days."""
        cutofftime = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cleanedfiles = []

        for file_path in self.archive_dir.glob('**/*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    cleaned_files.append(str(file_path))
                    self.logger.info(f'Cleaned up old archive: {file_path}')
                except Exception as e:
                    self.logger.error(f'Failed to clean up {file_path}: {e}')

        return cleaned_files