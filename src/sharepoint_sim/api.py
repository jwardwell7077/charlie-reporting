"""FastAPI router for SharePoint CSV simulator."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from typing import Optional, List, Dict

from sharepoint_sim.service import SharePointCSVGenerator

router = APIRouter(prefix="/sim", tags=["sim"])
_service = SharePointCSVGenerator()


@router.post("/generate")
async def generate(types: str, rows: Optional[int] = None) -> Dict[str, List[Dict[str, int | str]]]:
    datasets = [t.strip() for t in types.split(",") if t.strip()]
    files: List[Dict[str, int | str]] = []
    for d in datasets:
        try:
            path = _service.generate(d, rows)
        except ValueError as e:  # unknown dataset
            raise HTTPException(status_code=400, detail=str(e)) from e
        files.append({"filename": path.name, "size": path.stat().st_size})
    return {"files": files}


@router.get("/files")
async def files() -> Dict[str, List[Dict[str, int | str]]]:  # list
    return {"files": _service.list_files()}


@router.get("/download/{filename}")
async def download(filename: str) -> Response:
    for f in _service.storage.list_files():
        if f.name == filename:
            return Response(f.path.read_text(), media_type="text/csv")
    raise HTTPException(status_code=404, detail="File not found")


@router.post("/reset", status_code=204)
async def reset() -> Response:
    _service.reset()
    return Response(status_code=204)

__all__ = ["router"]
