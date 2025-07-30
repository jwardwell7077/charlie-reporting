#!/usr/bin/env python3
"""
Test script to validate Pydantic domain models work correctly.
This script helps verify our domain models are properly configured.
"""

import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'database-service', 'src'))

def test_pydantic_models():
    """Test all Pydantic domain models"""
    try:
        from domain.models.email_record import EmailRecord, EmailStatus, EmailPriority
        from domain.models.attachment import Attachment
        from domain.models.user import User, UserRole, UserStatus
        from domain.models.report import Report, ReportType, ReportStatus
        
        print("✅ Successfully imported all Pydantic domain models")
        
        # Test EmailRecord
        email = EmailRecord(
            id=uuid4(),
            message_id="test@example.com",
            subject="Test Email",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            cc_recipients=[],
            bcc_recipients=[],
            body_text="Test body",
            body_html="<p>Test body</p>",
            sent_date=datetime.now(),
            received_date=datetime.now(),
            priority=EmailPriority.NORMAL,
            status=EmailStatus.RECEIVED,
            attachments=[]
        )
        print(f"✅ Created EmailRecord: {email.subject}")
        
        # Test User
        user = User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            last_login=None,
            created_at=datetime.now()
        )
        print(f"✅ Created User: {user.username}")
        
        # Test Report
        report = Report(
            id=uuid4(),
            title="Test Report",
            description="A test report",
            report_type=ReportType.EMAIL_SUMMARY,
            status=ReportStatus.PENDING,
            created_by=user,
            email_records=[email],
            file_path=None,
            completed_at=None,
            created_at=datetime.now()
        )
        print(f"✅ Created Report: {report.title}")
        
        print("\n🎉 All Pydantic domain models work correctly!")
        return True
🎉 All Pydantic domain models work correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    success = test_pydantic_models()
    sys.exit(0 if success else 1)
