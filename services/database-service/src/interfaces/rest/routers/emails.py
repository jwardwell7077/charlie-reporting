"""Minimal emails router (POST create, GET by id) for TDD bring-up.

Legacy corrupted implementation replaced. Additional endpoints will be
reintroduced incrementally via tests.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ....business.services.email_service import EmailService
from ....domain.models.email_record import EmailRecord, EmailStatus

router = APIRouter()


class EmailCreate(BaseModel):
    message_id: str
    subject: str
    sender: str
    recipients: list[str]
    sent_date: datetime
    body_text: str | None = ""  # test payload uses body_text


class EmailResponse(BaseModel):
    id: UUID
    message_id: str
    subject: str
    sender: str
    recipients: list[str]
    sent_date: datetime
    status: EmailStatus

    @classmethod
    def from_domain(cls, rec: EmailRecord) -> EmailResponse:
        return cls(
            id=rec.id,
            message_id=rec.message_id,
            subject=rec.subject,
            sender=rec.sender,
            recipients=rec.recipients,
            sent_date=rec.sent_date,
            status=rec.status,
        )


def get_email_service(
    request: Request,
) -> EmailService:  # type: ignore[override]
    svc = request.app.state.email_service
    if svc is None:  # pragma: no cover - safety
        raise RuntimeError("EmailService not initialized")
    return svc


@router.post("/", response_model=EmailResponse, status_code=201)
async def create_email(
    payload: EmailCreate,
    email_service: EmailService = Depends(get_email_service),
) -> EmailResponse:
    try:
        saved = await email_service.import_email(payload.model_dump())
    except ValueError as exc:
        # Duplicate message_id or other validation handled as 409
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return EmailResponse.from_domain(saved)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: UUID,
    email_service: EmailService = Depends(get_email_service),
) -> EmailResponse:
    rec = await email_service.get_email_by_id(email_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Email not found")
    return EmailResponse.from_domain(rec)


@router.get("/", response_model=list[EmailResponse])
async def list_emails(
    email_service: EmailService = Depends(get_email_service),
):
    records = await email_service.list_emails()
    return [EmailResponse.from_domain(r) for r in records]

