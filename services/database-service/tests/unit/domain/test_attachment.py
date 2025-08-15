"""
Unit tests for Attachment domain model.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from src.domain.models.attachment import Attachment


class TestAttachment:
    """Test Attachment domain model"""
    
    @pytest.fixture
    def sample_attachment_data(self):
        """Sample attachment data for testing"""
        return {
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024000,  # 1MB
            "file_path": "/path/to/file/document.pdf",
            "content_id": "attachment123",
            "is_inline": False
        }
    
    def test_attachment_creation_with_required_fields(self):
        """Test Attachment creation with only required fields"""
        attachment = Attachment(
            filename="test.txt",
            content_type="text/plain",
            size_bytes=500
        )
        
        assert attachment.filename == "test.txt"
        assert attachment.content_type == "text/plain"
        assert attachment.size_bytes == 500
        assert attachment.file_path is None
        assert attachment.content_id is None
        assert attachment.is_inline is False
        assert isinstance(attachment.id, UUID)
        assert isinstance(attachment.created_at, datetime)
    
    def test_attachment_creation_with_all_fields(self, sample_attachment_data):
        """Test Attachment creation with all fields"""
        attachment = Attachment(**sample_attachment_data)
        
        assert attachment.filename == sample_attachment_data["filename"]
        assert attachment.content_type == sample_attachment_data["content_type"]
        assert attachment.size_bytes == sample_attachment_data["size_bytes"]
        assert attachment.file_path == sample_attachment_data["file_path"]
        assert attachment.content_id == sample_attachment_data["content_id"]
        assert attachment.is_inline == sample_attachment_data["is_inline"]
        assert isinstance(attachment.id, UUID)
    
    def test_attachment_id_is_unique(self, sample_attachment_data):
        """Test that each Attachment gets a unique ID"""
        attachment1 = Attachment(**sample_attachment_data)
        attachment2 = Attachment(**sample_attachment_data)
        
        assert attachment1.id != attachment2.id
        assert isinstance(attachment1.id, UUID)
        assert isinstance(attachment2.id, UUID)
    
    def test_attachment_validation_empty_filename(self):
        """Test validation fails for empty filename"""
        with pytest.raises(ValueError, match="Filename cannot be empty"):
            Attachment(
                filename="",
                content_type="text/plain",
                size_bytes=100
            )
    
    def test_attachment_validation_empty_content_type(self):
        """Test validation fails for empty content type"""
        with pytest.raises(ValueError, match="Content type cannot be empty"):
            Attachment(
                filename="test.txt",
                content_type="",
                size_bytes=100
            )
    
    def test_attachment_validation_negative_size(self):
        """Test validation fails for negative size"""
        with pytest.raises(ValueError, match="Size cannot be negative"):
            Attachment(
                filename="test.txt",
                content_type="text/plain",
                size_bytes=-100
            )
    
    def test_attachment_size_mb_property(self):
        """Test size_mb property calculation"""
        # 1MB = 1024 * 1024 bytes
        attachment = Attachment(
            filename="test.txt",
            content_type="text/plain",
            size_bytes=1048576  # Exactly 1MB
        )
        
        assert attachment.size_mb == 1.0
        
        # Test with different size
        attachment.size_bytes = 2097152  # 2MB
        assert attachment.size_mb == 2.0
    
    def test_attachment_is_image_property(self):
        """Test is_image property"""
        # Image attachment
        image_attachment = Attachment(
            filename="photo.jpg",
            content_type="image/jpeg",
            size_bytes=500000
        )
        assert image_attachment.is_image is True
        
        # Non-image attachment
        doc_attachment = Attachment(
            filename="document.pdf",
            content_type="application/pdf",
            size_bytes=100000
        )
        assert doc_attachment.is_image is False
    
    def test_attachment_is_document_property(self):
        """Test is_document property"""
        # PDF document
        pdf_attachment = Attachment(
            filename="document.pdf",
            content_type="application/pdf",
            size_bytes=100000
        )
        assert pdf_attachment.is_document is True
        
        # Word document
        word_attachment = Attachment(
            filename="document.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=200000
        )
        assert word_attachment.is_document is True
        
        # Text file
        text_attachment = Attachment(
            filename="readme.txt",
            content_type="text/plain",
            size_bytes=5000
        )
        assert text_attachment.is_document is True
        
        # Non-document (image)
        image_attachment = Attachment(
            filename="photo.jpg",
            content_type="image/jpeg",
            size_bytes=500000
        )
        assert image_attachment.is_document is False
    
    def test_attachment_to_dict(self, sample_attachment_data):
        """Test Attachment serialization to dictionary"""
        attachment = Attachment(**sample_attachment_data)
        attachment_dict = attachment.to_dict()
        
        assert isinstance(attachment_dict, dict)
        assert attachment_dict["filename"] == sample_attachment_data["filename"]
        assert attachment_dict["content_type"] == sample_attachment_data["content_type"]
        assert attachment_dict["size_bytes"] == sample_attachment_data["size_bytes"]
        assert attachment_dict["file_path"] == sample_attachment_data["file_path"]
        assert attachment_dict["content_id"] == sample_attachment_data["content_id"]
        assert attachment_dict["is_inline"] == sample_attachment_data["is_inline"]
        assert "id" in attachment_dict
        assert "created_at" in attachment_dict
    
    def test_attachment_from_dict(self, sample_attachment_data):
        """Test Attachment deserialization from dictionary"""
        attachment = Attachment(**sample_attachment_data)
        attachment_dict = attachment.to_dict()
        
        recreated_attachment = Attachment.from_dict(attachment_dict)
        
        assert recreated_attachment.id == attachment.id
        assert recreated_attachment.filename == attachment.filename
        assert recreated_attachment.content_type == attachment.content_type
        assert recreated_attachment.size_bytes == attachment.size_bytes
        assert recreated_attachment.file_path == attachment.file_path
        assert recreated_attachment.content_id == attachment.content_id
        assert recreated_attachment.is_inline == attachment.is_inline
        assert recreated_attachment.created_at == attachment.created_at
    
    def test_attachment_repr(self, sample_attachment_data):
        """Test Attachment string representation"""
        attachment = Attachment(**sample_attachment_data)
        repr_str = repr(attachment)
        
        assert "Attachment" in repr_str
        assert sample_attachment_data["filename"] in repr_str
        assert str(sample_attachment_data["size_bytes"]) in repr_str
        assert str(attachment.id) in repr_str
