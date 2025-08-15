"""Reports router (placeholder).

The previous merge left this file in a syntactically invalid state with
mis‑indentation and partially duplicated blocks. This clean version
provides a minimal, importable FastAPI router so the codebase compiles
while full report functionality is implemented incrementally.

Current design choices:
  * Endpoints return HTTP 501 Not Implemented (explicit placeholder)
  * Lightweight Pydantic request/response models defined for future use
  * Dependency getter expects an attribute ``report_service`` on
    ``app.state``; if absent, a 503 is raised (clearer than attribute
    errors during early development).

This satisfies the immediate goal of resolving merge conflicts without
introducing unfinished business logic.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

router = APIRouter()


# --- Pydantic models (minimal) -------------------------------------------------

class ReportCreateRequest(BaseModel):
    title: str = Field(..., description="Report title")
    description: str | None = Field(None, description="Optional description")
    report_type: str = Field("custom", description="Report type (enum placeholder)")


class ReportResponse(BaseModel):
    id: UUID
    title: str
    description: str
    report_type: str
    status: str


# --- Dependency -----------------------------------------------------------------

def get_report_service(request: Request):  # pragma: no cover - trivial accessor
    svc = getattr(request.app.state, "report_service", None)
    if svc is None:
        raise HTTPException(status_code=503, detail="ReportService not available")
    return svc


# --- Endpoints (stubs) ---------------------------------------------------------

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(_: ReportCreateRequest):  # pragma: no cover - stub
    raise HTTPException(status_code=501, detail="Report creation not yet implemented")


@router.get("/", response_model=list[ReportResponse])
async def list_reports():  # pragma: no cover - stub
    raise HTTPException(status_code=501, detail="Report listing not yet implemented")


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: UUID):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Retrieving report {report_id} not yet implemented"
    )


@router.post("/{report_id}/generate")
async def generate_report(report_id: UUID):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Generating report {report_id} not yet implemented"
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: UUID):  # pragma: no cover - stub
    raise HTTPException(
        status_code=501, detail=f"Deleting report {report_id} not yet implemented"
    )

