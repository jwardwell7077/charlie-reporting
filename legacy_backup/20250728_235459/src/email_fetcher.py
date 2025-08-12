import os
from datetime import datetime, timedelta
import platform
from typing import Optional
from pathlib import Path
import shutil

from config_loader import ConfigLoader
from logger import LoggerFactory
from utils import sanitize_filename

# Conditional Windows imports
try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    win32com = None

# Cross - platform email support
try:
    import imaplib
    import email
    from email.header import decode_header
    HAS_IMAP = True
except ImportError:
    HAS_IMAP = False


class EmailFetcher:
    """
    Connects to email service, filters emails by date / time, sender, subject, and saves CSV attachments.
    Supports both daily batch processing and hourly incremental processing.
    Uses pathlib for cross - platform path handling.
    TODO: Implement Graph API for simpler, cleaner email access.
    """
    def __init__(self, config: ConfigLoader, save_dir: str = 'data / raw', log_file: str = 'fetch_csv.log'):
        self.config = config
        self.savedir = Path(save_dir)  # Convert to Path object
        self.logger = LoggerFactory.get_logger('email_fetcher', log_file)
        self.logger.debug("EmailFetcher.__init__: Starting initialization")
        self.logger.debug(f"EmailFetcher.__init__: save_dir={self.save_dir}, log_file={log_file}")

        # TODO: Replace with Graph API implementation
        self.platform = 'mock'  # Placeholder for future Graph API
        self.logger.info(f"Using email platform: {self.platform} (Graph API coming soon)")

        self.logger.debug("EmailFetcher.__init__: Initialization complete")

    def detect_email_platform(self) -> str:
        """Detect which email platform to use."""
        # Check for forced platform via environment
        forcedplatform = os.getenv('EMAIL_CHECKER_PLATFORM', '').lower()
        if forced_platform in ['imap', 'windows']:
            return forced_platform

        # Auto - detect based on system and available libraries
        currentplatform = platform.system().lower()

        if current_platform == 'windows' and HAS_WIN32:
            # Check if we're in WSL
            if 'microsoft' in platform.uname().release.lower():
                return 'imap'
            return 'windows'
        elif HAS_IMAP:
            return 'imap'
        else:
            raise RuntimeError("No compatible email platform available. Install pywin32 (Windows) or ensure imaplib is available (Linux)")

    def init_imap_settings(self):
        """Initialize IMAP settings from config."""
        email_config = self.config.config.get('email', {})
        self.imapserver = email_config.get('imap_server', 'imap.gmail.com')
        self.imapusername = email_config.get('receiver_address') or os.getenv('INTEGRATION_TEST_RECEIVER_EMAIL')
        self.imappassword = os.getenv('INTEGRATION_TEST_EMAIL_PASSWORD') or os.getenv('INTEGRATION_TEST_APP_PASSWORD')

        if not self.imap_username or not self.imap_password:
            self.logger.warning("IMAP credentials not fully configured. Email fetching may fail.")
            self.logger.warning("Set INTEGRATION_TEST_RECEIVER_EMAIL and INTEGRATION_TEST_EMAIL_PASSWORD environment variables")

    def fetch(self, date_str: str):
        """
        Legacy method: Fetch emails received on date_str (YYYY - MM - DD), apply filters, and save CSV attachments.
        Also scans directory if enabled in config.
        """
        self.logger.debug("EmailFetcher.fetch: Starting method")
        self.logger.debug(f"EmailFetcher.fetch: date_str={date_str}")
        self.fetch_for_timeframe(date_str)

        # Also scan directory if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self.logger.debug("EmailFetcher.fetch: Directory scan enabled, calling scan_directory_for_date")
            self.scan_directory_for_date(date_str)
        else:
            self.logger.debug("EmailFetcher.fetch: Directory scan disabled or not configured")

        self.logger.debug("EmailFetcher.fetch: Method completed")

    def fetch_for_timeframe(self, date_str: str, start_hour: Optional[int] = None, end_hour: Optional[int] = None):
        """
        Fetch emails for a specific date or timeframe.

        Args:
            date_str: Date in YYYY - MM - DD format
            start_hour: Starting hour (0 - 23), None for full day
            end_hour: Ending hour (0 - 23), None for full day
        """
        self.logger.debug("EmailFetcher.fetch_for_timeframe: Starting method")
        self.logger.debug(f"EmailFetcher.fetch_for_timeframe: date_str={date_str}, start_hour={start_hour}, end_hour={end_hour}")

        # Parse target date
        try:
            targetdate = datetime.strptime(date_str, '%Y-%m-%d').date()
            self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Parsed target_date={target_date}")
        except ValueError:
            self.logger.error(f"Invalid date format: {date_str}. Expected YYYY - MM - DD.")
            self.logger.debug("EmailFetcher.fetch_for_timeframe: Method completed with error")
            return

        # Set time boundaries
        if start_hour is not None and end_hour is not None:
            starttime = datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour)
            endtime = datetime.combine(target_date, datetime.min.time()).replace(hour=end_hour, minute=59, second=59)
            self.logger.info(f"Fetching emails from {start_time} to {end_time}")
            self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Time range - start_time={start_time}, end_time={end_time}")
        else:
            starttime = datetime.combine(target_date, datetime.min.time())
            endtime = datetime.combine(target_date, datetime.max.time())
            self.logger.info(f"Fetching emails for full day: {target_date}")
            self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Full day - start_time={start_time}, end_time={end_time}")

        globalfilter = self.config.global_filter
        attachmentrules = self.config.attachment_rules
        self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Loaded {len(attachment_rules)} attachment rules")

        # Connect to email service (cross - platform)
        try:
            self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Connecting to email service ({self.platform})")

            if self.platform == 'windows':
                outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
                inbox = self.get_inbox_for_account(outlook)
                messages = inbox.Items
                messages.Sort('[ReceivedTime]', True)
                self.logger.debug(f"EmailFetcher.fetch_for_timeframe: Connected to Outlook, found {messages.Count} messages")

                # Process messages using Windows COM
                processedcount = self.process_outlook_messages(messages, start_time, end_time, global_filter, attachment_rules)

            elif self.platform == 'imap':
                # Process emails using IMAP
                processedcount = self.process_imap_messages(start_time, end_time, global_filter, attachment_rules)

            else:
                raise RuntimeError(f"Unsupported email platform: {self.platform}")

        except Exception as e:
            self.logger.error(f"Failed to connect to email service: {e}")
            self.logger.debug("EmailFetcher.fetch_for_timeframe: Method completed with email connection error")
            return

        self.logger.info(f"Email processing completed. Processed {processed_count} messages.")
        self.logger.debug("EmailFetcher.fetch_for_timeframe: Method completed successfully")

    def process_outlook_messages(self, messages, start_time, end_time, global_filter, attachment_rules):
        """Process messages using Windows Outlook COM interface."""
        processedcount = 0
        self.logger.debug("EmailFetcher.process_outlook_messages: Starting email processing loop")

        for msg in messages:
            try:
                # Get email received time as datetime
                receivedtime = msg.ReceivedTime
                if hasattr(received_time, 'date'):
                    receiveddt = received_time
                else:
                    # Handle different datetime formats
                    receiveddt = datetime.fromisoformat(str(received_time))

                # Check if email is within our timeframe
                if not (start_time <= received_dt <= end_time):
                    continue

                if not self.is_valid_email(msg, global_filter):
                    self.logger.debug(f"Skipping email from {getattr(msg, 'SenderEmailAddress', 'Unknown')} - filter mismatch")
                    continue

                self.logger.debug(f"EmailFetcher.process_outlook_messages: Processing valid email from {getattr(msg, 'SenderEmailAddress', 'Unknown')} received at {received_dt}")

                # Process attachments
                processed_count += self.process_outlook_attachments(msg, received_dt, attachment_rules)

            except Exception as e:
                self.logger.error(f"Error processing email: {e}", exc_info=True)

        return processed_count

    def process_outlook_attachments(self, msg, received_dt, attachment_rules):
        """Process attachments from Outlook message."""
        processedcount = 0
        attachmentcount = getattr(msg, 'Attachments', {})

        if hasattr(attachment_count, 'Count'):
            self.logger.debug(f"EmailFetcher.process_outlook_attachments: Found {attachment_count.Count} attachments")
            for i in range(1, attachment_count.Count + 1):
                attachment = attachment_count.Item(i)
                filename = getattr(attachment, 'FileName', '')
                self.logger.debug(f"EmailFetcher.process_outlook_attachments: Processing attachment {i}: {filename}")

                if not filename.lower().endswith('.csv'):
                    self.logger.debug(f"Skipping non - CSV attachment: {filename}")
                    continue

                rule = self.get_attachment_rule(filename, attachment_rules)
                if not rule:
                    self.logger.info(f"No matching rule for attachment: {filename}")
                    continue

                self.logger.debug(f"EmailFetcher.process_outlook_attachments: Found matching rule for {filename}")

                # Build new filename with timestamp for hourly processing
                base, ext = os.path.splitext(filename)
                safe_base = sanitize_filename(base)

                # Include hour in filename for better tracking
                timestamp = received_dt.strftime('%Y-%m-%d_%H%M')
                newname = f"{safe_base}__{timestamp}{ext}"

                # Ensure save directory exists
                os.makedirs(self.save_dir, exist_ok=True)
                savepath = os.path.join(self.save_dir, new_name)

                # Check if file already exists (avoid duplicate processing)
                if os.path.exists(save_path):
                    self.logger.debug(f"File already exists, skipping: {new_name}")
                    continue

                self.logger.debug(f"EmailFetcher.process_outlook_attachments: Saving attachment as: {new_name}")
                attachment.SaveAsFile(save_path)
                processed_count += 1

                sendername = getattr(msg, 'SenderName', 'Unknown')
                self.logger.info(
                    f"Saved attachment: {new_name} | From: {sender_name} | Received: {received_dt}"
                )

        return processed_count

    def process_imap_messages(self, start_time, end_time, global_filter, attachment_rules):
        """Process messages using IMAP."""
        if not HAS_IMAP:
            raise RuntimeError("IMAP support not available")

        processedcount = 0
        self.logger.debug("EmailFetcher.process_imap_messages: Starting IMAP email processing")

        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.imap_username, self.imap_password)
            mail.select('inbox')

            # Search for emails in date range
            search_date = start_time.strftime('%d-%b-%Y')  # IMAP date format
            typ, data = mail.search(None, f'(SINCE "{search_date}")')

            if not data[0]:
                self.logger.info("No emails found in specified timeframe")
                return 0

            emailids = data[0].split()
            self.logger.debug(f"Found {len(email_ids)} emails to process")

            for email_id in email_ids:
                try:
                    # Fetch email
                    typ, msgdata = mail.fetch(email_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    emailmessage = email.message_from_bytes(email_body)

                    # Parse received time
                    receivedtime_str = email_message.get("Date")
                    if received_time_str:
                        # Parse email date (this is complex, but we'll do basic parsing)
                        try:
                            # Remove timezone info for simplicity
                            receivedtime_str = received_time_str.split('(')[0].strip()
                            receiveddt = datetime.strptime(received_time_str.split(' +')[0].split(' -')[0], '%a, %d %b %Y %H:%M:%S')
                        except Exception:
                            # Fallback to current time if parsing fails
                            receiveddt = datetime.now()
                    else:
                        receiveddt = datetime.now()

                    # Check if email is within our timeframe
                    if not (start_time <= received_dt <= end_time):
                        continue

                    # Create a mock message object for compatibility with existing filter logic
                    mockmsg = type('MockMessage', (), {
                        'SenderEmailAddress': email_message.get("From", ""),
                        'Subject': email_message.get("Subject", ""),
                        'SenderName': email_message.get("From", "").split('<')[0].strip()
                    })()

                    if not self.is_valid_email(mock_msg, global_filter):
                        self.logger.debug(f"Skipping email from {mock_msg.SenderEmailAddress} - filter mismatch")
                        continue

                    self.logger.debug(f"EmailFetcher.process_imap_messages: Processing valid email from {mock_msg.SenderEmailAddress} received at {received_dt}")

                    # Process attachments
                    processed_count += self.process_imap_attachments(email_message, received_dt, attachment_rules, mock_msg.SenderName)

                except Exception as e:
                    self.logger.error(f"Error processing IMAP email {email_id}: {e}", exc_info=True)

            mail.logout()

        except Exception as e:
            self.logger.error(f"IMAP connection error: {e}", exc_info=True)

        return processed_count

    def process_imap_attachments(self, email_message, received_dt, attachment_rules, sender_name):
        """Process attachments from IMAP email message."""
        processedcount = 0

        # Process attachments
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename and filename.lower().endswith('.csv'):

                    rule = self.get_attachment_rule(filename, attachment_rules)
                    if not rule:
                        self.logger.info(f"No matching rule for attachment: {filename}")
                        continue

                    self.logger.debug(f"EmailFetcher.process_imap_attachments: Found matching rule for {filename}")

                    # Build new filename with timestamp
                    base, ext = os.path.splitext(filename)
                    safe_base = sanitize_filename(base)

                    timestamp = received_dt.strftime('%Y-%m-%d_%H%M')
                    newname = f"{safe_base}__{timestamp}{ext}"

                    # Ensure save directory exists
                    os.makedirs(self.save_dir, exist_ok=True)
                    savepath = os.path.join(self.save_dir, new_name)

                    # Check if file already exists
                    if os.path.exists(save_path):
                        self.logger.debug(f"File already exists, skipping: {new_name}")
                        continue

                    # Save attachment
                    attachmentdata = part.get_payload(decode=True)
                    with open(save_path, 'wb') as f:
                        f.write(attachment_data)

                    processed_count += 1
                    self.logger.info(
                        f"Saved attachment: {new_name} | From: {sender_name} | Received: {received_dt}"
                    )

        return processed_count

    def fetch_hourly(self, date_str: str, hour: int):
        """
        Fetch emails for a specific hour of a specific date.
        Also scans directory if enabled in config.

        Args:
            date_str: Date in YYYY - MM - DD format
            hour: Hour to fetch (0 - 23)
        """
        self.fetch_for_timeframe(date_str, start_hour=hour, end_hour=hour)

        # Also scan directory if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self.scan_directory_for_hour(date_str, hour)

    def fetch_recent(self, hours_back: int = 1):
        """
        Fetch emails from the last N hours.
        Also scans directory if enabled in config.

        Args:
            hours_back: Number of hours to look back
        """
        endtime = datetime.now()
        starttime = end_time - timedelta(hours=hours_back)

        self.logger.info(f"Fetching emails from last {hours_back} hour(s): {start_time} to {end_time}")

        # Scan directory first if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self.scan_directory_for_recent(hours_back)

        globalfilter = self.config.global_filter
        attachmentrules = self.config.attachment_rules

        # Connect to email service (cross - platform)
        try:
            self.logger.debug(f"EmailFetcher.fetch_recent: Connecting to email service ({self.platform})")

            if self.platform == 'windows':
                outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
                inbox = self.get_inbox_for_account(outlook)
                messages = inbox.Items
                messages.Sort('[ReceivedTime]', True)

                # Process messages using Windows COM
                processedcount = self.process_recent_outlook_messages(messages, start_time, end_time, global_filter, attachment_rules)

            elif self.platform == 'imap':
                # Process emails using IMAP
                processedcount = self.process_recent_imap_messages(start_time, end_time, global_filter, attachment_rules)

            else:
                raise RuntimeError(f"Unsupported email platform: {self.platform}")

        except Exception as e:
            self.logger.error(f"Failed to connect to email service: {e}")
            return

        self.logger.info(f"Recent email fetch completed. Processed {processed_count} attachments.")

    def process_recent_outlook_messages(self, messages, start_time, end_time, global_filter, attachment_rules):
        """Process recent messages using Windows Outlook COM interface."""
        processedcount = 0

        for msg in messages:
            try:
                receivedtime = msg.ReceivedTime
                if hasattr(received_time, 'date'):
                    receiveddt = received_time
                else:
                    receiveddt = datetime.fromisoformat(str(received_time))

                # Stop processing if we've gone too far back
                if received_dt < start_time:
                    break

                if received_dt > end_time:
                    continue

                if not self.is_valid_email(msg, global_filter):
                    continue

                # Process attachments (similar to fetch_for_timeframe)
                processed_count += self.process_outlook_attachments(msg, received_dt, attachment_rules)

            except Exception as e:
                self.logger.error(f"Error processing recent email: {e}", exc_info=True)

        return processed_count

    def process_recent_imap_messages(self, start_time, end_time, global_filter, attachment_rules):
        """Process recent messages using IMAP."""
        if not HAS_IMAP:
            raise RuntimeError("IMAP support not available")

        processedcount = 0

        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.imap_username, self.imap_password)
            mail.select('inbox')

            # Search for recent emails
            search_date = start_time.strftime('%d-%b-%Y')  # IMAP date format
            typ, data = mail.search(None, f'(SINCE "{search_date}")')

            if not data[0]:
                self.logger.info("No recent emails found")
                return 0

            emailids = data[0].split()
            self.logger.debug(f"Found {len(email_ids)} recent emails to process")

            for email_id in email_ids:
                try:
                    # Fetch email
                    typ, msgdata = mail.fetch(email_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    emailmessage = email.message_from_bytes(email_body)

                    # Parse received time (simplified)
                    receivedtime_str = email_message.get("Date")
                    if received_time_str:
                        try:
                            received_time_str = received_time_str.split('(')[0].strip()
                            receiveddt = datetime.strptime(received_time_str.split(' +')[0].split(' -')[0], '%a, %d %b %Y %H:%M:%S')
                        except Exception:
                            receiveddt = datetime.now()
                    else:
                        receiveddt = datetime.now()

                    # Check if email is within our timeframe
                    if received_dt < start_time or received_dt > end_time:
                        continue

                    # Create a mock message object for compatibility
                    mockmsg = type('MockMessage', (), {
                        'SenderEmailAddress': email_message.get("From", ""),
                        'Subject': email_message.get("Subject", ""),
                        'SenderName': email_message.get("From", "").split('<')[0].strip()
                    })()

                    if not self.is_valid_email(mock_msg, global_filter):
                        continue

                    # Process attachments
                    processed_count += self.process_imap_attachments(email_message, received_dt, attachment_rules, mock_msg.SenderName)

                except Exception as e:
                    self.logger.error(f"Error processing recent IMAP email {email_id}: {e}", exc_info=True)

            mail.logout()

        except Exception as e:
            self.logger.error(f"IMAP connection error: {e}", exc_info=True)

        return processed_count

    def is_valid_email(self, msg, global_filter: dict) -> bool:
        """
        Check sender and optional subject filters from global_filter.
        Args:
            msg: Outlook mail item or mock message object.
            global_filter (dict): Filter with 'sender' and 'subject_contains'.
        Returns:
            bool: True if email passes filters, False otherwise.
        """
        # Handle both Outlook COM objects and mock objects
        sender = getattr(msg, 'SenderEmailAddress', '')
        subject = getattr(msg, 'Subject', '') or ''

        allowed = global_filter.get('sender', [])
        allowed = [allowed] if isinstance(allowed, str) else allowed
        if allowed and sender not in allowed:
            return False

        mustcontain = global_filter.get('subject_contains', [])
        mustcontain = [must_contain] if isinstance(must_contain, str) else must_contain
        if must_contain and not any(substr.lower() in subject.lower() for substr in must_contain):
            return False

        return True

    def get_attachment_rule(self, filename: str, rules: dict) -> dict:
        """
        Return the matching rule dict for a given filename via substring matching.
        """
        namel = filename.lower()
        for key, rule in rules.items():
            # Extract base name from rule key (remove .csv extension)
            baserule_name = key.replace('.csv', '').lower()
            if base_rule_name in name_l:
                return rule
        return None

    def get_inbox_for_account(self, outlook_namespace):
        """
        Get the inbox for the specified account, or default if not specified / found.

        Args:
            outlook_namespace: Outlook MAPI namespace

        Returns:
            Inbox folder object
        """
        targetaccount = self.config.email.get('outlook_account') if hasattr(self.config, 'email') and isinstance(self.config.email, dict) else None

        if not target_account:
            # No specific account specified, use default
            return outlook_namespace.GetDefaultFolder(6)  # 6 = Inbox

        try:
            # Search through all accounts
            for account in outlook_namespace.Session.Accounts:
                if account.SmtpAddress.lower() == target_account.lower():
                    # Get the inbox for this specific account
                    inbox = account.DeliveryStore.GetDefaultFolder(6)
                    self.logger.info(f"Using inbox for account: {target_account}")
                    return inbox

            # Account not found, fall back to default
            self.logger.warning(f"Account '{target_account}' not found, using default inbox")
            return outlook_namespace.GetDefaultFolder(6)

        except Exception as e:
            self.logger.error(f"Error accessing account '{target_account}': {e}, using default inbox")
            return outlook_namespace.GetDefaultFolder(6)

    def scan_directory_for_date(self, date_str: str):
        """
        Scan the configured directory for CSV files modified on the target date.
        Uses pathlib for cross - platform path handling.

        Args:
            date_str: Date in YYYY - MM - DD format
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scanpath = Path(scan_config.get('scan_path', 'data / incoming'))
        processsubdirs = scan_config.get('process_subdirs', False)

        if not scan_path.exists():
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return

        # Parse target date
        try:
            targetdate = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.logger.error(f"Invalid date format for directory scan: {date_str}")
            return

        self.logger.info(f"Scanning directory for CSV files: {scan_path}")

        # Find CSV files using pathlib
        if process_subdirs:
            csvfiles = list(scan_path.rglob('*.csv'))  # Recursive search
        else:
            csvfiles = list(scan_path.glob('*.csv'))  # Non - recursive search

        attachment_rules = self.config.attachment_rules
        processedcount = 0

        for file_path in csv_files:
            try:
                # Check file modification date
                modtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mod_time.date() != target_date:
                    continue

                filename = file_path.name

                # Check if file matches any rules
                rule = self.get_attachment_rule(filename, attachment_rules)
                if not rule:
                    self.logger.debug(f"No matching rule for directory file: {filename}")
                    continue

                # Build timestamped filename
                base = file_path.stem
                ext = file_path.suffix
                safe_base = sanitize_filename(base)
                timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                newname = f"{safe_base}__{timestamp}{ext}"

                # Ensure save directory exists
                self.save_dir.mkdir(parents=True, exist_ok=True)
                savepath = self.save_dir / new_name

                # Check if file already exists
                if save_path.exists():
                    self.logger.debug(f"File already exists, skipping: {new_name}")
                    continue

                # Copy file to save directory
                shutil.copy2(file_path, save_path)
                processed_count += 1

                self.logger.info(f"Copied from directory: {new_name} | Modified: {mod_time}")

            except Exception as e:
                self.logger.error(f"Error processing directory file {file_path}: {e}", exc_info=True)

        self.logger.info(f"Directory scan completed. Processed {processed_count} files.")

    def scan_directory_for_hour(self, date_str: str, hour: int):
        """
        Scan the configured directory for CSV files modified in a specific hour.
        Uses pathlib for cross - platform path handling.

        Args:
            date_str: Date in YYYY - MM - DD format
            hour: Hour to scan (0 - 23)
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scanpath = Path(scan_config.get('scan_path', 'data / incoming'))

        if not scan_path.exists():
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return

        # Parse target date and hour
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            starttime = datetime.combine(target_date, datetime.min.time()).replace(hour=hour)
            endtime = start_time.replace(hour=hour, minute=59, second=59)
        except ValueError:
            self.logger.error(f"Invalid date format for directory scan: {date_str}")
            return

        self.scan_directory_for_timeframe(scan_path, start_time, end_time)

    def scan_directory_for_recent(self, hours_back: int):
        """
        Scan the configured directory for CSV files modified in the last N hours.
        Uses pathlib for cross - platform path handling.

        Args:
            hours_back: Number of hours to look back
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scanpath = Path(scan_config.get('scan_path', 'data / incoming'))

        if not scan_path.exists():
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return

        endtime = datetime.now()
        starttime = end_time - timedelta(hours=hours_back)

        self.scan_directory_for_timeframe(scan_path, start_time, end_time)

    def scan_directory_for_timeframe(self, scan_path: Path, start_time: datetime, end_time: datetime):
        """
        Scan directory for files modified within a specific timeframe.
        Uses pathlib for cross - platform path handling.

        Args:
            scan_path: Directory path to scan (as Path object)
            start_time: Start of timeframe
            end_time: End of timeframe
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        processsubdirs = scan_config.get('process_subdirs', False)

        self.logger.info(f"Scanning directory for timeframe {start_time} to {end_time}: {scan_path}")

        # Find CSV files using pathlib
        if process_subdirs:
            csvfiles = list(scan_path.rglob('*.csv'))  # Recursive search
        else:
            csvfiles = list(scan_path.glob('*.csv'))  # Non - recursive search

        attachment_rules = self.config.attachment_rules
        processedcount = 0

        for file_path in csv_files:
            try:
                # Check file modification time
                modtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if not (start_time <= mod_time <= end_time):
                    continue

                filename = file_path.name

                # Check if file matches any rules
                rule = self.get_attachment_rule(filename, attachment_rules)
                if not rule:
                    self.logger.debug(f"No matching rule for directory file: {filename}")
                    continue

                # Build timestamped filename
                base = file_path.stem
                ext = file_path.suffix
                safe_base = sanitize_filename(base)
                timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                newname = f"{safe_base}__{timestamp}{ext}"

                # Ensure save directory exists
                self.save_dir.mkdir(parents=True, exist_ok=True)
                savepath = self.save_dir / new_name

                # Check if file already exists
                if save_path.exists():
                    self.logger.debug(f"File already exists, skipping: {new_name}")
                    continue

                # Copy file to save directory
                shutil.copy2(file_path, save_path)
                processed_count += 1

                self.logger.info(f"Copied from directory: {new_name} | Modified: {mod_time}")

            except Exception as e:
                self.logger.error(f"Error processing directory file {file_path}: {e}", exc_info=True)

        self.logger.info(f"Directory timeframe scan completed. Processed {processed_count} files.")