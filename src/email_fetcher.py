import os
from datetime import datetime, timedelta
import win32com.client
from typing import Optional
import glob
import shutil

from config_loader import ConfigLoader
from logger import LoggerFactory
from utils import sanitize_filename

class EmailFetcher:
    """
    Connects to Outlook, filters emails by date/time, sender, subject, and saves CSV attachments.
    Supports both daily batch processing and hourly incremental processing.
    """
    def __init__(self, config: ConfigLoader, save_dir: str = 'data/raw', log_file: str = 'fetch_csv.log'):
        self.config = config
        self.save_dir = save_dir
        self.logger = LoggerFactory.get_logger('email_fetcher', log_file)

    def fetch(self, date_str: str):
        """
        Legacy method: Fetch emails received on date_str (YYYY-MM-DD), apply filters, and save CSV attachments.
        Also scans directory if enabled in config.
        """
        self.fetch_for_timeframe(date_str)
        
        # Also scan directory if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self._scan_directory_for_date(date_str)

    def fetch_for_timeframe(self, date_str: str, start_hour: Optional[int] = None, end_hour: Optional[int] = None):
        """
        Fetch emails for a specific date or timeframe.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            start_hour: Starting hour (0-23), None for full day
            end_hour: Ending hour (0-23), None for full day
        """
        # Parse target date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
            return

        # Set time boundaries
        if start_hour is not None and end_hour is not None:
            start_time = datetime.combine(target_date, datetime.min.time()).replace(hour=start_hour)
            end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=end_hour, minute=59, second=59)
            self.logger.info(f"Fetching emails from {start_time} to {end_time}")
        else:
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            self.logger.info(f"Fetching emails for full day: {target_date}")

        global_filter = self.config.global_filter
        attachment_rules = self.config.attachment_rules

        # Connect to Outlook
        try:
            outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
            inbox = self._get_inbox_for_account(outlook)
            messages = inbox.Items
            messages.Sort('[ReceivedTime]', True)
        except Exception as e:
            self.logger.error(f"Failed to connect to Outlook: {e}")
            return

        processed_count = 0
        for msg in messages:
            try:
                # Get email received time as datetime
                received_time = msg.ReceivedTime
                if hasattr(received_time, 'date'):
                    received_dt = received_time
                else:
                    # Handle different datetime formats
                    received_dt = datetime.fromisoformat(str(received_time))

                # Check if email is within our timeframe
                if not (start_time <= received_dt <= end_time):
                    continue

                if not self._is_valid_email(msg, global_filter):
                    self.logger.debug(f"Skipping email from {getattr(msg, 'SenderEmailAddress', 'Unknown')} - filter mismatch")
                    continue

                # Process attachments
                attachment_count = getattr(msg, 'Attachments', {})
                if hasattr(attachment_count, 'Count'):
                    for i in range(1, attachment_count.Count + 1):
                        attachment = attachment_count.Item(i)
                        filename = getattr(attachment, 'FileName', '')

                        if not filename.lower().endswith('.csv'):
                            self.logger.debug(f"Skipping non-CSV attachment: {filename}")
                            continue

                        rule = self._get_attachment_rule(filename, attachment_rules)
                        if not rule:
                            self.logger.info(f"No matching rule for attachment: {filename}")
                            continue

                        # Build new filename with timestamp for hourly processing
                        base, ext = os.path.splitext(filename)
                        safe_base = sanitize_filename(base)
                        
                        # Include hour in filename for better tracking
                        timestamp = received_dt.strftime('%Y-%m-%d_%H%M')
                        new_name = f"{safe_base}__{timestamp}{ext}"

                        # Ensure save directory exists
                        os.makedirs(self.save_dir, exist_ok=True)
                        save_path = os.path.join(self.save_dir, new_name)
                        
                        # Check if file already exists (avoid duplicate processing)
                        if os.path.exists(save_path):
                            self.logger.debug(f"File already exists, skipping: {new_name}")
                            continue
                        
                        attachment.SaveAsFile(save_path)
                        processed_count += 1

                        sender_name = getattr(msg, 'SenderName', 'Unknown')
                        self.logger.info(
                            f"Saved attachment: {new_name} | From: {sender_name} | Received: {received_dt}"
                        )

            except Exception as e:
                self.logger.error(f"Error processing email: {e}", exc_info=True)

        self.logger.info(f"Email fetch completed. Processed {processed_count} attachments.")

    def fetch_hourly(self, date_str: str, hour: int):
        """
        Fetch emails for a specific hour of a specific date.
        Also scans directory if enabled in config.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            hour: Hour to fetch (0-23)
        """
        self.fetch_for_timeframe(date_str, start_hour=hour, end_hour=hour)
        
        # Also scan directory if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self._scan_directory_for_hour(date_str, hour)

    def fetch_recent(self, hours_back: int = 1):
        """
        Fetch emails from the last N hours.
        Also scans directory if enabled in config.
        
        Args:
            hours_back: Number of hours to look back
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        self.logger.info(f"Fetching emails from last {hours_back} hour(s): {start_time} to {end_time}")
        
        # Scan directory first if enabled
        if hasattr(self.config, 'directory_scan') and self.config.directory_scan.get('enabled', False):
            self._scan_directory_for_recent(hours_back)
        
        global_filter = self.config.global_filter
        attachment_rules = self.config.attachment_rules

        # Connect to Outlook
        try:
            outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
            inbox = self._get_inbox_for_account(outlook)
            messages = inbox.Items
            messages.Sort('[ReceivedTime]', True)
        except Exception as e:
            self.logger.error(f"Failed to connect to Outlook: {e}")
            return

        processed_count = 0
        for msg in messages:
            try:
                received_time = msg.ReceivedTime
                if hasattr(received_time, 'date'):
                    received_dt = received_time
                else:
                    received_dt = datetime.fromisoformat(str(received_time))

                # Stop processing if we've gone too far back
                if received_dt < start_time:
                    break

                if received_dt > end_time:
                    continue

                if not self._is_valid_email(msg, global_filter):
                    continue

                # Process attachments (similar to fetch_for_timeframe)
                attachment_count = getattr(msg, 'Attachments', {})
                if hasattr(attachment_count, 'Count'):
                    for i in range(1, attachment_count.Count + 1):
                        attachment = attachment_count.Item(i)
                        filename = getattr(attachment, 'FileName', '')

                        if not filename.lower().endswith('.csv'):
                            continue

                        rule = self._get_attachment_rule(filename, attachment_rules)
                        if not rule:
                            continue

                        base, ext = os.path.splitext(filename)
                        safe_base = sanitize_filename(base)
                        timestamp = received_dt.strftime('%Y-%m-%d_%H%M')
                        new_name = f"{safe_base}__{timestamp}{ext}"

                        os.makedirs(self.save_dir, exist_ok=True)
                        save_path = os.path.join(self.save_dir, new_name)
                        
                        if os.path.exists(save_path):
                            continue
                        
                        attachment.SaveAsFile(save_path)
                        processed_count += 1

                        sender_name = getattr(msg, 'SenderName', 'Unknown')
                        self.logger.info(f"Saved recent attachment: {new_name} | From: {sender_name}")

            except Exception as e:
                self.logger.error(f"Error processing recent email: {e}", exc_info=True)

        self.logger.info(f"Recent email fetch completed. Processed {processed_count} attachments.")

    def _is_valid_email(self, msg, global_filter: dict) -> bool:
        """
        Check sender and optional subject filters from global_filter.
        Args:
            msg: Outlook mail item.
            global_filter (dict): Filter with 'sender' and 'subject_contains'.
        Returns:
            bool: True if email passes filters, False otherwise.
        """
        sender = msg.SenderEmailAddress
        subject = msg.Subject or ''

        allowed = global_filter.get('sender', [])
        allowed = [allowed] if isinstance(allowed, str) else allowed
        if allowed and sender not in allowed:
            return False

        must_contain = global_filter.get('subject_contains', [])
        must_contain = [must_contain] if isinstance(must_contain, str) else must_contain
        if must_contain and not any(substr.lower() in subject.lower() for substr in must_contain):
            return False

        return True

    def _get_attachment_rule(self, filename: str, rules: dict) -> dict:
        """
        Return the matching rule dict for a given filename via substring matching.
        """
        name_l = filename.lower()
        for key, rule in rules.items():
            # Extract base name from rule key (remove .csv extension)
            base_rule_name = key.replace('.csv', '').lower()
            if base_rule_name in name_l:
                return rule
        return None

    def _get_inbox_for_account(self, outlook_namespace):
        """
        Get the inbox for the specified account, or default if not specified/found.
        
        Args:
            outlook_namespace: Outlook MAPI namespace
            
        Returns:
            Inbox folder object
        """
        target_account = self.config.email.get('outlook_account') if hasattr(self.config, 'email') and isinstance(self.config.email, dict) else None
        
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

    def _scan_directory_for_date(self, date_str: str):
        """
        Scan the configured directory for CSV files modified on the target date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scan_path = scan_config.get('scan_path', 'data/incoming')
        process_subdirs = scan_config.get('process_subdirs', False)
        
        if not os.path.exists(scan_path):
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return
        
        # Parse target date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.logger.error(f"Invalid date format for directory scan: {date_str}")
            return
        
        self.logger.info(f"Scanning directory for CSV files: {scan_path}")
        
        # Build search pattern
        pattern = os.path.join(scan_path, '*.csv')
        if process_subdirs:
            pattern = os.path.join(scan_path, '**', '*.csv')
            csv_files = glob.glob(pattern, recursive=True)
        else:
            csv_files = glob.glob(pattern)
        
        attachment_rules = self.config.attachment_rules
        processed_count = 0
        
        for file_path in csv_files:
            try:
                # Check file modification date
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mod_time.date() != target_date:
                    continue
                
                filename = os.path.basename(file_path)
                
                # Check if file matches any rules
                rule = self._get_attachment_rule(filename, attachment_rules)
                if not rule:
                    self.logger.debug(f"No matching rule for directory file: {filename}")
                    continue
                
                # Build timestamped filename
                base, ext = os.path.splitext(filename)
                safe_base = sanitize_filename(base)
                timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                new_name = f"{safe_base}__{timestamp}{ext}"
                
                # Ensure save directory exists
                os.makedirs(self.save_dir, exist_ok=True)
                save_path = os.path.join(self.save_dir, new_name)
                
                # Check if file already exists
                if os.path.exists(save_path):
                    self.logger.debug(f"File already exists, skipping: {new_name}")
                    continue
                
                # Copy file to save directory
                shutil.copy2(file_path, save_path)
                processed_count += 1
                
                self.logger.info(f"Copied from directory: {new_name} | Modified: {mod_time}")
                
            except Exception as e:
                self.logger.error(f"Error processing directory file {file_path}: {e}", exc_info=True)
        
        self.logger.info(f"Directory scan completed. Processed {processed_count} files.")

    def _scan_directory_for_hour(self, date_str: str, hour: int):
        """
        Scan the configured directory for CSV files modified in a specific hour.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            hour: Hour to scan (0-23)
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scan_path = scan_config.get('scan_path', 'data/incoming')
        
        if not os.path.exists(scan_path):
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return
        
        # Parse target date and hour
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.combine(target_date, datetime.min.time()).replace(hour=hour)
            end_time = start_time.replace(hour=hour, minute=59, second=59)
        except ValueError:
            self.logger.error(f"Invalid date format for directory scan: {date_str}")
            return
        
        self._scan_directory_for_timeframe(scan_path, start_time, end_time)

    def _scan_directory_for_recent(self, hours_back: int):
        """
        Scan the configured directory for CSV files modified in the last N hours.
        
        Args:
            hours_back: Number of hours to look back
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        scan_path = scan_config.get('scan_path', 'data/incoming')
        
        if not os.path.exists(scan_path):
            self.logger.warning(f"Directory scan path does not exist: {scan_path}")
            return
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        self._scan_directory_for_timeframe(scan_path, start_time, end_time)

    def _scan_directory_for_timeframe(self, scan_path: str, start_time: datetime, end_time: datetime):
        """
        Scan directory for files modified within a specific timeframe.
        
        Args:
            scan_path: Directory to scan
            start_time: Start of timeframe
            end_time: End of timeframe
        """
        scan_config = getattr(self.config, 'directory_scan', {})
        process_subdirs = scan_config.get('process_subdirs', False)
        
        self.logger.info(f"Scanning directory for timeframe {start_time} to {end_time}: {scan_path}")
        
        # Build search pattern
        pattern = os.path.join(scan_path, '*.csv')
        if process_subdirs:
            pattern = os.path.join(scan_path, '**', '*.csv')
            csv_files = glob.glob(pattern, recursive=True)
        else:
            csv_files = glob.glob(pattern)
        
        attachment_rules = self.config.attachment_rules
        processed_count = 0
        
        for file_path in csv_files:
            try:
                # Check file modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if not (start_time <= mod_time <= end_time):
                    continue
                
                filename = os.path.basename(file_path)
                
                # Check if file matches any rules
                rule = self._get_attachment_rule(filename, attachment_rules)
                if not rule:
                    self.logger.debug(f"No matching rule for directory file: {filename}")
                    continue
                
                # Build timestamped filename
                base, ext = os.path.splitext(filename)
                safe_base = sanitize_filename(base)
                timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                new_name = f"{safe_base}__{timestamp}{ext}"
                
                # Ensure save directory exists
                os.makedirs(self.save_dir, exist_ok=True)
                save_path = os.path.join(self.save_dir, new_name)
                
                # Check if file already exists
                if os.path.exists(save_path):
                    self.logger.debug(f"File already exists, skipping: {new_name}")
                    continue
                
                # Copy file to save directory
                shutil.copy2(file_path, save_path)
                processed_count += 1
                
                self.logger.info(f"Copied from directory: {new_name} | Modified: {mod_time}")
                
            except Exception as e:
                self.logger.error(f"Error processing directory file {file_path}: {e}", exc_info=True)
        
        self.logger.info(f"Directory timeframe scan completed. Processed {processed_count} files.")
