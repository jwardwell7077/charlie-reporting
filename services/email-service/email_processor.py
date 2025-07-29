"""
Complete Email Processing Service
Migrated and enhanced from src/email_fetcher.py
"""
import sys
import imaplib
import email.message
import email.header
import email.utils
import logging
import asyncio
from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
import re
import time
import csv
import io

# Import shared utilities
sys.path.append(str(Path(__file__).parent.parent.parent / 'shared'))
try:
    from config_manager import ConfigManager
    from logging_utils import setup_logging
    from file_archiver import FileArchiver
except ImportError:
    # Fallback for development
    logging.basicConfig(level=logging.INFO)
    
    class ConfigManager:
        def __init__(self, config_path=None):
            self.config = {}
        def get(self, key, default=None):
            return default
    
    def setup_logging(name):
        return logging.getLogger(name)
    
    class FileArchiver:
        async def archive_multiple_files(self, files):
            return {'successful': []};

"""
Complete Email Processing Service
Migrated and enhanced from src/email_fetcher.py
"""
import sys
import imaplib
import email.message
import email.header
import email.utils
import logging
import asyncio
from typing import List, Dict, Tuple, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
import re
import csv
import io

class EmailProcessor:
    """
    Comprehensive email processing service.
    Migrated and enhanced from src/email_fetcher.py
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Basic configuration
        self.logger = logging.getLogger('email_processor')
        
        # Email connection settings
        self.imap_server = None
        
        # Processing settings
        self.batch_size = 50
        self.retry_attempts = 3
        self.output_dir = Path('data/processed')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def connect_to_email(self, server: str, username: str, password: str, 
                              port: int = 993, use_ssl: bool = True) -> bool:
        """Connect to email server with enhanced error handling."""
        try:
            if use_ssl:
                self.imap_server = imaplib.IMAP4_SSL(server, port)
            else:
                self.imap_server = imaplib.IMAP4(server, port)
            
            self.imap_server.login(username, password)
            self.logger.info(f"Successfully connected to {server}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to email server: {e}")
            return False
    
    async def fetch_emails_by_criteria(self, folder: str = 'INBOX', 
                                     subject_filter: Optional[str] = None,
                                     sender_filter: Optional[str] = None,
                                     date_filter: Optional[str] = None,
                                     limit: Optional[int] = None) -> List[Dict]:
        """Fetch emails based on various criteria with enhanced filtering."""
        if not self.imap_server:
            self.logger.error("No email connection established")
            return []
        
        try:
            self.imap_server.select(folder)
            
            # Build search criteria
            search_criteria = []
            if subject_filter:
                search_criteria.append(f'SUBJECT "{subject_filter}"')
            if sender_filter:
                search_criteria.append(f'FROM "{sender_filter}"')
            if date_filter:
                search_criteria.append(f'SINCE "{date_filter}"')
            
            search_string = ' '.join(search_criteria) if search_criteria else 'ALL'
            
            typ, data = self.imap_server.search(None, search_string)
            if typ != 'OK':
                self.logger.error(f"Email search failed: {typ}")
                return []
            
            email_ids = data[0].split()
            if limit:
                email_ids = email_ids[-limit:]  # Get most recent
            
            emails = []
            for i, email_id in enumerate(email_ids):
                if i % 10 == 0:  # Progress logging
                    self.logger.info(f"Processing email {i+1}/{len(email_ids)}")
                
                email_data = await self._fetch_single_email(email_id)
                if email_data:
                    emails.append(email_data)
            
            self.logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []
    
    async def _fetch_single_email(self, email_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email with comprehensive data extraction."""
        try:
            typ, data = self.imap_server.fetch(email_id.decode(), '(RFC822)')
            if typ != 'OK' or not data:
                return None
            
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract email metadata
            email_data = {
                'id': email_id.decode(),
                'subject': self._decode_header(email_message['Subject']),
                'sender': self._decode_header(email_message['From']),
                'recipient': self._decode_header(email_message['To']),
                'date': email_message['Date'],
                'timestamp': self._parse_email_date(email_message['Date']),
                'attachments': [],
                'body_text': '',
                'body_html': '',
                'has_csv': False,
                'csv_data': []
            }
            
            # Process email body and attachments
            await self._process_email_parts(email_message, email_data)
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error processing email {email_id}: {e}")
            return None
    
    async def _process_email_parts(self, email_message, email_data: Dict) -> None:
        """Process email body and attachments with CSV detection."""
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition', ''))
            
            # Handle text content
            if content_type == 'text/plain':
                try:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode('utf-8')
                        email_data['body_text'] = body
                except:
                    pass
            elif content_type == 'text/html':
                try:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode('utf-8')
                        email_data['body_html'] = body
                except:
                    pass
            
            # Handle attachments
            elif 'attachment' in content_disposition:
                filename = part.get_filename()
                if filename:
                    attachment_data = {
                        'filename': filename,
                        'content_type': content_type,
                        'size': 0
                    }
                    
                    # Process CSV attachments
                    if filename.lower().endswith('.csv'):
                        csv_content = await self._extract_csv_from_attachment(part)
                        if csv_content:
                            attachment_data['csv_data'] = csv_content
                            email_data['has_csv'] = True
                            email_data['csv_data'].append(csv_content)
                    
                    email_data['attachments'].append(attachment_data)
    
    async def _extract_csv_from_attachment(self, attachment_part) -> Optional[List[Dict]]:
        """Extract and parse CSV data from email attachment."""
        try:
            csv_bytes = attachment_part.get_payload(decode=True)
            if isinstance(csv_bytes, bytes):
                csv_text = csv_bytes.decode('utf-8')
                
                # Parse CSV
                csv_reader = csv.DictReader(io.StringIO(csv_text))
                csv_data = []
                for row in csv_reader:
                    csv_data.append(dict(row))
                
                self.logger.info(f"Extracted {len(csv_data)} rows from CSV attachment")
                return csv_data
            
        except Exception as e:
            self.logger.error(f"Error extracting CSV: {e}")
        
        return None
    
    async def process_emails_to_csv(self, emails: List[Dict], 
                                  output_filename: Optional[str] = None) -> str:
        """Process emails and save extracted data to CSV files."""
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"email_data_{timestamp}.csv"
        
        output_path = self.output_dir / output_filename
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['email_id', 'subject', 'sender', 'date', 'timestamp', 
                             'has_attachments', 'has_csv', 'csv_row_count', 'body_preview']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for email_data in emails:
                    row = {
                        'email_id': email_data['id'],
                        'subject': email_data['subject'],
                        'sender': email_data['sender'],
                        'date': email_data['date'],
                        'timestamp': email_data['timestamp'],
                        'has_attachments': len(email_data['attachments']) > 0,
                        'has_csv': email_data['has_csv'],
                        'csv_row_count': sum(len(csv) for csv in email_data['csv_data']),
                        'body_preview': email_data['body_text'][:200] if email_data['body_text'] else ''
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Email data saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error saving email data to CSV: {e}")
            raise
    
    async def extract_csv_attachments(self, emails: List[Dict], 
                                    save_individual: bool = True) -> List[str]:
        """Extract CSV attachments and save them as separate files."""
        saved_files = []
        
        for email_data in emails:
            if not email_data['has_csv']:
                continue
            
            for i, csv_data in enumerate(email_data['csv_data']):
                if save_individual and csv_data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    email_id = email_data['id']
                    filename = f"csv_extract_{email_id}_{i}_{timestamp}.csv"
                    filepath = self.output_dir / filename
                    
                    try:
                        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                            fieldnames = csv_data[0].keys()
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(csv_data)
                        
                        saved_files.append(str(filepath))
                        self.logger.info(f"Saved CSV attachment: {filename}")
                        
                    except Exception as e:
                        self.logger.error(f"Error saving CSV attachment: {e}")
        
        return saved_files
    
    async def fetch_recent_emails(self, hours_back: int = 24, **kwargs) -> List[Dict]:
        """Fetch emails from the last N hours with criteria."""
        date_filter = (datetime.now() - timedelta(hours=hours_back)).strftime('%d-%b-%Y')
        kwargs['date_filter'] = date_filter
        return await self.fetch_emails_by_criteria(**kwargs)
    
    def _decode_header(self, header_value: Optional[str]) -> str:
        """Decode email header with proper encoding handling."""
        if not header_value:
            return ''
        
        try:
            decoded_parts = email.header.decode_header(header_value)
            decoded_string = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8')
                else:
                    decoded_string += str(part)
            return decoded_string
        except:
            return str(header_value)
    
    def _parse_email_date(self, date_string: Optional[str]) -> Optional[str]:
        """Parse email date string to ISO format."""
        if not date_string:
            return None
        
        try:
            # Parse email date format
            parsed_date = email.utils.parsedate_tz(date_string)
            if parsed_date:
                timestamp = email.utils.mktime_tz(parsed_date)
                return datetime.fromtimestamp(timestamp).isoformat()
        except:
            pass
        
        return date_string
    
    async def disconnect(self):
        """Clean disconnect from email server."""
        if self.imap_server:
            try:
                self.imap_server.close()
                self.imap_server.logout()
                self.logger.info("Email connection closed")
            except:
                pass
            finally:
                self.imap_server = None
