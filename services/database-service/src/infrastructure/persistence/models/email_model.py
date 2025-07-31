"""
SQLAlchemy ORM model for EmailRecord.
Maps domain EmailRecord to database table.
"""

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON
import enum

from .base import Base, TimestampMixin, UUIDMixin


from uuid import UUID
# SQLAlchemy enums for database storage
class EmailStatusEnum(enum.Enum):
        RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class EmailPriorityEnum(enum.Enum):
        LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailRecordModel(Base, UUIDMixin, TimestampMixin):
        """SQLAlchemy model for email records"""

    __tablename__ = "email_records"

    # Core email fields
    message_id = Column(String(255), unique=True, nullable=False, index=True)
        subject = Column(String(998), nullable=False)  # RFC 2822 max subject length
        sender = (
        Column(String(320), nullable=False, index=True)  # RFC 5321 max email length
    )

        # Recipients stored as JSON array
    recipients = Column(JSON, nullable=False)
        cc_recipients = Column(JSON, nullable=True, default=list)
        bcc_recipients = Column(JSON, nullable=True, default=list)

        # Email content
    body_text = Column(Text, nullable=True)
        body_html = Column(Text, nullable=True)

        # Dates
    sent_date = Column(DateTime(timezone=True), nullable=False, index=True)
        received_date = Column(DateTime(timezone=True), nullable=False, index=True)

        # Status and priority
    status = Column(
        SQLEnum(EmailStatusEnum, name="email_status"),
            nullable=False,
        default=EmailStatusEnum.RECEIVED,
        index=True
    )
        priority = Column(
        SQLEnum(EmailPriorityEnum, name="email_priority"),
            nullable=False,
        default=EmailPriorityEnum.NORMAL,
        index=True
    )

        def __repr__(self):
            return f"<EmailRecordModel(id={self.id}, message_id='{self.message_id}', subject='{self.subject[:50]}...')>"
