"""
Email Fetcher Business Service
Pure business logic for email operations - migrated from src/email_fetcher.py
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
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')
        has_attachments = bool(email_data.get('attachments', []))
        
        return config.should_process_email(subject, sender, has_attachments)
    
    def process_email_batch(self, emails: List[Dict[str, Any]], config: OutlookConfiguration) -> List[Email]:
        """
        Business logic for processing a batch of emails
        """
        processed_emails = []
        
        for email_data in emails:
            if self.should_fetch_email(email_data, config):
                try:
                    email = self._convert_to_domain_email(email_data)
                    processed_emails.append(email)
                    self.logger.debug(f"Processed email: {email.subject}")
                except Exception as e:
                    self.logger.error(f"Failed to process email: {e}")
        
        self.logger.info(f"Processed {len(processed_emails)} emails from {len(emails)} total")
        return processed_emails
    
    def filter_emails_by_time_range(self, emails: List[Email], config: OutlookConfiguration) -> List[Email]:
        """
        Filter emails by the configured time range
        """
        start_time, end_time = config.get_time_range()
        
        filtered_emails = []
        for email in emails:
            if start_time <= email.received_time <= end_time:
                filtered_emails.append(email)
        
        self.logger.info(f"Filtered {len(filtered_emails)} emails within time range {start_time} to {end_time}")
        return filtered_emails
    
    def categorize_emails_by_type(self, emails: List[Email]) -> Dict[str, List[Email]]:
        """
        Group emails by their detected type (ACQ, QCBS, etc.)
        """
        categorized = {}
        
        for email in emails:
            email_type = email.extract_email_type()
            if email_type:
                if email_type not in categorized:
                    categorized[email_type] = []
                categorized[email_type].append(email)
            else:
                # Store unclassified emails
                if 'UNCLASSIFIED' not in categorized:
                    categorized['UNCLASSIFIED'] = []
                categorized['UNCLASSIFIED'].append(email)
        
        return categorized
    
    def prepare_attachment_save_paths(self, email: Email, base_save_dir: Path) -> Dict[str, Path]:
        """
        Business logic for determining where to save attachments
        """
        save_paths = {}
        email_type = email.extract_email_type() or 'UNCLASSIFIED'
        
        # Create type-specific directory
        type_dir = base_save_dir / email_type
        
        for attachment in email.get_csv_attachments():
            # Sanitize filename for filesystem
            safe_filename = self._sanitize_filename(attachment)
            
            # Add timestamp to avoid conflicts
            timestamp = email.received_time.strftime("%Y%m%d_%H%M")
            filename_parts = safe_filename.split('.')
            if len(filename_parts) > 1:
                safe_filename = f"{filename_parts[0]}_{timestamp}.{filename_parts[1]}"
            else:
                safe_filename = f"{safe_filename}_{timestamp}.csv"
            
            save_paths[attachment] = type_dir / safe_filename
        
        return save_paths
    
    def validate_email_data_quality(self, emails: List[Email]) -> Dict[str, Any]:
        """
        Business rules for data quality validation
        """
        quality_report = {
            'total_emails': len(emails),
            'emails_with_csv': 0,
            'emails_by_type': {},
            'errors': [],
            'warnings': []
        }
        
        for email in emails:
            # Check for CSV attachments
            if email.has_csv_attachments:
                quality_report['emails_with_csv'] += 1
            
            # Count by type
            email_type = email.extract_email_type() or 'UNCLASSIFIED'
            if email_type not in quality_report['emails_by_type']:
                quality_report['emails_by_type'][email_type] = 0
            quality_report['emails_by_type'][email_type] += 1
            
            # Validate email completeness
            if not email.subject:
                quality_report['warnings'].append(f"Email {email.id} has empty subject")
            if not email.sender:
                quality_report['warnings'].append(f"Email {email.id} has empty sender")
            if not email.attachments and email.has_csv_attachments:
                quality_report['errors'].append(f"Email {email.id} flagged as having CSV but no attachments found")
        
        return quality_report
    
    def _convert_to_domain_email(self, email_data: Dict[str, Any]) -> Email:
        """Convert raw email data to domain model"""
        return Email(
            subject=email_data.get('subject', ''),
            sender=email_data.get('sender', ''),
            received_time=email_data.get('received_time', datetime.now()),
            body=email_data.get('body', ''),
            attachments=email_data.get('attachments', []),
            id=email_data.get('id'),
            folder=email_data.get('folder')
        )
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility
        Migrated from utils.py
        """
        import re
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        
        # Remove leading/trailing periods and spaces
        filename = filename.strip('. ')
        
        # Ensure it's not empty
        if not filename:
            filename = "unknown_file"
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = f"{name[:95]}.{ext}" if ext else name[:100]
        
        return filename
