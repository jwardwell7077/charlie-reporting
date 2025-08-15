"""Report domain model.
Represents generated reports containing email data (legacy Pydantic style).
"""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from .email_record import EmailRecord
from .user import User


class ReportType(Enum):
    """Report type categories."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportStatus(Enum):
    """Report processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(BaseModel):
    """Domain model for generated reports (Pydantic v1 variant)."""

    title: str
    created_by: User

    description: str = ""
    report_type: ReportType = ReportType.CUSTOM
    status: ReportStatus = ReportStatus.PENDING
    email_records: list[EmailRecord] = Field(default_factory=list)
    file_path: str | None = None
    completed_at: datetime | None = None
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    class Config:  # type: ignore
        arbitrary_types_allowed = True
        use_enum_values = True

    @validator("title")
    def validate_title(cls, v: str) -> str:  # noqa: D401
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @validator("created_by")
    def validate_created_by(cls, v: User) -> User:  # noqa: D401
        if v is None:
            raise ValueError("Created by user is required")
        return v

    @property
    def email_count(self) -> int:
        return len(self.email_records)

    @property
    def is_completed(self) -> bool:
        return self.status == ReportStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == ReportStatus.FAILED

    def add_email_record(self, email_record: EmailRecord) -> None:
        if email_record not in self.email_records:
            self.email_records.append(email_record)

    def remove_email_record(self, email_record: EmailRecord) -> None:
        if email_record in self.email_records:
            self.email_records.remove(email_record)

    def start_processing(self) -> None:
        self.status = ReportStatus.PROCESSING

    def mark_as_completed(self, file_path: str) -> None:
        self.status = ReportStatus.COMPLETED
        self.file_path = file_path
        self.completed_at = datetime.now(UTC)

    def mark_as_failed(self) -> None:
        self.status = ReportStatus.FAILED
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "report_type": self.report_type.value,
            "status": self.status.value,
            "created_by_id": str(self.created_by.id),
            "email_record_ids": [
                str(email.id) for email in self.email_records
            ],
            "file_path": self.file_path,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        created_by_user: User,
        email_records: list[EmailRecord] | None = None,
    ) -> "Report":
        report_data = data.copy()
        report_data["id"] = UUID(report_data["id"])
        report_data["created_at"] = datetime.fromisoformat(
            report_data["created_at"]
        )
        if report_data.get("completed_at"):
            report_data["completed_at"] = datetime.fromisoformat(
                report_data["completed_at"]
            )
        report_data["report_type"] = ReportType(report_data["report_type"])
        report_data["status"] = ReportStatus(report_data["status"])
        report_data["created_by"] = created_by_user
        report_data["email_records"] = email_records or []
        report_data.pop("created_by_id", None)
        report_data.pop("email_record_ids", None)
        return cls(**report_data)

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return isinstance(other, Report) and self.id == other.id

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "Report(id="
            f"{self.id}, title='{self.title}', status={self.status})"
        )
