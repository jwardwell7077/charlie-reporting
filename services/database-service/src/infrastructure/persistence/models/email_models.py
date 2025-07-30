"""
SQLAlchemy EmailRecord ORM Model.
Database representation of email records.
"""

from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class EmailRecordORM(Base, TimestampMixin):
    """SQLAlchemy ORM model for email records"""
    
    __tablename__ = "email_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(String(500), unique=True, nullable=False, index=True)
    subject = Column(String(1000), nullable=False)
    sender = Column(String(255), nullable=False, index=True)
    recipients = Column(JSON, nullable=False)  # Store as JSON array
    cc_recipients = Column(JSON, default=list)
    bcc_recipients = Column(JSON, default=list)
    body_text = Column(Text, default="")
    body_html = Column(Text, default="")
    sent_date = Column(DateTime(timezone=True), nullable=False, index=True)
    received_date = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(String(20), default="normal", index=True)
    status = Column(String(20), default="received", index=True)
    
    def __repr__(self):
        return (f"<EmailRecordORM(id={self.id}, "
                f"message_id='{self.message_id}', "
                f"subject='{self.subject}')>")


class AttachmentORM(Base, TimestampMixin):
    """SQLAlchemy ORM model for attachments"""
    
    __tablename__ = "attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(255), nullable=False)
    size_bytes = Column(String(20), nullable=False)  # Use String to avoid int overflow
    file_path = Column(String(1000), nullable=True)
    content_id = Column(String(255), nullable=True)
    is_inline = Column(String(10), default="false")  # Store as string
    email_record_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    def __repr__(self):
        return (f"<AttachmentORM(id={self.id}, "
                f"filename='{self.filename}', "
                f"size_bytes={self.size_bytes})>")


class UserORM(Base, TimestampMixin):
    """SQLAlchemy ORM model for users"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100), default="")
    last_name = Column(String(100), default="")
    role = Column(String(20), default="user", index=True)
    status = Column(String(20), default="active", index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return (f"<UserORM(id={self.id}, "
                f"username='{self.username}', "
                f"email='{self.email}')>")


class ReportORM(Base, TimestampMixin):
    """SQLAlchemy ORM model for reports"""
    
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    report_type = Column(String(20), default="custom", index=True)
    status = Column(String(20), default="pending", index=True)
    created_by_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    email_record_ids = Column(JSON, default=list)  # Store as JSON array
    file_path = Column(String(1000), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return (f"<ReportORM(id={self.id}, "
                f"title='{self.title}', "
                f"status='{self.status}')>")
