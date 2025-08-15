#!/usr/bin/env python3
"""Test script to understand SQLAlchemy ORM attribute access.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Add the services directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'database-service', 'src'))

def test_orm_attribute_access():
    """Test how SQLAlchemy ORM attribute access works"""
    try:
        from infrastructure.persistence.models.email_models import EmailRecordORM
        
        print("Successfully imported EmailRecordORM")
        
        # Create an instance 
        orm_instance = EmailRecordORM(
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
            priority="normal",
            status="received",
            created_at=datetime.now()
        )
        
        print(f"Instance subject type: {type(orm_instance.subject)}")
        print(f"Instance subject value: {orm_instance.subject}")
        
        print(f"Class subject type: {type(EmailRecordORM.subject)}")
        print(f"Class subject value: {EmailRecordORM.subject}")
        
        print("\nORM instance attributes work correctly when accessed on instances!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_orm_attribute_access()
    sys.exit(0 if success else 1)
