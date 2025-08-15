"""
Unit tests for Report domain model.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from unittest.mock import MagicMock

from src.domain.models.report import Report, ReportStatus, ReportType
from src.domain.models.user import User
from src.domain.models.email_record import EmailRecord


class TestReport:
    """Test Report domain model"""
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(email="user@example.com", username="testuser")
    
    @pytest.fixture
    def sample_email_records(self):
        """Sample email records for testing"""
        email1 = MagicMock(spec=EmailRecord)
        email1.id = UUID("12345678-1234-5678-9012-123456789012")
        email1.subject = "Test Email 1"
        
        email2 = MagicMock(spec=EmailRecord)
        email2.id = UUID("87654321-4321-8765-2109-876543210987")
        email2.subject = "Test Email 2"
        
        return [email1, email2]
    
    @pytest.fixture
    def sample_report_data(self, sample_user, sample_email_records):
        """Sample report data for testing"""
        return {
            "title": "Monthly Email Report",
            "description": "Report for January 2025",
            "report_type": ReportType.MONTHLY,
            "created_by": sample_user,
            "email_records": sample_email_records,
            "status": ReportStatus.PENDING
        }
    
    def test_report_creation_with_required_fields(self, sample_user):
        """Test Report creation with only required fields"""
        report = Report(
            title="Test Report",
            created_by=sample_user
        )
        
        assert report.title == "Test Report"
        assert report.created_by == sample_user
        assert report.description == ""
        assert report.report_type == ReportType.CUSTOM
        assert report.status == ReportStatus.PENDING
        assert report.email_records == []
        assert isinstance(report.id, UUID)
        assert isinstance(report.created_at, datetime)
        assert report.completed_at is None
        assert report.file_path is None
    
    def test_report_creation_with_all_fields(self, sample_report_data):
        """Test Report creation with all fields"""
        report = Report(**sample_report_data)
        
        assert report.title == sample_report_data["title"]
        assert report.description == sample_report_data["description"]
        assert report.report_type == sample_report_data["report_type"]
        assert report.created_by == sample_report_data["created_by"]
        assert report.email_records == sample_report_data["email_records"]
        assert report.status == sample_report_data["status"]
        assert isinstance(report.id, UUID)
    
    def test_report_id_is_unique(self, sample_report_data):
        """Test that each Report gets a unique ID"""
        report1 = Report(**sample_report_data)
        sample_report_data["title"] = "Different Report"
        report2 = Report(**sample_report_data)
        
        assert report1.id != report2.id
        assert isinstance(report1.id, UUID)
        assert isinstance(report2.id, UUID)
    
    def test_report_validation_empty_title(self, sample_user):
        """Test validation fails for empty title"""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Report(title="", created_by=sample_user)
    
    def test_report_validation_none_created_by(self):
        """Test validation fails for None created_by"""
        with pytest.raises(ValueError, match="Created by user is required"):
            Report(title="Test Report", created_by=None)
    
    def test_report_email_count_property(self, sample_report_data):
        """Test email_count property"""
        report = Report(**sample_report_data)
        assert report.email_count == 2
        
        # Empty report
        empty_report = Report(
            title="Empty Report",
            created_by=sample_report_data["created_by"]
        )
        assert empty_report.email_count == 0
    
    def test_report_is_completed_property(self, sample_report_data):
        """Test is_completed property"""
        # Pending report
        report = Report(**sample_report_data)
        assert report.is_completed is False
        
        # Completed report
        sample_report_data["status"] = ReportStatus.COMPLETED
        completed_report = Report(**sample_report_data)
        assert completed_report.is_completed is True
    
    def test_report_is_failed_property(self, sample_report_data):
        """Test is_failed property"""
        # Pending report
        report = Report(**sample_report_data)
        assert report.is_failed is False
        
        # Failed report
        sample_report_data["status"] = ReportStatus.FAILED
        failed_report = Report(**sample_report_data)
        assert failed_report.is_failed is True
    
    def test_report_add_email_record(self, sample_report_data, sample_email_records):
        """Test adding email record to report"""
        # Start with one email
        sample_report_data["email_records"] = [sample_email_records[0]]
        report = Report(**sample_report_data)
        
        # Add second email
        report.add_email_record(sample_email_records[1])
        
        assert len(report.email_records) == 2
        assert sample_email_records[1] in report.email_records
    
    def test_report_add_email_record_prevents_duplicates(self, sample_report_data):
        """Test adding duplicate email record is prevented"""
        report = Report(**sample_report_data)
        initial_count = len(report.email_records)
        
        # Try to add existing email
        report.add_email_record(sample_report_data["email_records"][0])
        
        assert len(report.email_records) == initial_count
    
    def test_report_remove_email_record(self, sample_report_data):
        """Test removing email record from report"""
        report = Report(**sample_report_data)
        email_to_remove = sample_report_data["email_records"][0]
        
        report.remove_email_record(email_to_remove)
        
        assert len(report.email_records) == 1
        assert email_to_remove not in report.email_records
    
    def test_report_mark_as_completed(self, sample_report_data):
        """Test marking report as completed"""
        report = Report(**sample_report_data)
        file_path = "/path/to/report.pdf"
        
        report.mark_as_completed(file_path)
        
        assert report.status == ReportStatus.COMPLETED
        assert report.file_path == file_path
        assert report.completed_at is not None
        assert isinstance(report.completed_at, datetime)
    
    def test_report_mark_as_failed(self, sample_report_data):
        """Test marking report as failed"""
        report = Report(**sample_report_data)
        
        report.mark_as_failed()
        
        assert report.status == ReportStatus.FAILED
        assert report.completed_at is not None
        assert isinstance(report.completed_at, datetime)
    
    def test_report_start_processing(self, sample_report_data):
        """Test starting report processing"""
        report = Report(**sample_report_data)
        
        report.start_processing()
        
        assert report.status == ReportStatus.PROCESSING
    
    def test_report_to_dict(self, sample_report_data):
        """Test Report serialization to dictionary"""
        report = Report(**sample_report_data)
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert report_dict["title"] == sample_report_data["title"]
        assert report_dict["description"] == sample_report_data["description"]
        assert report_dict["report_type"] == sample_report_data["report_type"].value
        assert report_dict["status"] == sample_report_data["status"].value
        assert report_dict["created_by_id"] == str(sample_report_data["created_by"].id)
        assert "id" in report_dict
        assert "created_at" in report_dict
        assert len(report_dict["email_record_ids"]) == 2
    
    def test_report_from_dict_basic(self, sample_user):
        """Test Report deserialization from dictionary (basic version)"""
        report = Report(title="Test Report", created_by=sample_user)
        report_dict = report.to_dict()
        
        # For from_dict, we need to provide the user object
        recreated_report = Report.from_dict(report_dict, sample_user)
        
        assert recreated_report.id == report.id
        assert recreated_report.title == report.title
        assert recreated_report.description == report.description
        assert recreated_report.report_type == report.report_type
        assert recreated_report.status == report.status
        assert recreated_report.created_by == sample_user
    
    def test_report_repr(self, sample_report_data):
        """Test Report string representation"""
        report = Report(**sample_report_data)
        repr_str = repr(report)
        
        assert "Report" in repr_str
        assert sample_report_data["title"] in repr_str
        assert str(report.id) in repr_str
    
    def test_report_equality(self, sample_report_data):
        """Test Report equality comparison"""
        report1 = Report(**sample_report_data)
        sample_report_data["title"] = "Different Report"
        report2 = Report(**sample_report_data)
        
        # Different instances should not be equal (different IDs)
        assert report1 != report2
        
        # Same instance should be equal to itself
        assert report1 == report1
        
        # Reports with same ID should be equal
        report2.id = report1.id
        assert report1 == report2


class TestReportType:
    """Test ReportType enum"""
    
    def test_report_type_values(self):
        """Test ReportType enum values"""
        assert ReportType.DAILY.value == "daily"
        assert ReportType.WEEKLY.value == "weekly"
        assert ReportType.MONTHLY.value == "monthly"
        assert ReportType.QUARTERLY.value == "quarterly"
        assert ReportType.YEARLY.value == "yearly"
        assert ReportType.CUSTOM.value == "custom"
    
    def test_report_type_string_conversion(self):
        """Test ReportType string conversion"""
        assert str(ReportType.MONTHLY) == "ReportType.MONTHLY"
        assert ReportType.MONTHLY.value == "monthly"


class TestReportStatus:
    """Test ReportStatus enum"""
    
    def test_report_status_values(self):
        """Test ReportStatus enum values"""
        assert ReportStatus.PENDING.value == "pending"
        assert ReportStatus.PROCESSING.value == "processing"
        assert ReportStatus.COMPLETED.value == "completed"
        assert ReportStatus.FAILED.value == "failed"
    
    def test_report_status_string_conversion(self):
        """Test ReportStatus string conversion"""
        assert str(ReportStatus.COMPLETED) == "ReportStatus.COMPLETED"
        assert ReportStatus.COMPLETED.value == "completed"
