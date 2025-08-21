"""
Scheduler SharePoint/Graph API communication stubs.

Each stub calls a corresponding sim service function for now.
When ready to integrate the real API, replace the sim function calls with actual SharePoint/Graph API logic.
"""
from typing import List
from pathlib import Path

# --- SharePoint/Graph API Communication Stubs ---
def authenticate_sharepoint() -> None:
    """Authenticate with SharePoint/Graph API (stub)."""
    return sim_authenticate()

def list_sharepoint_files(folder: str) -> List[str]:
    """List files in a SharePoint/Graph API folder (stub).
    Args:
        folder (str): SharePoint folder path.
    Returns:
        List[str]: List of filenames.
    """
    return sim_list_files(folder)

def download_sharepoint_file(folder: str, filename: str, dest: Path) -> Path:
    """Download a file from SharePoint/Graph API (stub).
    Args:
        folder (str): SharePoint folder path.
        filename (str): File to download.
        dest (Path): Local destination path.
    Returns:
        Path: Path to downloaded file.
    """
    return sim_download_file(folder, filename, dest)

# --- Sim Service Functions (to be replaced with real API) ---
def sim_authenticate() -> None:
    """Simulate authentication (no-op for sim)."""
    pass

def sim_list_files(folder: str) -> List[str]:
    """Simulate listing files in a folder using the sim service."""
    # TODO: Implement actual call to sim service or mock
    return ["ACQ__2025-08-20_0800.csv", "Productivity__2025-08-20_0800.csv"]

def sim_download_file(folder: str, filename: str, dest: Path) -> Path:
    """Simulate downloading a file from the sim service."""
    # TODO: Implement actual download from sim service or mock
    dest.write_text(f"Simulated content for {filename}")
    return dest
