#!/usr / bin / env python3
"""
Migrate existing code from src/ into appropriate microservice structures
"""

from pathlib import Path
from typing import Dict, Any

# Code migration mapping - where each existing file should go
MIGRATION_MAP = {
    # Email Fetcher -> Outlook Relay Service
    "src / email_fetcher.py": {
        "target_service": "outlook - relay",
        "new_locations": [
            {
                "path": "src / business / services / email_fetcher.py",
                "transform": "extract_business_logic"
            },
            {
                "path": "src / infrastructure / outlook / com_client.py",
                "transform": "extract_outlook_com_integration"
            },
            {
                "path": "src / interfaces / rest / email_controller.py",
                "transform": "create_rest_interface"
            }
        ]
    },

    # Transformer -> Report Generator Service
    "src / transformer.py": {
        "target_service": "report - generator",
        "new_locations": [
            {
                "path": "src / business / services / data_transformer.py",
                "transform": "extract_transformation_logic"
            },
            {
                "path": "src / business / models / data_model.py",
                "transform": "extract_data_models"
            }
        ]
    },

    # Excel Writer -> Report Generator Service
    "src / excel_writer.py": {
        "target_service": "report - generator",
        "new_locations": [
            {
                "path": "src / business / services / report_builder.py",
                "transform": "extract_report_building_logic"
            },
            {
                "path": "src / infrastructure / excel / writer.py",
                "transform": "extract_excel_infrastructure"
            }
        ]
    },

    # Main -> Scheduler Service + Individual Services
    "src / main.py": {
        "target_service": "scheduler - service",
        "new_locations": [
            {
                "path": "src / business / services / orchestrator.py",
                "transform": "extract_orchestration_logic"
            }
        ]
    },

    # Utils -> Split across services
    "src / utils.py": {
        "target_service": "multiple",
        "new_locations": [
            {
                "service": "email - service",
                "path": "src / business / services / email_sender.py",
                "transform": "extract_email_sending_logic"
            },
            {
                "service": "outlook - relay",
                "path": "src / infrastructure / outlook / utilities.py",
                "transform": "extract_outlook_utilities"
            }
        ]
    },

    # Config Loader -> Shared component (already done)
    "src / config_loader.py": {
        "target_service": "shared",
        "status": "already_migrated_to_shared_config"
    }
}


def read_source_file(file_path: str) -> str:
    """Read source file content"""
    try:
        with open(file_path, 'r', encoding='utf - 8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return ""


def extract_business_logic(content: str, original_file: str) -> str:
    """Extract business logic from email_fetcher.py"""

    if "email_fetcher.py" in original_file:
        return '''"""


Email Fetcher Business Service
Pure business logic for email operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path

from ..models.email import Email
from ..models.outlook import OutlookConfiguration


class EmailFetcherService:
    """
    Business service for email fetching operations
    Pure domain logic without infrastructure dependencies
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def should_fetch_email(self, email_data: Dict[str, Any], config: OutlookConfiguration) -> bool:
        """
        Business rule: Determine if an email should be fetched
        """
        # TODO: Extract business rules from original email_fetcher.py
        # Examples:
        # - Check if email is within time range
        # - Validate sender requirements
        # - Check attachment criteria
        return True

    def process_email_batch(self, emails: List[Dict[str, Any]], config: OutlookConfiguration) -> List[Email]:
        """
        Business logic for processing a batch of emails
        """
        processedemails = []

        for email_data in emails:
            if self.should_fetch_email(email_data, config):
                try:
                    email = self.convert_to_domain_email(email_data)
                    processed_emails.append(email)
                    self.logger.debug(f"Processed email: {email.subject}")
                except Exception as e:
                    self.logger.error(f"Failed to process email: {e}")

        return processed_emails

    def convert_to_domain_email(self, email_data: Dict[str, Any]) -> Email:
        """Convert raw email data to domain model"""
        # TODO: Extract conversion logic from original code
        return Email(
            subject=email_data.get('subject', ''),
            sender=email_data.get('sender', ''),
            received_time=email_data.get('received_time'),
            body=email_data.get('body', ''),
            attachments=email_data.get('attachments', [])
        )

# TODO: Move the rest of the business logic from src / email_fetcher.py here  # Keep infrastructure (COM / Graph API calls) separate
'''

    return content


def extract_outlook_com_integration(content: str, original_file: str) -> str:
    """Extract Outlook COM integration infrastructure"""

    return '''"""


Outlook COM Client Infrastructure
Low - level Outlook COM integration
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


class OutlookComClient:
    """
    Infrastructure component for Outlook COM integration
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.outlook = None
        self.namespace = None

        if not COM_AVAILABLE:
            self.logger.warning("COM libraries not available - Outlook integration disabled")

    async def connect(self) -> bool:
        """Establish connection to Outlook"""
        if not COM_AVAILABLE:
            return False

        try:
            # TODO: Extract COM connection logic from original email_fetcher.py
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            self.logger.info("Connected to Outlook via COM")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Outlook: {e}")
            return False

    async def fetch_emails_from_folder(self, folder_name: str, time_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch emails from specific Outlook folder"""
        if not self.outlook:
            raise RuntimeError("Not connected to Outlook")

        # TODO: Extract folder fetching logic from original code
        emails = []

        try:
            folder = self.namespace.GetDefaultFolder(6)  # Inbox
            items = folder.Items

            # TODO: Apply time filtering and other criteria

            for item in items:
                emaildata = self.extract_email_data(item)
                emails.append(email_data)

        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")

        return emails

    def extract_email_data(self, outlook_item) -> Dict[str, Any]:
        """Extract data from Outlook item"""
        # TODO: Extract this logic from original email_fetcher.py
        return {
            'subject': getattr(outlook_item, 'Subject', ''),
            'sender': getattr(outlook_item, 'SenderEmailAddress', ''),
            'received_time': getattr(outlook_item, 'ReceivedTime', None),
            'body': getattr(outlook_item, 'Body', ''),
            'attachments': []  # TODO: Extract attachment handling
        }

    async def disconnect(self):
        """Clean up COM resources"""
        # TODO: Extract cleanup logic
        self.outlook = None
        self.namespace = None

# TODO: Move COM - specific code from src / email_fetcher.py here
'''


def create_rest_interface(content: str, original_file: str) -> str:
    """Create REST interface for email operations"""

    return '''"""


Email Controller - REST Interface
HTTP endpoints for email operations
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...business.services.email_fetcher import EmailFetcherService
from ...business.models.email import Email

router = APIRouter(prefix="/emails", tags=["emails"])


class EmailFetchRequest(BaseModel):
    """Request model for email fetching"""
    folder_name: Optional[str] = "Inbox"
    time_range_hours: Optional[int] = 24
    sender_filter: Optional[str] = None


class EmailResponse(BaseModel):
    """Response model for email data"""
    subject: str
    sender: str
    received_time: datetime
    body: str
    attachment_count: int


@router.post("/fetch", response_model=List[EmailResponse])
async def fetch_emails(request: EmailFetchRequest):
    """
    Fetch emails from Outlook
    """
    try:
        # TODO: Implement using EmailFetcherService
        service = EmailFetcherService()
        emails = []  # service.fetch_emails(request)

        return [
            EmailResponse(
                subject=email.subject,
                sender=email.sender,
                received_time=email.received_time,
                body=email.body,
                attachment_count=len(email.attachments)
            )
            for email in emails
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def email_health():
    """Health check for email service"""
    return {"status": "healthy", "service": "email - fetcher"}

# TODO: Add more endpoints as needed
'''


def extract_transformation_logic(content: str, original_file: str) -> str:
    """Extract data transformation business logic"""

    return '''"""


Data Transformer Business Service
Pure business logic for data transformations
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import pandas as pd

from ..models.data_model import DataRecord, TransformationRule


class DataTransformerService:
    """
    Business service for data transformation operations
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.transformationrules = []

    def transform_email_data_to_records(self, email_data: List[Dict[str, Any]]) -> List[DataRecord]:
        """
        Transform raw email data into structured data records
        """
        records = []

        for email in email_data:
            try:
                record = self.apply_transformation_rules(email)
                records.append(record)
            except Exception as e:
                self.logger.error(f"Failed to transform email data: {e}")

        return records

    def aggregate_records_by_criteria(self, records: List[DataRecord], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate data records based on business criteria
        """
        # TODO: Extract aggregation logic from transformer.py
        aggregated = {
            'total_records': len(records),
            'processed_at': datetime.now(),
            'criteria_applied': criteria
        }

        return aggregated

    def validate_data_quality(self, records: List[DataRecord]) -> Dict[str, Any]:
        """
        Business rules for data quality validation
        """
        qualityreport = {
            'total_records': len(records),
            'valid_records': 0,
            'errors': [],
            'warnings': []
        }

        # TODO: Extract validation rules from transformer.py

        return quality_report

    def apply_transformation_rules(self, data: Dict[str, Any]) -> DataRecord:
        """Apply configured transformation rules to data"""
        # TODO: Extract transformation rules from original code

        return DataRecord(
            source_type='email',
            processed_at=datetime.now(),
            data=data
        )

# TODO: Move business logic from src / transformer.py here  # Keep pandas / Excel operations in infrastructure layer
'''


def extract_report_building_logic(content: str, original_file: str) -> str:
    """Extract report building business logic"""

    return '''"""


Report Builder Business Service
Pure business logic for report generation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.report_template import ReportTemplate
from ..models.data_model import DataRecord


class ReportBuilderService:
    """
    Business service for report building operations
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def create_report_from_data(self, data: List[DataRecord], template: ReportTemplate) -> Dict[str, Any]:
        """
        Create report structure from data using template
        """
        report = {
            'template_name': template.name,
            'generated_at': datetime.now(),
            'data_source': 'email_processing',
            'sections': []
        }

        # TODO: Extract report building logic from excel_writer.py

        for section in template.sections:
            sectiondata = self.build_section(data, section)
            report['sections'].append(section_data)

        return report

    def validate_report_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Business rules for report validation
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # TODO: Extract validation logic

        return validation

    def calculate_report_metrics(self, data: List[DataRecord]) -> Dict[str, Any]:
        """
        Calculate business metrics for the report
        """
        metrics = {
            'total_records': len(data),
            'processing_time': None,  # TODO: Extract from original
            'quality_score': None     # TODO: Extract from original
        }

        return metrics

    def build_section(self, data: List[DataRecord], section_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build individual report section"""
        # TODO: Extract section building logic

        return {
            'name': section_config.get('name', 'Unknown'),
            'data': [],
            'metrics': {}
        }

# TODO: Move business logic from src / excel_writer.py here  # Keep Excel formatting in infrastructure layer
'''


def extract_excel_infrastructure(content: str, original_file: str) -> str:
    """Extract Excel writing infrastructure"""

    return '''"""


Excel Writer Infrastructure
Low - level Excel file operations
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ExcelWriter:
    """
    Infrastructure component for Excel file operations
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

        if not EXCEL_AVAILABLE:
            self.logger.warning("Excel libraries not available")

    async def write_report_to_excel(self, report_data: Dict[str, Any], output_path: Path) -> bool:
        """Write report data to Excel file"""
        if not EXCEL_AVAILABLE:
            self.logger.error("Excel libraries not available")
            return False

        try:
            # TODO: Extract Excel writing logic from excel_writer.py
            workbook = openpyxl.Workbook()
            worksheet = workbook.active

            # TODO: Apply formatting and styling

            workbook.save(output_path)
            self.logger.info(f"Excel report written to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to write Excel report: {e}")
            return False

    def apply_formatting(self, worksheet, template_config: Dict[str, Any]):
        """Apply Excel formatting based on template"""
        # TODO: Extract formatting logic from original code
        pass

    def create_data_sheet(self, worksheet, data: List[Dict[str, Any]], sheet_config: Dict[str, Any]):
        """Create data sheet with proper formatting"""
        # TODO: Extract sheet creation logic
        pass

# TODO: Move Excel - specific code from src / excel_writer.py here
'''


def extract_orchestration_logic(content: str, original_file: str) -> str:
    """Extract orchestration logic from main.py"""

    return '''"""


Orchestration Service
Business logic for coordinating service operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging


class OrchestratorService:
    """
    Business service for orchestrating multi - service operations
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.serviceendpoints = {}

    async def execute_email_processing_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete email processing workflow
        """
        workflowresult = {
            'started_at': datetime.now(),
            'status': 'running',
            'steps': []
        }

        try:
            # Step 1: Fetch emails from Outlook Relay
            email_data = await self.call_outlook_relay(config)
            workflow_result['steps'].append({'step': 'fetch_emails', 'status': 'completed'})

            # Step 2: Store in Database Service
            storage_result = await self.call_database_service(email_data)
            workflow_result['steps'].append({'step': 'store_data', 'status': 'completed'})

            # Step 3: Generate reports via Report Generator
            report_result = await self.call_report_generator(storage_result)
            workflow_result['steps'].append({'step': 'generate_report', 'status': 'completed'})

            # Step 4: Send notifications via Email Service
            notification_result = await self.call_email_service(report_result)
            workflow_result['steps'].append({'step': 'send_notifications', 'status': 'completed'})

            workflow_result['status'] = 'completed'
            workflow_result['completed_at'] = datetime.now()

        except Exception as e:
            workflow_result['status'] = 'failed'
            workflow_result['error'] = str(e)
            self.logger.error(f"Workflow failed: {e}")

        return workflow_result

    async def call_outlook_relay(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Outlook Relay Service"""
        # TODO: Implement HTTP client call
        return {'emails': []}

    async def call_database_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Database Service"""
        # TODO: Implement HTTP client call
        return {'stored_records': len(data.get('emails', []))}

    async def call_report_generator(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Report Generator Service"""
        # TODO: Implement HTTP client call
        return {'report_path': 'reports / generated_report.xlsx'}

    async def call_email_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Email Service"""
        # TODO: Implement HTTP client call
        return {'notifications_sent': 1}

# TODO: Move orchestration logic from src / main.py here
'''


def extract_email_sending_logic(content: str, original_file: str) -> str:
    """Extract email sending logic from utils.py"""

    return '''"""


Email Sender Business Service
Pure business logic for email sending operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.email_template import EmailTemplate
from ..models.recipient import Recipient
from ..models.delivery import DeliveryResult


class EmailSenderService:
    """
    Business service for email sending operations
    """

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def prepare_email_from_template(self, template: EmailTemplate, recipients: List[Recipient], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare email using template and data
        """
        email = {
            'template_id': template.id,
            'recipients': [r.email for r in recipients],
            'subject': self.render_template(template.subject, data),
            'body': self.render_template(template.body, data),
            'prepared_at': datetime.now()
        }

        return email

    def validate_recipients(self, recipients: List[Recipient]) -> Dict[str, Any]:
        """
        Business rules for recipient validation
        """
        validation = {
            'valid_recipients': [],
            'invalid_recipients': [],
            'errors': []
        }

        for recipient in recipients:
            if self.is_valid_email(recipient.email):
                validation['valid_recipients'].append(recipient)
            else:
                validation['invalid_recipients'].append(recipient)
                validation['errors'].append(f"Invalid email: {recipient.email}")

        return validation

    def calculate_delivery_schedule(self, recipients: List[Recipient], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Business logic for email delivery scheduling
        """
        schedule = {
            'total_recipients': len(recipients),
            'batch_size': config.get('batch_size', 10),
            'delay_between_batches': config.get('delay_seconds', 60),
            'estimated_completion': None  # TODO: Calculate
        }

        return schedule

    def render_template(self, template_text: str, data: Dict[str, Any]) -> str:
        """Render template with data"""
        # TODO: Extract template rendering from utils.py
        return template_text.format(**data)

    def is_valid_email(self, email: str) -> bool:
        """Validate email address"""
        # TODO: Extract email validation logic
        return '@' in email and '.' in email.split('@')[1]

# TODO: Move email sending business logic from src / utils.py here
'''


def create_business_models(service_name: str):
    """Create business model files for a service"""

    models = {
        "outlook - relay": {
            "email.py": '''"""Email domain model"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass


class Email:
    subject: str
    sender: str
    received_time: datetime
    body: str
    attachments: List[str]
    id: Optional[str] = None
    folder: Optional[str] = None''',

            "outlook.py": '''"""Outlook configuration model"""
from dataclasses import dataclass
from typing import Optional


@dataclass


class OutlookConfiguration:
    folder_name: str = "Inbox"
    time_range_hours: int = 24
    sender_filter: Optional[str] = None
    attachment_required: bool = False''',

            "attachment.py": '''"""Attachment domain model"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass


class Attachment:
    filename: str
    file_path: Path
    size_bytes: int
    content_type: str
    id: Optional[str] = None'''
        },

        "report - generator": {
            "report_template.py": '''"""Report template model"""
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass


class ReportTemplate:
    name: str
    sections: List[Dict[str, Any]]
    format_config: Dict[str, Any]
    id: Optional[str] = None''',

            "data_model.py": '''"""Data record model"""
from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass


class DataRecord:
    source_type: str
    processed_at: datetime
    data: Dict[str, Any]
    id: Optional[str] = None'''
        },

        "email - service": {
            "email_template.py": '''"""Email template model"""
from dataclasses import dataclass
from typing import Optional


@dataclass


class EmailTemplate:
    name: str
    subject: str
    body: str
    format: str = "html"
    id: Optional[str] = None''',

            "recipient.py": '''"""Recipient model"""
from dataclasses import dataclass
from typing import Optional


@dataclass


class Recipient:
    email: str
    name: Optional[str] = None
    id: Optional[str] = None''',

            "delivery.py": '''"""Delivery result model"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass


class DeliveryResult:
    recipient: str
    status: str
    sent_at: datetime
    error_message: Optional[str] = None'''
        }
    }

    service_models = models.get(service_name, {})
    service_path = Path(f"services/{service_name}/src / business / models")

    for filename, content in service_models.items():
        model_file = service_path / filename
        model_file.write_text(content)
        print(f"  ✅ Created {filename}")


def migrate_file(source_path: str, migration_config: Dict[str, Any]):
    """Migrate a single source file according to configuration"""

    print(f"\n📄 Migrating {source_path}...")

    if not Path(source_path).exists():
        print(f"  ⚠️  Source file not found: {source_path}")
        return

    content = read_source_file(source_path)
    if not content:
        return

    # Handle multiple target services
    if migration_config["target_service"] == "multiple":
        for location in migration_config["new_locations"]:
            service_name = location["service"]
            target_path = f"services/{service_name}/{location['path']}"
            transform_func = globals().get(location["transform"])

            if transform_func:
                transformed_content = transform_func(content, source_path)
                Path(target_path).parent.mkdir(parents=True, exist_ok=True)
                Path(target_path).write_text(transformed_content)
                print(f"  ✅ Created {target_path}")
            else:
                print(f"  ⚠️  Transform function not found: {location['transform']}")

    elif migration_config["target_service"] == "shared":
        print("  ✅ Already handled in shared components")

    else:
        # Single service target
        service_name = migration_config["target_service"]

        for location in migration_config["new_locations"]:
            target_path = f"services/{service_name}/{location['path']}"
            transform_func = globals().get(location["transform"])

            if transform_func:
                transformed_content = transform_func(content, source_path)
                Path(target_path).parent.mkdir(parents=True, exist_ok=True)
                Path(target_path).write_text(transformed_content)
                print(f"  ✅ Created {target_path}")
            else:
                print(f"  ⚠️  Transform function not found: {location['transform']}")


def create_symlinks():
    """Create symlinks to shared components in each service"""

    print("\n🔗 Creating shared component symlinks...")

    shared_source = Path("shared").absolute()

    for service_name in ["outlook - relay", "database - service", "scheduler - service", "report - generator", "email - service"]:
        service_path = Path(f"services/{service_name}")
        shared_link = service_path / "shared"

        if shared_link.exists():
            shared_link.unlink()

        try:
            shared_link.symlink_to(shared_source)
            print(f"  ✅ Created symlink for {service_name}")
        except Exception as e:
            print(f"  ⚠️  Failed to create symlink for {service_name}: {e}")


def main():
    """Execute the migration"""

    print("🚀 Migrating Existing Code to Microservices")
    print("=" * 60)

    # Create business models first
    print("\n📋 Creating business models...")
    for service_name in ["outlook - relay", "report - generator", "email - service"]:
        print(f"Creating models for {service_name}:")
        create_business_models(service_name)

    # Migrate source files
    for source_file, migration_config in MIGRATION_MAP.items():
        migrate_file(source_file, migration_config)

    # Create symlinks
    create_symlinks()

    print("\n🎉 Migration completed!")
    print("\n📋 Summary:")
    print(f"- Migrated {len(MIGRATION_MAP)} source files")
    print("- Created business models for 3 services")
    print("- Set up shared component symlinks")

    print("\n🚀 Next steps:")
    print("1. Review generated code and adjust business logic")
    print("2. Test individual services: python services / SERVICE_NAME / scripts / run - dev.py")
    print("3. Test all services: python tools / run - all - services.py")
    print("4. Implement missing TODO items")


if __name__ == "__main__":
    main()