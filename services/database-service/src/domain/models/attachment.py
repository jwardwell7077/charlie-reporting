"""Attachment domain model.
Represents email attachments with file metadata.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Attachment(BaseModel):
    """Domain model for email attachments."""

    filename: str
    content_type: str
    size_bytes: int
    file_path: str | None = None
    content_id: str | None = None  # For inline attachments
    is_inline: bool = False
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # Allow arbitrary types for UUID
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v:
            raise ValueError("Filename cannot be empty")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        if not v:
            raise ValueError("Content type cannot be empty")
        return v

    @field_validator("size_bytes")
    @classmethod
    def validate_size_bytes(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Size cannot be negative")
        return v

    @property
    def size_mb(self) -> float:
        """Get attachment size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return self.content_type.startswith("image/")

    @property
    def is_document(self) -> bool:
        """Check if attachment is a document."""
        document_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument",
            "text/plain",
        ]
        return any(
            self.content_type.startswith(doc_type)
            for doc_type in document_types
        )

    def to_dict(self) -> dict:
        """Convert attachment to dictionary."""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "file_path": self.file_path,
            "content_id": self.content_id,
            "is_inline": self.is_inline,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attachment":
        """Create attachment from dictionary."""
        attachment_data = data.copy()
        attachment_data["id"] = UUID(attachment_data["id"])
        attachment_data["created_at"] = datetime.fromisoformat(
            attachment_data["created_at"]
        )
        return cls(**attachment_data)

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return (
            "Attachment(id="
            f"{self.id}, filename='{self.filename}', size={self.size_bytes} "
            "bytes)"
        )
