"""
Report management endpoints for the database service API.
Provides CRUD operations for report records.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field

from ....domain.models.report import Report, ReportType, ReportStatus
from ....business.services.report_service import ReportService

from uuid import UUID
from typing import Optional
from typing import List
router = APIRouter()


# Request/Response Models


class ReportCreateRequest(BaseModel):
    """Request model for creating a new report"""
    title: str = Field(..., description="Report title")
        description: Optional[str] = (
            Field(None, description="Report description")
        )
        report_type: ReportType = (
            Field(ReportType.CUSTOM, description="Report type")
        )


class ReportResponse(BaseModel):
    """Response model for report"""
    id: UUID
    title: str
    description: str
    report_type: ReportType
    status: ReportStatus
    email_count: int
    is_completed: bool
    is_failed: bool
    created_at: str
    completed_at: Optional[str] = None
    file_path: Optional[str] = None

    @classmethod
    def from_domain(cls, report: Report) -> 'ReportResponse':
        """Convert domain model to response model"""
        return cls(
            id=report.id,
            title=report.title,
            description=report.description,
            report_type=report.report_type,
            status=report.status,
            email_count=report.email_count,
            is_completed=report.is_completed,
            is_failed=report.is_failed,
            created_at=report.created_at.isoformat(),
        completed_at=report.completed_at.isoformat() if report.completed_at else None,
        file_path=report.file_path
        )


# Dependency injection


    async def get_report_service(request: Request) -> ReportService:
        """Dependency to get report service from app state"""
        return request.app.state.report_service


# Endpoints
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)


async def create_report(
        report_data: ReportCreateRequest,
    report_service: ReportService = Depends(get_report_service)
) -> ReportResponse:
        """Create a new report"""
    try:
        # Placeholder implementation - would need user context
        created_report = await report_service.create_report(
            title=report_data.title,
            description=report_data.description or "",
            report_type=report_data.report_type,
            created_by_user_id="placeholder"  # TODO: Get from auth context
        )

            return ReportResponse.from_domain(created_report)

        except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
            )


@router.get("/", response_model=List[ReportResponse])


async def list_reports(
        status_filter: Optional[ReportStatus] = (
            Query(None, description="Filter by status"),
        )
        type_filter: Optional[ReportType] = (
            Query(None, description="Filter by type"),
        )
        report_service: ReportService = Depends(get_report_service)
) -> List[ReportResponse]:
        """Get list of reports with optional filtering"""
    try:
        # Placeholder implementation
        reports = await report_service.get_all_reports()
            return [ReportResponse.from_domain(report) for report in reports]

        except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reports"
        )


@router.get("/{report_id}", response_model=ReportResponse)


async def get_report(
        report_id: UUID,
    report_service: ReportService = Depends(get_report_service)
) -> ReportResponse:
        """Get a specific report by ID"""
    try:
        report = await report_service.get_report_by_id(report_id)
            if not report:
            raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report not found"
            )

            return ReportResponse.from_domain(report)

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve report"
        )


@router.post("/{report_id}/generate")


async def generate_report(
        report_id: UUID,
    report_service: ReportService = Depends(get_report_service)
) -> dict:
        """Trigger report generation"""
    try:
        result = await report_service.generate_report(report_id)
            return {"message": "Report generation started", "result": result}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)


async def delete_report(
        report_id: UUID,
    report_service: ReportService = Depends(get_report_service)
):
        """Delete a report"""
    try:
        success = await report_service.delete_report(report_id)
            if not success:
            raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report not found"
            )

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )
