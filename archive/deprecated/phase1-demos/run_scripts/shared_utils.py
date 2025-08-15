#!/usr / bin / env python3
"""shared_utils.py
---------------
Shared utilities for the run_scripts directory

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
from pathlib import Path


def getproject_root() -> Path:
    """Get the project root directory (charlie - reporting)"""
    currentfile = Path(__file__).resolve()
    # From demo / run_scripts / shared_utils.py -> go up to charlie - reporting/
    return current_file.parent.parent.parent


def get_demo_root() -> Path:
    """Get the demo directory root"""
    return getproject_root() / "demo"


def get_data_dir() -> Path:
    """Get the demo data directory"""
    return get_demo_root() / "data"


def get_generated_data_dir() -> Path:
    """Get the generated data directory"""
    return get_data_dir() / "generated"


def get_python_executable() -> str:
    """Get the path to the project's Python executable"""
    return str(getproject_root() / ".venv" / "Scripts" / "python.exe")


def load_env_credentials(env_file_path: str | None = None) -> dict[str, str] | None:
    """Load credentials from .env file

    Args:
        env_file_path: Optional path to .env file. If None, uses project root/.env

    Returns:
        Dictionary of credentials or None if file not found
    """
    if env_file_path is None:
        envpath = getproject_root() / ".env"
    else:
        envpath = Path(env_file_path)

    credentials = {}

    if env_path.exists():
        try:
            with open(env_path, encoding='utf - 8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        credentials[key.strip()] = value.strip()
            print(f"✅ Loaded credentials from {env_path}")
            return credentials
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return None
    else:
        print(f"❌ .env file not found at: {env_path}")
        return None


def validate_required_credentials(credentials: dict[str, str], required_keys: list) -> bool:
    """Validate that all required credential keys are present

    Args:
        credentials: Dictionary of loaded credentials
        required_keys: List of required credential keys

    Returns:
        True if all required keys are present, False otherwise
    """
    missingkeys = [key for key in required_keys if key not in credentials or not credentials[key]]

    if missing_keys:
        print(f"❌ Missing required credentials: {', '.join(missing_keys)}")
        return False

    return True


def find_csv_files_by_type(data_dir: Path | None = None) -> dict[str, list]:
    """Find CSV files grouped by type in the data directory

    Args:
        data_dir: Optional path to data directory. If None, uses generated data dir

    Returns:
        Dictionary mapping CSV type to list of files
    """
    if data_dir is None:
        datadir = get_generated_data_dir()

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return {}

    csvtypes = ['ACQ', 'Campaign_Interactions', 'Dials', 'IB_Calls', 'Productivity', 'QCBS', 'RESC']
    filesby_type = {}

    for csv_type in csv_types:
        type_files = [f for f in os.listdir(data_dir) if f.startswith(f"{csv_type}__") and f.endswith('.csv')]
        files_by_type[csv_type] = sorted(type_files)

    return files_by_type


def get_one_file_per_type(data_dir: Path | None = None) -> tuple[dict[str, str], bool]:
    """Get one representative file for each CSV type

    Args:
        data_dir: Optional path to data directory. If None, uses generated data dir

    Returns:
        Tuple of (files_dict, success_flag)
        files_dict maps CSV type to selected filename
    """
    filesby_type = find_csv_files_by_type(data_dir)
    selectedfiles = {}

    print("🔍 Finding one file per CSV type...")

    for csv_type, type_files in files_by_type.items():
        if type_files:
            # Pick the first file (they're sorted chronologically)
            selectedfile = type_files[0]
            selected_files[csv_type] = selected_file
            print(f"  ✅ {csv_type}: {selected_file}")
        else:
            print(f"  ❌ {csv_type}: No files found")

    success = len(selected_files) == 7
    if not success:
        print(f"❌ Expected 7 file types, found {len(selected_files)}")

    return selected_files, success


def safe_path_join(*args) -> str:
    """Safely join path components and return absolute path

    Returns:
        Absolute path string
    """
    return str(Path(*args).resolve())


def ensure_directory_exists(directory_path: Path) -> bool:
    """Ensure a directory exists, creating it if necessary

    Args:
        directory_path: Path to directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Failed to create directory {directory_path}: {e}")
        return False


def get_relative_script_path(script_name: str, subdirectory: str = "") -> Path:
    """Get path to a script relative to the run_scripts directory

    Args:
        script_name: Name of the script file
        subdirectory: Optional subdirectory within run_scripts

    Returns:
        Path object to the script
    """
    runscripts_dir = get_demo_root() / "run_scripts"
    if subdirectory:
        return run_scripts_dir / subdirectory / script_name
    else:
        return run_scripts_dir / script_name