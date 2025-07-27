import os
from datetime import datetime
import win32com.client

from config_loader import ConfigLoader
from logger import LoggerFactory
from utils import sanitize_filename

class EmailFetcher:
    """
    Connects to Outlook, filters emails by date, sender, subject, and saves CSV attachments.
    """
    def __init__(self, config: ConfigLoader, save_dir: str = 'data/raw', log_file: str = 'fetch_csv.log'):
        self.config = config
        self.save_dir = save_dir
        self.logger = LoggerFactory.get_logger('email_fetcher', log_file)

    def fetch(self, date_str: str):
        """
        Fetch emails received on date_str (YYYY-MM-DD), apply global filters, and save CSV attachments.
        """
        # Parse target date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")
            return

        self.logger.info(f"Fetching CSV emails for date: {target_date}")

        global_filter = self.config.global_filter
        attachment_rules = self.config.attachment_rules

        # Connect to Outlook
        outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
        inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox
        messages = inbox.Items
        messages.Sort('[ReceivedTime]', True)

        for msg in messages:
            try:
                received = msg.ReceivedTime.date()
                if received != target_date:
                    continue

                if not self._is_valid_email(msg, global_filter):
                    self.logger.info(f"Skipping email from {msg.SenderEmailAddress} with subject '{msg.Subject}'")
                    continue

                # Process attachments
                for i in range(1, msg.Attachments.Count + 1):
                    attachment = msg.Attachments.Item(i)
                    filename = attachment.FileName

                    if not filename.lower().endswith('.csv'):
                        self.logger.debug(f"Skipping non-CSV attachment: {filename}")
                        continue

                    rule = self._get_attachment_rule(filename, attachment_rules)
                    if not rule:
                        self.logger.info(f"No matching rule for attachment: {filename}")
                        continue

                    # Build new filename with date
                    base, ext = os.path.splitext(filename)
                    safe_base = sanitize_filename(base)
                    new_name = f"{safe_base}__{date_str}{ext}"

                    # Ensure save directory exists
                    os.makedirs(self.save_dir, exist_ok=True)
                    save_path = os.path.join(self.save_dir, new_name)
                    attachment.SaveAsFile(save_path)

                    self.logger.info(
                        f"Saved attachment: {new_name} | From: {msg.SenderName} | Received: {received}"
                    )

            except Exception as e:
                self.logger.error(f"Error processing email: {e}", exc_info=True)

    def _is_valid_email(self, msg, global_filter: dict) -> bool:
        """
        Check sender and optional subject filters from global_filter.
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
            if key.lower() in name_l:
                return rule
        return None
