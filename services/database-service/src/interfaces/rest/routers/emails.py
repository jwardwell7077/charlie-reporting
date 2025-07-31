"""
Email management endpoints for the database service API.
Provides CRUD operations for email records.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field

from ....domain.models.email_record import EmailRecord, EmailStatus, EmailPriority
from ....business.services.email_service import EmailService

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from typing import List
router = APIRouter()


# Request/Response Models
class EmailCreateRequest(BaseModel):
        """Request model for creating a new email record"""
    message_id: str = Field(..., description="Unique message identifier")
        subject: str = Field(..., description="Email subject")
        sender: str = Field(..., description="Sender email address")
        recipients: List[str] = Field(..., description="List of recipient email addresses")
        sent_date: datetime = Field(..., description="Date when email was sent")
        body: Optional[str] = Field(None, description="Email body content")
        priority: EmailPriority = Field(
        EmailPriority.NORMAL,
        description="Email priority level"
    )


class EmailUpdateRequest(BaseModel):
        """Request model for updating an email record"""
    subject: Optional[str] = Field(None, description="Email subject")
        status: Optional[EmailStatus] = Field(None, description="Email status")
        priority: Optional[EmailPriority] = Field(None, description="Email priority")
        body: Optional[str] = Field(None, description="Email body content")


class EmailResponse(BaseModel):
        """Response model for email record"""
    id: UUID
    message_id: str
    subject: str
    sender: str
    recipients: List[str]
    sent_date: datetime
    created_at: datetime
    status: EmailStatus
    priority: EmailPriority
    body: Optional[str] = None
    attachment_count: int = 0
    is_high_priority: bool = False

    @classmethod

    def from_domain(cls, email: EmailRecord) -> 'EmailResponse':
            """Convert domain model to response model"""
        return cls(
            id=email.id,
            message_id=email.message_id,
            subject=email.subject,
            sender=email.sender,
            recipients=email.recipients,
            sent_date=email.sent_date,
            created_at=email.created_at,
            status=email.status,
            priority=email.priority,
            body=email.body,
            attachment_count=email.attachment_count,
            is_high_priority=email.is_high_priority
        )


class EmailListResponse(BaseModel):
        """Response model for email list operations"""
    emails: List[EmailResponse]
    total: int
    page: int
    page_size: int


# Dependency injection
async def get_email_service(request: Request) -> EmailService:
        """Dependency to get email service from app state"""
    return request.app.state.email_service


# Endpoints
@router.post("/", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)


async def create_email(
        email_data: EmailCreateRequest,
    email_service: EmailService = Depends(get_email_service)
) -> EmailResponse:
        """
    Create a new email record.
    """
    try:
        # Convert request to domain model
        email_record = EmailRecord(
            message_id=email_data.message_id,
            subject=email_data.subject,
            sender=email_data.sender,
            recipients=email_data.recipients,
            sent_date=email_data.sent_date,
            body=email_data.body,
            priority=email_data.priority
        )

            # Create via service
        created_email = await email_service.import_email(email_record)

            return EmailResponse.from_domain(created_email)

        except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
            )
        except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email record"
        )


@router.get("/", response_model=EmailListResponse)

async def list_emails(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=100, description="Items per page"),
        status_filter: Optional[EmailStatus] = Query(None, description="Filter by status"),
        sender_filter: Optional[str] = Query(None, description="Filter by sender"),
        email_service: EmailService = Depends(get_email_service)
) -> EmailListResponse:
        """
    Get a paginated list of email records with optional filtering.
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size

            # Get emails (simplified - in production you'd implement proper pagination)
            if status_filter:
            emails = await email_service.get_emails_by_status(status_filter)
            elif sender_filter:
            emails = await email_service.get_emails_by_sender(sender_filter)
            else:
            emails = await email_service.get_all_emails()

            # Apply pagination (simplified)
            paginated_emails = emails[offset:offset + page_size]

        return EmailListResponse(
            emails=[EmailResponse.from_domain(email) for email in paginated_emails],
                total=len(emails),
                page=page,
            page_size=page_size
        )

        except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emails"
        )


@router.get("/{email_id}", response_model=EmailResponse)

async def get_email(
        email_id: UUID,
    email_service: EmailService = Depends(get_email_service)
) -> EmailResponse:
        """
    Get a specific email record by ID.
    """
    try:
        email = await email_service.get_email_by_id(email_id)
            if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

            return EmailResponse.from_domain(email)

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email"
        )


@router.put("/{email_id}", response_model=EmailResponse)

async def update_email(
        email_id: UUID,
    email_data: EmailUpdateRequest,
    email_service: EmailService = Depends(get_email_service)
) -> EmailResponse:
        """
    Update an existing email record.
    """
    try:
        # Get existing email
        existing_email = await email_service.get_email_by_id(email_id)
            if not existing_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

            # Update fields that were provided
        update_data = email_data.dict(exclude_unset=True)

            # Apply updates to domain model
        for field, value in update_data.items():
                setattr(existing_email, field, value)

            # Process update via service
        updated_email = await email_service.process_email(existing_email)

            return EmailResponse.from_domain(updated_email)

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email"
        )


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)

async def delete_email(
        email_id: UUID,
    email_service: EmailService = Depends(get_email_service)
):
        """
    Delete an email record.
    """
    try:
        success = await email_service.delete_email(email_id)
            if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

        except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email"
        )


@router.get("/statistics/overview")

async def get_email_statistics(
        email_service: EmailService = Depends(get_email_service)
) -> dict:
        """
    Get email processing statistics and overview.
    """
    try:
        stats = await email_service.get_email_statistics()
            return stats

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email statistics"
        )
