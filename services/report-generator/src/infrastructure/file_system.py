"""
File System Infrastructure Implementations
Real implementations for directory processing and file management
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..business.interfaces import IDirectoryProcessor, IFileManager
from ..business.exceptions import DirectoryException, FileException


class DirectoryProcessorImpl(IDirectoryProcessor):
    """
    Real implementation of directory scanning and processing
    """
    
    def __init__(self):
        self._supported_extensions = {'.csv', '.txt', '.tsv'}
    
    async def scan_directory(
        self, directory_path: str, pattern: str = "*.csv"
    ) -> List[str]:
        """
        Scan directory for files matching pattern
        
        Args:
            directory_path: Path to scan
            pattern: File pattern to match (e.g., "*.csv")
            
        Returns:
            List of matching file paths
            
        Raises:
            DirectoryException: If directory doesn't exist or can't be accessed
        """
        try:
            path = Path(directory_path)
            
            if not path.exists():
                raise DirectoryException(
                    f"Directory does not exist: {directory_path}"
                )
            
            if not path.is_dir():
                raise DirectoryException(
                    f"Path is not a directory: {directory_path}"
                )
            
            # Convert glob pattern to pathlib pattern
            glob_pattern = pattern if pattern else "*.csv"
            
            # Find matching files
            matching_files = []
            for file_path in path.glob(glob_pattern):
                is_file = file_path.is_file()
                suffix_lower = file_path.suffix.lower()
                is_supported = suffix_lower in self._supported_extensions
                if is_file and is_supported:
                    matching_files.append(str(file_path.absolute()))
            
            # Sort files by modification time (newest first)
            matching_files.sort(
                key=lambda f: os.path.getmtime(f),
                reverse=True
            )
            
            return matching_files
            
        except PermissionError:
            raise DirectoryException(
                f"Permission denied accessing directory: {directory_path}"
            )
        except Exception as e:
            raise DirectoryException(
                f"Error scanning directory {directory_path}: {str(e)}"
            )
    
    async def get_directory_stats(self, directory_path: str) -> Dict[str, Any]:
        """
        Get statistics about directory contents
        
        Args:
            directory_path: Path to analyze
            
        Returns:
            Dictionary with directory statistics
        """
        try:
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                return {"error": "Directory not found or not accessible"}
            
            stats = {
                "total_files": 0,
                "csv_files": 0,
                "total_size_bytes": 0,
                "last_modified": None,
                "file_extensions": {},
                "directory_path": str(path.absolute())
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
                        if stats["last_modified"] is None or mtime > stats["last_modified"]:
                            stats["last_modified"] = mtime
                        
                        # Track extensions
                        ext = file_path.suffix.lower()
                        if ext:
                            stats["file_extensions"][ext] = stats["file_extensions"].get(ext, 0) + 1
                            
                            # Count CSV files specifically
                            if ext in {'.csv', '.tsv'}:
                                stats["csv_files"] += 1
                    
                    except (OSError, PermissionError):
                        # Skip files we can't access
                        continue
            
            return stats
            
        except Exception as e:
            return {"error": f"Error analyzing directory: {str(e)}"}


class FileManagerImpl(IFileManager):
    """
    Real implementation of file operations
    """
    
    def __init__(self):
        self._max_file_size = 100 * 1024 * 1024  # 100MB default
    
    async def read_file(self, file_path: str) -> bytes:
        """
        Read file contents as bytes
        
        Args:
            file_path: Path to file to read
            
        Returns:
            File contents as bytes
            
        Raises:
            FileException: If file can't be read
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileException(f"File does not exist: {file_path}")
            
            if not path.is_file():
                raise FileException(f"Path is not a file: {file_path}")
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self._max_file_size:
                raise FileException(
                    f"File too large: {file_size} bytes (max: {self._max_file_size})"
                )
            
            # Use asyncio to read file without blocking
            def _read_file_sync():
                with open(path, 'rb') as f:
                    return f.read()
            
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, _read_file_sync)
            
            return content
            
        except PermissionError:
            raise FileException(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise FileException(f"Error reading file {file_path}: {str(e)}")
    
    async def write_file(self, file_path: str, content: bytes) -> bool:
        """
        Write content to file
        
        Args:
            file_path: Path where to write file
            content: Content to write
            
        Returns:
            True if successful
            
        Raises:
            FileException: If file can't be written
        """
        try:
            path = Path(file_path)
            
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use asyncio to write file without blocking
            def _write_file_sync():
                with open(path, 'wb') as f:
                    f.write(content)
                return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _write_file_sync)
            
            return success
            
        except PermissionError:
            raise FileException(f"Permission denied writing file: {file_path}")
        except Exception as e:
            raise FileException(f"Error writing file {file_path}: {str(e)}")
    
    async def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move file from source to destination
        
        Args:
            source_path: Current file location
            destination_path: Target file location
            
        Returns:
            True if successful
            
        Raises:
            FileException: If file can't be moved
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if not source.exists():
                raise FileException(f"Source file does not exist: {source_path}")
            
            if not source.is_file():
                raise FileException(f"Source is not a file: {source_path}")
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use asyncio to move file without blocking
            def _move_file_sync():
                shutil.move(str(source), str(destination))
                return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _move_file_sync)
            
            return success
            
        except PermissionError:
            raise FileException(f"Permission denied moving file from {source_path} to {destination_path}")
        except Exception as e:
            raise FileException(f"Error moving file from {source_path} to {destination_path}: {str(e)}")
    
    async def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy file from source to destination
        
        Args:
            source_path: Source file location
            destination_path: Target file location
            
        Returns:
            True if successful
            
        Raises:
            FileException: If file can't be copied
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if not source.exists():
                raise FileException(f"Source file does not exist: {source_path}")
            
            if not source.is_file():
                raise FileException(f"Source is not a file: {source_path}")
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Use asyncio to copy file without blocking
            def _copy_file_sync():
                shutil.copy2(str(source), str(destination))
                return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _copy_file_sync)
            
            return success
            
        except PermissionError:
            raise FileException(f"Permission denied copying file from {source_path} to {destination_path}")
        except Exception as e:
            raise FileException(f"Error copying file from {source_path} to {destination_path}: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful
            
        Raises:
            FileException: If file can't be deleted
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                # File already doesn't exist, consider success
                return True
            
            if not path.is_file():
                raise FileException(f"Path is not a file: {file_path}")
            
            # Use asyncio to delete file without blocking
            def _delete_file_sync():
                path.unlink()
                return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, _delete_file_sync)
            
            return success
            
        except PermissionError:
            raise FileException(f"Permission denied deleting file: {file_path}")
        except Exception as e:
            raise FileException(f"Error deleting file {file_path}: {str(e)}")
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
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
                "is_writable": os.access(path, os.W_OK)
            }
            
        except Exception as e:
            return {"error": f"Error getting file info: {str(e)}"}
