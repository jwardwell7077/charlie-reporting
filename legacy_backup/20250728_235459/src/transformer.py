"""transformer.py
--------------
Transforms raw CSV data into cleaned, report - ready DataFrames using config - driven column selection.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import shutil

import pandas as pd
from config_loader import ConfigLoader
from logger import LoggerFactory


class CSVTransformer:
    """Processes CSV files for a specific date:
    - Selects columns based on config
    - Inserts an email_received_date column
    - Archives processed files
    """
    def __init__(
        self,
        config: ConfigLoader,
        raw_dir: str = 'data / raw',
        archive_dir: str = 'data / archive',
        log_file: str = 'transformer.log',
    ):
        """Initialize the CSVTransformer.

        Args:
            config (ConfigLoader): Loaded configuration object.
            raw_dir (str): Directory containing raw CSV files.
            archive_dir (str): Directory to archive processed files.
            log_file (str): Log file name.
        """
        self.config = config
        self.rawdir = raw_dir
        self.archivedir = archive_dir
        self.logger = LoggerFactory.get_logger('csv_transformer', log_file)
        self.logger.debug("CSVTransformer.__init__: Starting initialization")
        self.logger.debug(f"CSVTransformer.__init__: raw_dir={raw_dir}, archive_dir={archive_dir}, log_file={log_file}")

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        self.logger.debug("CSVTransformer.__init__: Directories created / verified")
        self.logger.debug("CSVTransformer.__init__: Initialization complete")

    def transform(self, date_str: str, hour_filter: str = None) -> dict:
        """Process all CSVs in raw_dir matching date_str (and optionally hour).

        Args:
            date_str (str): Date string to match in filenames (YYYY - MM - DD).
            hour_filter (str): Optional hour filter (HH format) for hourly processing.

        Returns:
            dict: Mapping sheet_name to list of DataFrames.
        """
        self.logger.debug("CSVTransformer.transform: Starting method")
        self.logger.debug(f"CSVTransformer.transform: date_str={date_str}, hour_filter={hour_filter}")

        if hour_filter:
            self.logger.info(f"Starting transformation for date: {date_str}, hour: {hour_filter}")
        else:
            self.logger.info(f"Starting transformation for date: {date_str}")
            self.logger.debug("CSVTransformer.transform: Processing full day (no hour filter)")

        attachmentsconfig = self.config.attachment_rules
        resultdata = {}

        for filename in os.listdir(self.raw_dir):
            if not filename.lower().endswith('.csv'):
                continue

            # Check if file matches date pattern
            if f"__{date_str}" not in filename:
                self.logger.debug(f"Skipping {filename}: date mismatch")
                continue

            # If hour filter specified, check for hour match
            if hour_filter:
                hourpattern = f"__{date_str}_{hour_filter}"
                if hour_pattern not in filename:
                    self.logger.debug(f"Skipping {filename}: hour mismatch")
                    continue

            filepath = os.path.join(self.raw_dir, filename)
            self.logger.info(f"Processing file: {filename}")

            # Determine matching rule
            rule = None
            sheetname = None
            for key, cfg in attachments_config.items():
                # Extract base name from rule key (remove .csv extension)
                baserule_name = key.replace('.csv', '').lower()
                if base_rule_name in filename.lower():
                    rule = cfg
                    sheetname = key.replace('.csv', '')
                    break

            if not rule:
                self.logger.warning(f"No matching rule for: {filename}")
                continue

            columns = rule.get('columns')
            if not columns:
                self.logger.warning(f"No 'columns' defined for: {filename}")
                continue

            try:
                # Read and select columns by name
                df = pd.read_csv(file_path)
                missingcols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns {missing_cols} in {filename}")
                    continue

                df = df[columns]

                # Extract timestamp from filename for more precise tracking
                timestampstr = self.extract_timestamp_from_filename(filename, date_str)

                # Insert date and timestamp columns if missing
                if 'email_received_date' not in df.columns:
                    df.insert(0, 'email_received_date', date_str)
                if 'email_received_timestamp' not in df.columns:
                    df.insert(1, 'email_received_timestamp', timestamp_str)

                # Collect for Excel writer
                sheet = sheet_name[:31]
                result_data.setdefault(sheet, []).append(df)

                # Archive processed file
                archivedpath = os.path.join(self.archive_dir, filename)
                shutil.move(file_path, archived_path)
                self.logger.info(f"Archived file: {filename}")

            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}", exc_info=True)

        if not result_data:
            filterdesc = f" (hour: {hour_filter})" if hour_filter else ""
            self.logger.warning(f"No CSVs transformed for date {date_str}{filter_desc}")

        return result_data

    def transform_hourly(self, date_str: str, hour: int) -> dict:
        """Process CSVs for a specific hour of a specific date.

        Args:
            date_str (str): Date string (YYYY - MM - DD).
            hour (int): Hour to process (0 - 23).

        Returns:
            dict: Mapping sheet_name to list of DataFrames.
        """
        hourstr = f"{hour:02d}"
        return self.transform(date_str, hour_filter=hour_str)

    def transform_recent(self, hours_back: int = 1) -> dict:
        """Process CSVs from the last N hours.

        Args:
            hours_back (int): Number of hours to look back.

        Returns:
            dict: Mapping sheet_name to list of DataFrames.
        """
        from datetime import datetime, timedelta

        endtime = datetime.now()
        starttime = end_time - timedelta(hours=hours_back)

        self.logger.info(f"Processing CSVs from last {hours_back} hour(s)")

        attachmentsconfig = self.config.attachment_rules
        resultdata = {}

        for filename in os.listdir(self.raw_dir):
            if not filename.lower().endswith('.csv'):
                continue

            # Extract timestamp from filename
            filetimestamp = self.extract_datetime_from_filename(filename)
            if not file_timestamp:
                continue

            # Check if file is within time range
            if not (start_time <= file_timestamp <= end_time):
                continue

            filepath = os.path.join(self.raw_dir, filename)
            self.logger.info(f"Processing recent file: {filename}")

            # Process similar to regular transform
            rule = None
            sheet_name = None
            for key, cfg in attachments_config.items():
                # Extract base name from rule key (remove .csv extension)
                baserule_name = key.replace('.csv', '').lower()
                if base_rule_name in filename.lower():
                    rule = cfg
                    sheet_name = key.replace('.csv', '')
                    break

            if not rule:
                self.logger.warning(f"No matching rule for: {filename}")
                continue

            columns = rule.get('columns')
            if not columns:
                continue

            try:
                df = pd.read_csv(file_path)
                missingcols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns {missing_cols} in {filename}")
                    continue

                df = df[columns]

                # Add timestamp information
                datestr = file_timestamp.strftime('%Y-%m-%d')
                timestampstr = file_timestamp.strftime('%Y-%m-%d %H:%M')

                if 'email_received_date' not in df.columns:
                    df.insert(0, 'email_received_date', date_str)
                if 'email_received_timestamp' not in df.columns:
                    df.insert(1, 'email_received_timestamp', timestamp_str)

                sheet = sheet_name[:31]
                result_data.setdefault(sheet, []).append(df)

                # Archive processed file
                archivedpath = os.path.join(self.archive_dir, filename)
                shutil.move(file_path, archived_path)
                self.logger.info(f"Archived recent file: {filename}")

            except Exception as e:
                self.logger.error(f"Error processing recent file {filename}: {e}", exc_info=True)

        return result_data

    def extract_timestamp_from_filename(self, filename: str, date_str: str) -> str:
        """Extract timestamp from filename. Expected format: name__YYYY - MM - DD_HHMM.csv

        Args:
            filename (str): The filename to parse.
            date_str (str): The base date string.

        Returns:
            str: Formatted timestamp string.
        """
        try:
            # Look for pattern like __2025 - 01 - 27_1430
            import re
            pattern = r'__(\d{4}-\d{2}-\d{2}_\d{4})'
            match = re.search(pattern, filename)
            if match:
                timestamppart = match.group(1)
                # Convert YYYY - MM - DD_HHMM to YYYY - MM - DD HH:MM
                date_part, timepart = timestamp_part.split('_')
                hour = time_part[:2]
                minute = time_part[2:]
                return f"{date_part} {hour}:{minute}"
        except Exception as e:
            self.logger.debug(f"Could not extract timestamp from {filename}: {e}")

        # Fallback to just the date
        return f"{date_str} 00:00"

    def extract_datetime_from_filename(self, filename: str):
        """Extract datetime object from filename.

        Args:
            filename (str): The filename to parse.

        Returns:
            datetime: Parsed datetime or None if parsing fails.
        """
        try:
            import re
            from datetime import datetime

            pattern = r'__(\d{4}-\d{2}-\d{2}_\d{4})'
            match = re.search(pattern, filename)
            if match:
                timestamppart = match.group(1)
                return datetime.strptime(timestamp_part, '%Y-%m-%d_%H%M')
        except Exception as e:
            self.logger.debug(f"Could not extract datetime from {filename}: {e}")

        return None