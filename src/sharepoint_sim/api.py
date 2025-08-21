"""FastAPI router for SharePoint CSV simulator.

Added endpoints:
- ``GET /sim/datasets``: List dataset metadata (name, headers, allowed roles).
- ``GET /sim/datasets/{name}``: Schema & role info for one dataset.
- ``POST /sim/generate/all``: Generate all datasets in one call.
- ``GET /sim/spec``: Return spec addendum markdown (if present) for client introspection.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pathlib import Path
from sharepoint_sim.schemas import ROLE_RULES
from sharepoint_sim.service import GENERATOR_MAP

from sharepoint_sim.service import SharePointCSVGenerator

router = APIRouter(prefix="/sim", tags=["sim"])
_service = SharePointCSVGenerator()


@router.post("/generate")
async def generate(types: str, rows: int | None = None) -> dict[str, list[dict[str, int | str]]]:
    """Generate one or more datasets by name.

    Args:
        types (str): Comma-separated dataset names (e.g., "ACQ,Productivity").
        rows (int, optional): Row count override for all datasets. Defaults to None.

    Returns:
        dict: Metadata for created files. Example::
            {
                "files": [
                    {"filename": "ACQ__2025-08-18_0200.csv", "size": 1234},
                    ...
                ]
            }

    Raises:
        HTTPException: If any dataset name is unknown (400).
    """
    datasets = [t.strip() for t in types.split(",") if t.strip()]
    files: list[dict[str, int | str]] = []
    for d in datasets:
        try:
            path = _service.generate(d, rows)
        except ValueError as e:  # unknown dataset
            raise HTTPException(status_code=400, detail=str(e)) from e
        files.append({"filename": path.name, "size": path.stat().st_size})
    return {"files": files}


@router.post("/generate/all")
async def generate_all(rows: int | None = None) -> dict[str, list[dict[str, int | str]]]:
    """Generate all known datasets in a single call.

    Args:
        rows (int, optional): Row count override for all datasets. Defaults to None.

    Returns:
        dict: Metadata for created files. Example::
            {
                "files": [
                    {"filename": "ACQ__2025-08-18_0200.csv", "size": 1234},
                    ...
                ]
            }
    """
    names = list(GENERATOR_MAP.keys())
    files: list[dict[str, int | str]] = []
    for d in names:
        path = _service.generate(d, rows)
        files.append({"filename": path.name, "size": path.stat().st_size})
    return {"files": files}


@router.get("/files")
async def files() -> dict[str, list[dict[str, int | str]]]:
    """List all generated simulator CSV files.

    Returns:
        dict: List of file metadata (filename, size). Example::
            {
                "files": [
                    {"filename": "ACQ__2025-08-18_0200.csv", "size": 1234},
                    ...
                ]
            }
    """
    return {"files": _service.list_files()}


@router.get("/datasets")
async def list_datasets() -> dict[str, list[dict[str, object]]]:
    """Return metadata for each dataset.

    Returns:
        dict: List of dataset descriptors with keys: name, headers, roles. Example::
            {
                "datasets": [
                    {"name": "ACQ", "headers": [...], "roles": [...]},
                    ...
                ]
            }
    """
    out: list[dict[str, object]] = []
    for name, cls in GENERATOR_MAP.items():
        out.append({
            "name": name,
            "headers": list(cls.headers),  # type: ignore[attr-defined]
            "roles": sorted(list(ROLE_RULES.get(name, set()))),
        })
    return {"datasets": out}


@router.get("/datasets/{name}")
async def get_dataset(name: str) -> dict[str, object]:
    """Return schema information for a single dataset.

    Args:
        name (str): Dataset name (e.g., "ACQ").

    Returns:
        dict: Dataset descriptor with keys: name, headers, roles.

    Raises:
        HTTPException: If dataset is unknown (404).
    """
    cls = GENERATOR_MAP.get(name)
    if cls is None:
        raise HTTPException(status_code=404, detail="Unknown dataset")
    return {
        "name": name,
        "headers": list(cls.headers),  # type: ignore[attr-defined]
        "roles": sorted(list(ROLE_RULES.get(name, set()))),
    }


@router.get("/spec", response_class=PlainTextResponse)
async def spec_addendum() -> str:
    """Return the simulator spec addendum markdown (or placeholder).

    Returns:
        str: Markdown content of the spec addendum, or a not found message.
    """
    path = Path("docs/sharepoint_sim_spec_addendum.md")
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return "Spec addendum not found."


@router.get("/download/{filename}")
async def download(filename: str) -> Response:
    """Download a generated CSV file by filename.

    Args:
        filename (str): Name of the file to download.

    Returns:
        Response: CSV file contents with text/csv media type.

    Raises:
        HTTPException: If file is not found (404).
    """
    for f in _service.storage.list_files():
        if f.name == filename:
            return Response(f.path.read_text(), media_type="text/csv")
    raise HTTPException(status_code=404, detail="File not found")


@router.post("/reset", status_code=204)
async def reset() -> Response:
    """Delete all generated simulator files and reset state.

    Returns:
        Response: Empty response with status 204.
    """
    _service.reset()
    return Response(status_code=204)

__all__ = ["router"]
