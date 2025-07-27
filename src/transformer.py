import os
import shutil
import pandas as pd

from logger import LoggerFactory
from config_loader import ConfigLoader
from utils import parse_excel_range


class CSVTransformer:
    """
    CSVTransformer processes CSV files saved for a specific date:
      - Slices columns based on configured range
      - Inserts an email_received_date column
      - Archives processed files
    """
    def __init__(
        self,
        config: ConfigLoader,
        raw_dir: str = 'data/raw',
        archive_dir: str = 'data/archive',
        log_file: str = 'transformer.log',
    ):
        self.config = config
        self.raw_dir = raw_dir
        self.archive_dir = archive_dir
        self.logger = LoggerFactory.get_logger('csv_transformer', log_file)

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

    def transform(self, date_str: str) -> dict:
        """
        Process all CSVs in raw_dir matching date_str (in filename).

        Returns:
            A dict mapping sheet_name to list of DataFrames.
        """
        self.logger.info(f"Starting transformation for date: {date_str}")

        attachments_config = self.config.attachment_rules
        result_data = {}

        for filename in os.listdir(self.raw_dir):
            if not filename.lower().endswith('.csv'):
                continue

            # Only process files for the given date
            if f"__{date_str}" not in filename:
                self.logger.debug(f"Skipping {filename}: date mismatch")
                continue

            file_path = os.path.join(self.raw_dir, filename)
            self.logger.info(f"Processing file: {filename}")


            # Determine matching rule
            rule = None
            sheet_name = None
            for key, cfg in attachments_config.items():
                if key.lower() in filename.lower():
                    rule = cfg
                    sheet_name = key.replace('.csv', '')
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
                missing_cols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns {missing_cols} in {filename}")
                    continue
                df = df[columns]

                # Insert date column if missing
                if 'email_received_date' not in df.columns:
                    df.insert(0, 'email_received_date', date_str)

                # Collect for Excel writer
                sheet = sheet_name[:31]
                result_data.setdefault(sheet, []).append(df)

                # Archive processed file
                archived_path = os.path.join(self.archive_dir, filename)
                shutil.move(file_path, archived_path)
                self.logger.info(f"Archived file: {filename}")

            except Exception as e:
                self.logger.error(f"Error processing {filename}: {e}", exc_info=True)

        if not result_data:
            self.logger.warning(f"No CSVs transformed for date {date_str}")

        return result_data
