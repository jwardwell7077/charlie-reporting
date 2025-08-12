"""
REST Email Client - Updated EmailFetcher
----------------------------------------
Updated EmailFetcher that uses the Windows Email Service REST API instead of direct COM / IMAP.
This allows cross - platform email access while keeping email credentials on the Windows service.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import json
import time

from config_loader import ConfigLoader
from logger import LoggerFactory
from utils import sanitize_filename


class EmailServiceError(Exception):
    """Custom exception for email service errors"""
    pass


class EmailFetcher:
    """
    REST client for Windows Email Service.
    Fetches emails and CSV attachments via HTTP API calls to a Windows service.
    Provides cross - platform email access with fallback to directory scanning.
    """

    def __init__(self, config: ConfigLoader, save_dir: str = 'data / raw', log_file: str = 'fetch_csv.log'):
        self.config = config
        self.savedir = Path(save_dir)
        self.logger = LoggerFactory.get_logger('email_fetcher', log_file)

        # Email service configuration
        email_service_config = getattr(config, 'email_service', {})
        self.serviceurl = email_service_config.get('url', 'http://localhost:8080')
        self.apikey = email_service_config.get('api_key', 'default - dev - key')
        self.timeout = email_service_config.get('timeout_seconds', 60)
        self.retryattempts = email_service_config.get('retry_attempts', 2)

        # Setup request headers
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content - Type': 'application / json'
        }

        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"EmailFetcher initialized with service URL: {self.service_url}")

        # Test service connectivity
        self.check_service_health()

    def check_service_health(self) -> bool:
        """Check if the email service is healthy and accessible"""
        try:
            response = requests.get(
                f"{self.service_url}/api / health",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                healthdata = response.json()
                if health_data.get('outlook_connected', False):
                    self.logger.info("Email service is healthy and Outlook is connected")
                    return True
                else:
                    self.logger.warning("Email service is running but Outlook is not connected")
                    return False
            else:
                self.logger.error(f"Email service health check failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Cannot connect to email service: {e}")
            return False

    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to email service with retry logic"""
        url = f"{self.service_url}/api{endpoint}"

        for attempt in range(self.retry_attempts + 1):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=self.headers, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=self.headers, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise EmailServiceError("Authentication failed - check API key")
                elif response.status_code == 503:
                    raise EmailServiceError("Email service unavailable")
                else:
                    raise EmailServiceError(f"Service returned error: {response.status_code} - {response.text}")

            except requests.exceptions.Timeout:
                if attempt < self.retry_attempts:
                    self.logger.warning(f"Request timeout, retrying... (attempt {attempt + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise EmailServiceError("Request timed out after retries")

            except requests.exceptions.ConnectionError:
                if attempt < self.retry_attempts:
                    self.logger.warning(f"Connection error, retrying... (attempt {attempt + 1})")
                    time.sleep(2 ** attempt)
                else:
                    raise EmailServiceError("Cannot connect to email service")

    def fetch(self, date_str: str) -> bool:
        """
        Fetch emails for a specific date via REST API.

        Args:
            date_str: Date in YYYY - MM - DD format

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Fetching emails for date: {date_str}")

        try:
            # Prepare request data
            request_data = {
                "date": date_str,
                "filters": {
                    "sender": self.config.global_filter.get('sender', []),
                    "subject_contains": self.config.global_filter.get('subject_contains', [])
                },
                "attachment_rules": {
                    filename: {"columns": rule.get('columns', [])}
                    for filename, rule in self.config.attachment_rules.items()
                }
            }

            # Make API call
            responsedata = self.make_request('POST', '/emails / fetch', request_data)

            if response_data.get('success', False):
                processedemails = response_data.get('processed_emails', 0)
                downloadedfiles = response_data.get('downloaded_attachments', 0)
                files = response_data.get('files', [])

                self.logger.info(f"Successfully processed {processed_emails} emails, downloaded {downloaded_files} attachments")

                # Download files from service to local save directory
                self.download_files(files)

                # Also scan directory if enabled
                if self.config.directory_scan.get('enabled', False):
                    self.scan_directory_for_date(date_str)

                return True
            else:
                self.logger.error(f"Email fetch failed: {response_data.get('message', 'Unknown error')}")
                return False

        except EmailServiceError as e:
            self.logger.error(f"Email service error: {e}")
            # Fall back to directory scanning if available
            return self.fallback_directory_scan(date_str)
        except Exception as e:
            self.logger.error(f"Unexpected error during email fetch: {e}")
            return self.fallback_directory_scan(date_str)

    def fetch_hourly(self, date_str: str, hour: int) -> bool:
        """
        Fetch emails for a specific hour via REST API.

        Args:
            date_str: Date in YYYY - MM - DD format
            hour: Hour (0 - 23)

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Fetching emails for {date_str} hour {hour}")

        try:
            request_data = {
                "date": date_str,
                "start_hour": hour,
                "end_hour": hour,
                "filters": {
                    "sender": self.config.global_filter.get('sender', []),
                    "subject_contains": self.config.global_filter.get('subject_contains', [])
                },
                "attachment_rules": {
                    filename: {"columns": rule.get('columns', [])}
                    for filename, rule in self.config.attachment_rules.items()
                }
            }

            responsedata = self.make_request('POST', '/emails / fetch', request_data)

            if response_data.get('success', False):
                files = response_data.get('files', [])
                self.download_files(files)

                # Also scan directory if enabled
                if self.config.directory_scan.get('enabled', False):
                    self.scan_directory_for_hour(date_str, hour)

                return True
            return False

        except EmailServiceError as e:
            self.logger.error(f"Email service error: {e}")
            return self.fallback_directory_scan_hour(date_str, hour)

    def fetch_recent(self, hours: int) -> bool:
        """
        Fetch emails from recent hours via REST API.

        Args:
            hours: Number of hours to look back

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Fetching emails from last {hours} hours")

        try:
            request_data = {
                "hours": hours,
                "filters": {
                    "sender": self.config.global_filter.get('sender', []),
                    "subject_contains": self.config.global_filter.get('subject_contains', [])
                },
                "attachment_rules": {
                    filename: {"columns": rule.get('columns', [])}
                    for filename, rule in self.config.attachment_rules.items()
                }
            }

            responsedata = self.make_request('POST', '/emails / fetch - recent', request_data)

            if response_data.get('success', False):
                files = response_data.get('files', [])
                self.download_files(files)

                # Also scan directory if enabled
                if self.config.directory_scan.get('enabled', False):
                    self.scan_directory_for_recent(hours)

                return True
            return False

        except EmailServiceError as e:
            self.logger.error(f"Email service error: {e}")
            return self.fallback_directory_scan_recent(hours)

    def download_files(self, files: List[Dict]) -> None:
        """Download files from email service to local directory"""
        for file_info in files:
            filename = file_info['filename']
            try:
                response = requests.get(
                    f"{self.service_url}/api / files/{filename}",
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    localpath = self.save_dir / filename
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Downloaded file: {filename}")
                else:
                    self.logger.error(f"Failed to download {filename}: {response.status_code}")

            except Exception as e:
                self.logger.error(f"Error downloading {filename}: {e}")

    def get_accounts(self) -> List[Dict]:
        """Get list of available email accounts from service"""
        try:
            responsedata = self.make_request('GET', '/accounts')
            return response_data.get('accounts', [])
        except EmailServiceError as e:
            self.logger.error(f"Failed to get accounts: {e}")
            return []

    def fallback_directory_scan(self, date_str: str) -> bool:
        """Fallback to directory scanning when email service is unavailable"""
        if self.config.directory_scan.get('enabled', False):
            self.logger.info("Falling back to directory scanning")
            self.scan_directory_for_date(date_str)
            return True
        return False

    def fallback_directory_scan_hour(self, date_str: str, hour: int) -> bool:
        """Fallback to directory scanning for specific hour"""
        if self.config.directory_scan.get('enabled', False):
            self.logger.info("Falling back to directory scanning for hour")
            self.scan_directory_for_hour(date_str, hour)
            return True
        return False

    def fallback_directory_scan_recent(self, hours: int) -> bool:
        """Fallback to directory scanning for recent files"""
        if self.config.directory_scan.get('enabled', False):
            self.logger.info("Falling back to directory scanning for recent files")
            self.scan_directory_for_recent(hours)
            return True
        return False

    # Directory scanning methods (kept from original implementation)
    def scan_directory_for_date(self, date_str: str):
        """Scan configured directory for files modified on specific date"""
        if not self.config.directory_scan.get('enabled', False):
            return

        scanpath = Path(self.config.directory_scan.get('scan_path', ''))
        if not scan_path.exists():
            self.logger.warning(f"Scan directory does not exist: {scan_path}")
            return

        targetdate = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Scan for CSV files
        pattern = "**/*.csv" if self.config.directory_scan.get('process_subdirs', False) else "*.csv"

        for file_path in scan_path.glob(pattern):
            modtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            if mod_time.date() == target_date:
                if file_path.name in self.config.attachment_rules:
                    timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                    filename_base = file_path.stem
                    newfilename = f"{filename_base}__{timestamp}.csv"

                    destpath = self.save_dir / new_filename
                    dest_path.write_bytes(file_path.read_bytes())

                    self.logger.info(f"Copied from directory scan: {new_filename}")

    def scan_directory_for_hour(self, date_str: str, hour: int):
        """Scan directory for files modified in specific hour"""
        if not self.config.directory_scan.get('enabled', False):
            return

        scanpath = Path(self.config.directory_scan.get('scan_path', ''))
        if not scan_path.exists():
            return

        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        starttime = datetime.combine(target_date, datetime.min.time()).replace(hour=hour)
        endtime = start_time.replace(hour=hour, minute=59, second=59)

        pattern = "**/*.csv" if self.config.directory_scan.get('process_subdirs', False) else "*.csv"

        for file_path in scan_path.glob(pattern):
            modtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            if start_time <= mod_time <= end_time:
                if file_path.name in self.config.attachment_rules:
                    timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                    filename_base = file_path.stem
                    newfilename = f"{filename_base}__{timestamp}.csv"

                    destpath = self.save_dir / new_filename
                    dest_path.write_bytes(file_path.read_bytes())

                    self.logger.info(f"Copied from directory scan: {new_filename}")

    def scan_directory_for_recent(self, hours: int):
        """Scan directory for files modified in recent hours"""
        if not self.config.directory_scan.get('enabled', False):
            return

        scanpath = Path(self.config.directory_scan.get('scan_path', ''))
        if not scan_path.exists():
            return

        cutofftime = datetime.now() - timedelta(hours=hours)
        pattern = "**/*.csv" if self.config.directory_scan.get('process_subdirs', False) else "*.csv"

        for file_path in scan_path.glob(pattern):
            modtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            if mod_time >= cutoff_time:
                if file_path.name in self.config.attachment_rules:
                    timestamp = mod_time.strftime('%Y-%m-%d_%H%M')
                    filename_base = file_path.stem
                    newfilename = f"{filename_base}__{timestamp}.csv"

                    destpath = self.save_dir / new_filename
                    dest_path.write_bytes(file_path.read_bytes())

                    self.logger.info(f"Copied from directory scan: {new_filename}")