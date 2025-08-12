"""
Complete Email Processing Service
Migrated and enhanced from src / email_fetcher.py
"""
import csv
import email.header
import email.message
import email.utils
import imaplib
import io
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import shared utilities
sys.path.append(str(Path(__file__).parent.parent.parent / 'shared'))
try:
    from config_manager import ConfigManager
    from file_archiver import FileArchiver
    from logging_utils import setup_logging
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
            return {'successful': []}


class EmailProcessor:
    """
    Comprehensive email processing service.
    Migrated and enhanced from src / email_fetcher.py
    """

    def __init__(self, config_path: Optional[str] = None):
        # Basic configuration
        self.logger = logging.getLogger('email_processor')

        # Email connection settings
        self.imapserver = None

        # Processing settings
        self.batchsize = 50
        self.retryattempts = 3
        self.outputdir = Path('data / processed')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def connect_to_email(
        self,
        server: str,
        username: str,
        password: str,
        port: int = 993,
        use_ssl: bool = True
    ) -> bool:
        """Connect to email server with enhanced error handling."""
        try:
            if use_ssl:
                self.imapserver = imaplib.IMAP4_SSL(server, port)
            else:
                self.imapserver = imaplib.IMAP4(server, port)

            self.imap_server.login(username, password)
            self.logger.info(f"Successfully connected to {server}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to email server: {e}")
            return False

    async def fetch_emails_by_criteria(
        self,
        folder: str = 'INBOX',
        subject_filter: Optional[str] = None,
        sender_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Fetch emails based on various criteria with enhanced filtering."""
        if not self.imap_server:
            self.logger.error("No email connection established")
            return []

        try:
            self.imap_server.select(folder)

            # Build search criteria
            searchcriteria = self.build_search_criteria(
                subject_filter, sender_filter, date_filter
            )

            search_string = (' '.join(search_criteria)
                             if search_criteria else 'ALL')

            typ, data = self.imap_server.search(None, search_string)
            if typ != 'OK':
                self.logger.error(f"Email search failed: {typ}")
                return []

            emailids = data[0].split()
            if limit:
                emailids = email_ids[-limit:]  # Get most recent

            return await self.process_email_batch(email_ids, folder)

        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []

    def build_search_criteria(
        self,
        subject_filter: Optional[str],
        sender_filter: Optional[str],
        date_filter: Optional[str]
    ) -> List[str]:
        """Build IMAP search criteria from filters."""
        searchcriteria = []
        if subject_filter:
            search_criteria.append(f'SUBJECT "{subject_filter}"')
        if sender_filter:
            search_criteria.append(f'FROM "{sender_filter}"')
        if date_filter:
            search_criteria.append(f'SINCE "{date_filter}"')
        return search_criteria

    async def process_email_batch(
        self, email_ids: List[bytes], folder: str
    ) -> List[Dict]:
        """Process a batch of email IDs."""
        emails = []
        for i, email_id in enumerate(email_ids):
            if i % 10 == 0:  # Progress logging
                self.logger.info(
                    f"Processing email {i + 1}/{len(email_ids)}"
                )

            emaildata = await self.fetch_single_email(email_id)
            if email_data:
                emails.append(email_data)

        self.logger.info(f"Fetched {len(emails)} emails from {folder}")
        return emails

    async def fetch_single_email(self, email_id: bytes) -> Optional[Dict]:
        """Fetch and parse a single email with comprehensive data extraction."""
        try:
            typ, data = self.imap_server.fetch(email_id.decode(), '(RFC822)')
            if typ != 'OK' or not data:
                return None

            raw_email = data[0][1]
            emailmessage = email.message_from_bytes(raw_email)

            # Extract email metadata
            emaildata = {
                'id': email_id.decode(),
                'subject': self.decode_header(email_message['Subject']),
                'sender': self.decode_header(email_message['From']),
                'recipient': self.decode_header(email_message['To']),
                'date': email_message['Date'],
                'timestamp': self.parse_email_date(email_message['Date']),
                'attachments': [],
                'body_text': '',
                'body_html': '',
                'has_csv': False,
                'csv_data': []
            }

            # Process email body and attachments
            await self.process_email_parts(email_message, email_data)

            return email_data

        except Exception as e:
            self.logger.error(f"Error processing email {email_id}: {e}")
            return None

    async def process_email_parts(
        self, email_message, email_data: Dict
    ) -> None:
        """Process email body and attachments with CSV detection."""
        for part in email_message.walk():
            contenttype = part.get_content_type()
            contentdisposition = str(part.get('Content - Disposition', ''))

            await self.process_text_content(part, content_type, email_data)
            await self.process_attachments(
                part, content_disposition, email_data
            )

    async def process_text_content(
        self, part, content_type: str, email_data: Dict
    ) -> None:
        """Process text content from email parts."""
        if content_type == 'text / plain':
            try:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode('utf - 8')
                    email_data['body_text'] = body
            except (UnicodeDecodeError, AttributeError):
    pass
        elif content_type == 'text / html':
            try:
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode('utf - 8')
                    email_data['body_html'] = body
            except (UnicodeDecodeError, AttributeError):
    pass

    async def process_attachments(
        self, part, content_disposition: str, email_data: Dict
    ) -> None:
        """Process email attachments."""
        if 'attachment' not in content_disposition:
            return

        filename = part.get_filename()
        if not filename:
            return

        attachmentdata = {
            'filename': filename,
            'content_type': part.get_content_type(),
            'size': 0
        }

        # Process CSV attachments
        if filename.lower().endswith('.csv'):
            csvcontent = await self.extract_csv_from_attachment(part)
            if csv_content:
                attachment_data['csv_data'] = csv_content
                email_data['has_csv'] = True
                email_data['csv_data'].append(csv_content)

        email_data['attachments'].append(attachment_data)

    async def extract_csv_from_attachment(
        self, attachment_part
    ) -> Optional[List[Dict]]:
        """Extract and parse CSV data from email attachment."""
        try:
            csvbytes = attachment_part.get_payload(decode=True)
            if isinstance(csv_bytes, bytes):
                csv_text = csv_bytes.decode('utf - 8')

                # Parse CSV
                csvreader = csv.DictReader(io.StringIO(csv_text))
                csvdata = []
                for row in csv_reader:
                    csv_data.append(dict(row))

                self.logger.info(
                    f"Extracted {len(csv_data)} rows from CSV attachment"
                )
                return csv_data

        except Exception as e:
            self.logger.error(f"Error extracting CSV: {e}")

        return None

    async def process_emails_to_csv(
        self,
        emails: List[Dict],
        output_filename: Optional[str] = None
    ) -> str:
        """Process emails and save extracted data to CSV files."""
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"email_data_{timestamp}.csv"

        outputpath = self.output_dir / output_filename

        try:
            with open(output_path, 'w', newline='',
                      encoding='utf - 8') as csvfile:
                fieldnames = [
                    'email_id', 'subject', 'sender', 'date', 'timestamp',
                    'has_attachments', 'has_csv', 'csv_row_count',
                    'body_preview'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for email_data in emails:
                    row = self.build_csv_row(email_data)
                    writer.writerow(row)

            self.logger.info(f"Email data saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Error saving email data to CSV: {e}")
            raise

    def build_csv_row(self, email_data: Dict) -> Dict:
        """Build a CSV row from email data."""
        return {
            'email_id': email_data['id'],
            'subject': email_data['subject'],
            'sender': email_data['sender'],
            'date': email_data['date'],
            'timestamp': email_data['timestamp'],
            'has_attachments': len(email_data['attachments']) > 0,
            'has_csv': email_data['has_csv'],
            'csv_row_count': sum(len(csv) for csv in email_data['csv_data']),
            'body_preview': (email_data['body_text'][:200]
                             if email_data['body_text'] else '')
        }

    async def extract_csv_attachments(
        self,
        emails: List[Dict],
        save_individual: bool = True
    ) -> List[str]:
        """Extract CSV attachments and save them as separate files."""
        savedfiles = []

        for email_data in emails:
            if not email_data['has_csv']:
                continue

            for i, csv_data in enumerate(email_data['csv_data']):
                if save_individual and csv_data:
                    filepath = self.save_csv_attachment(
                        csv_data, email_data['id'], i
                    )
                    if filepath:
                        saved_files.append(filepath)

        return saved_files

    def save_csv_attachment(
        self, csv_data: List[Dict], email_id: str, index: int
    ) -> Optional[str]:
        """Save a single CSV attachment to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"csv_extract_{email_id}_{index}_{timestamp}.csv"
            filepath = self.output_dir / filename

            with open(filepath, 'w', newline='', encoding='utf - 8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            self.logger.info(f"Saved CSV attachment: {filename}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Error saving CSV attachment: {e}")
            return None

    async def fetch_recent_emails(
        self, hours_back: int = 24, **kwargs
    ) -> List[Dict]:
        """Fetch emails from the last N hours with criteria."""
        date_filter = ((datetime.now() - timedelta(hours=hours_back))
                       .strftime('%d-%b-%Y'))
        kwargs['date_filter'] = date_filter
        return await self.fetch_emails_by_criteria(**kwargs)

    def decode_header(self, header_value: Optional[str]) -> str:
        """Decode email header with proper encoding handling."""
        if not header_value:
            return ''

        try:
            decodedparts = email.header.decode_header(header_value)
            decodedstring = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf - 8')
                else:
                    decoded_string += str(part)
            return decoded_string
        except (UnicodeDecodeError, AttributeError):
            return str(header_value)

    def parse_email_date(self, date_string: Optional[str]) -> Optional[str]:
        """Parse email date string to ISO format."""
        if not date_string:
            return None

        try:
            # Parse email date format
            parseddate = email.utils.parsedate_tz(date_string)
            if parsed_date:
                timestamp = email.utils.mktime_tz(parsed_date)
                return datetime.fromtimestamp(timestamp).isoformat()
        except (ValueError, TypeError):
    pass

        return date_string

    async def disconnect(self):
        """Clean disconnect from email server."""
        if self.imap_server:
            try:
                self.imap_server.close()
                self.imap_server.logout()
                self.logger.info("Email connection closed")
            except Exception:
    pass
            finally:
                self.imapserver = None