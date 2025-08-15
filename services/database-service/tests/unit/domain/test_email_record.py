"""
Unit tests for EmailRecord domain model.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID

from src.domain.models.email_record import EmailRecord, EmailStatus, EmailPriority
from src.domain.models.attachment import Attachment


class TestEmailRecord:
    """Test EmailRecord domain model"""
    
    @pytest.fixture
    def sample_email_data(self):
        """Sample email data for testing"""
        return {
            "message_id": "test-message-123@example.com",
            "subject": "Test Email Subject",
            "sender": "sender@example.com",
            "recipients": ["recipient1@example.com", "recipient2@example.com"],
            "cc_recipients": ["cc@example.com"],
            "bcc_recipients": ["bcc@example.com"],
            "body_text": "This is the email body content.",
            "body_html": "<p>This is the email body content.</p>",
            "sent_date": datetime(2025, 7, 29, 10, 0, 0, tzinfo=timezone.utc),
            "received_date": datetime(2025, 7, 29, 10, 1, 0, tzinfo=timezone.utc),
            "priority": EmailPriority.NORMAL,
            "status": EmailStatus.RECEIVED
        }
    
    def test_email_record_creation_with_required_fields(self, sample_email_data):
        """Test EmailRecord creation with only required fields"""
        # Remove optional fields
        required_data = {
            "message_id": sample_email_data["message_id"],
            "subject": sample_email_data["subject"],
            "sender": sample_email_data["sender"],
            "recipients": sample_email_data["recipients"],
            "sent_date": sample_email_data["sent_date"]
        }
        
        email = EmailRecord(**required_data)
        
        assert email.message_id == required_data["message_id"]
        assert email.subject == required_data["subject"]
        assert email.sender == required_data["sender"]
        assert email.recipients == required_data["recipients"]
        assert email.sent_date == required_data["sent_date"]
        
        # Check defaults
        assert email.cc_recipients == []
        assert email.bcc_recipients == []
        assert email.body_text == ""
        assert email.body_html == ""
        assert email.priority == EmailPriority.NORMAL
        assert email.status == EmailStatus.RECEIVED
        assert email.received_date is not None
        assert isinstance(email.id, UUID)
        assert email.attachments == []
    
    def test_email_record_creation_with_all_fields(self, sample_email_data):
        """Test EmailRecord creation with all fields"""
        email = EmailRecord(**sample_email_data)
        
        assert email.message_id == sample_email_data["message_id"]
        assert email.subject == sample_email_data["subject"]
        assert email.sender == sample_email_data["sender"]
        assert email.recipients == sample_email_data["recipients"]
        assert email.cc_recipients == sample_email_data["cc_recipients"]
        assert email.bcc_recipients == sample_email_data["bcc_recipients"]
        assert email.body_text == sample_email_data["body_text"]
        assert email.body_html == sample_email_data["body_html"]
        assert email.sent_date == sample_email_data["sent_date"]
        assert email.received_date == sample_email_data["received_date"]
        assert email.priority == sample_email_data["priority"]
        assert email.status == sample_email_data["status"]
        assert isinstance(email.id, UUID)
    
    def test_email_record_id_is_unique(self, sample_email_data):
        """Test that each EmailRecord gets a unique ID"""
        email1 = EmailRecord(**sample_email_data)
        email2 = EmailRecord(**sample_email_data)
        
        assert email1.id != email2.id
        assert isinstance(email1.id, UUID)
        assert isinstance(email2.id, UUID)
    
    def test_email_record_with_attachments(self, sample_email_data):
        """Test EmailRecord with attachments"""
        attachment1 = MagicMock(spec=Attachment)
        attachment1.filename = "document.pdf"
        attachment2 = MagicMock(spec=Attachment)
        attachment2.filename = "image.jpg"
        
        sample_email_data["attachments"] = [attachment1, attachment2]
        email = EmailRecord(**sample_email_data)
        
        assert len(email.attachments) == 2
        assert attachment1 in email.attachments
        assert attachment2 in email.attachments
    
    def test_email_record_add_attachment(self, sample_email_data):
        """Test adding attachment to EmailRecord"""
        email = EmailRecord(**sample_email_data)
        attachment = MagicMock(spec=Attachment)
        attachment.filename = "new_attachment.pdf"
        
        email.add_attachment(attachment)
        
        assert len(email.attachments) == 1
        assert attachment in email.attachments
    
    def test_email_record_remove_attachment(self, sample_email_data):
        """Test removing attachment from EmailRecord"""
        attachment1 = MagicMock(spec=Attachment)
        attachment2 = MagicMock(spec=Attachment)
        sample_email_data["attachments"] = [attachment1, attachment2]
        
        email = EmailRecord(**sample_email_data)
        email.remove_attachment(attachment1)
        
        assert len(email.attachments) == 1
        assert attachment1 not in email.attachments
        assert attachment2 in email.attachments
    
    def test_email_record_has_attachments_property(self, sample_email_data):
        """Test has_attachments property"""
        # Email without attachments
        email_no_attachments = EmailRecord(**sample_email_data)
        assert email_no_attachments.has_attachments is False
        
        # Email with attachments
        attachment = MagicMock(spec=Attachment)
        sample_email_data["attachments"] = [attachment]
        email_with_attachments = EmailRecord(**sample_email_data)
        assert email_with_attachments.has_attachments is True
    
    def test_email_record_attachment_count_property(self, sample_email_data):
        """Test attachment_count property"""
        # Email without attachments
        email = EmailRecord(**sample_email_data)
        assert email.attachment_count == 0
        
        # Add attachments
        attachment1 = MagicMock(spec=Attachment)
        attachment2 = MagicMock(spec=Attachment)
        email.add_attachment(attachment1)
        email.add_attachment(attachment2)
        
        assert email.attachment_count == 2
    
    def test_email_record_is_high_priority_property(self, sample_email_data):
        """Test is_high_priority property"""
        # Normal priority
        sample_email_data["priority"] = EmailPriority.NORMAL
        email_normal = EmailRecord(**sample_email_data)
        assert email_normal.is_high_priority is False
        
        # High priority
        sample_email_data["priority"] = EmailPriority.HIGH
        email_high = EmailRecord(**sample_email_data)
        assert email_high.is_high_priority is True
    
    def test_email_record_mark_as_processed(self, sample_email_data):
        """Test marking email as processed"""
        email = EmailRecord(**sample_email_data)
        initial_status = email.status
        
        email.mark_as_processed()
        
        assert email.status == EmailStatus.PROCESSED
        assert email.status != initial_status
    
    def test_email_record_mark_as_failed(self, sample_email_data):
        """Test marking email as failed"""
        email = EmailRecord(**sample_email_data)
        
        email.mark_as_failed()
        
        assert email.status == EmailStatus.FAILED
    
    def test_email_record_to_dict(self, sample_email_data):
        """Test EmailRecord serialization to dictionary"""
        email = EmailRecord(**sample_email_data)
        email_dict = email.to_dict()
        
        assert isinstance(email_dict, dict)
        assert email_dict["message_id"] == sample_email_data["message_id"]
        assert email_dict["subject"] == sample_email_data["subject"]
        assert email_dict["sender"] == sample_email_data["sender"]
        assert email_dict["recipients"] == sample_email_data["recipients"]
        assert email_dict["priority"] == sample_email_data["priority"].value
        assert email_dict["status"] == sample_email_data["status"].value
        assert "id" in email_dict
    
    def test_email_record_from_dict(self, sample_email_data):
        """Test EmailRecord deserialization from dictionary"""
        email = EmailRecord(**sample_email_data)
        email_dict = email.to_dict()
        
        recreated_email = EmailRecord.from_dict(email_dict)
        
        assert recreated_email.id == email.id
        assert recreated_email.message_id == email.message_id
        assert recreated_email.subject == email.subject
        assert recreated_email.sender == email.sender
        assert recreated_email.priority == email.priority
        assert recreated_email.status == email.status
    
    def test_email_record_repr(self, sample_email_data):
        """Test EmailRecord string representation"""
        email = EmailRecord(**sample_email_data)
        repr_str = repr(email)
        
        assert "EmailRecord" in repr_str
        assert sample_email_data["message_id"] in repr_str
        assert sample_email_data["subject"] in repr_str
    
    def test_email_record_equality(self, sample_email_data):
        """Test EmailRecord equality comparison"""
        email1 = EmailRecord(**sample_email_data)
        email2 = EmailRecord(**sample_email_data)
        
        # Different instances should not be equal (different IDs)
        assert email1 != email2
        
        # Same instance should be equal to itself
        assert email1 == email1
        
        # Emails with same ID should be equal
        email2.id = email1.id
        assert email1 == email2


class TestEmailStatus:
    """Test EmailStatus enum"""
    
    def test_email_status_values(self):
        """Test EmailStatus enum values"""
        assert EmailStatus.RECEIVED.value == "received"
        assert EmailStatus.PROCESSED.value == "processed"
        assert EmailStatus.FAILED.value == "failed"
        assert EmailStatus.ARCHIVED.value == "archived"
    
    def test_email_status_string_conversion(self):
        """Test EmailStatus string conversion"""
        assert str(EmailStatus.RECEIVED) == "EmailStatus.RECEIVED"
        assert EmailStatus.RECEIVED.value == "received"


class TestEmailPriority:
    """Test EmailPriority enum"""
    
    def test_email_priority_values(self):
        """Test EmailPriority enum values"""
        assert EmailPriority.LOW.value == "low"
        assert EmailPriority.NORMAL.value == "normal"
        assert EmailPriority.HIGH.value == "high"
        assert EmailPriority.URGENT.value == "urgent"
    
    def test_email_priority_comparison(self):
        """Test EmailPriority comparison for sorting"""
        # Test that priorities can be compared numerically
        priorities = [EmailPriority.LOW, EmailPriority.NORMAL, EmailPriority.HIGH, EmailPriority.URGENT]
        assert len(set(priority.value for priority in priorities)) == 4
