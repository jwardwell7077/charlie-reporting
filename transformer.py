import os
import pandas as pd
from openpyxl.utils import column_index_from_string
from logger import get_logger
import re
import shutil
import yaml
from datetime import datetime

RAW_DIR = "data/raw"
ARCHIVE_DIR = "data/archive"
OUTPUT_DIR = "data/output"
CONFIG_PATH = "config/columns_config.yaml"

logger = get_logger("csv_transformer")


def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_attachment_rule(attachment_name: str, attachments_config: dict):
    attachment_name = attachment_name.lower()
    for config_key, rule in attachments_config.items():
        if config_key.lower() in attachment_name:
            return rule
    return None


def parse_excel_range(range_str):
    start_col, end_col = range_str.split(":")
    start_idx = column_index_from_string(start_col) - 1
    end_idx = column_index_from_string(end_col) - 1
    return start_idx, end_idx


def extract_date_from_filename(filename):
    match = re.search(r'__(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None


def transform_and_generate_excel(date_str):
    logger.info(f"Starting transformation for date: {date_str}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    config = load_config()
    attachments_config = config.get("attachments", {})

    result_data = {}

    for filename in os.listdir(RAW_DIR):
        if not filename.lower().endswith(".csv"):
            continue

        if f"__{date_str}" not in filename:
            logger.debug(f"Skipping file not matching date: {filename}")
            continue

        file_path = os.path.join(RAW_DIR, filename)
        logger.info(f"Processing: {filename}")

        rule = get_attachment_rule(filename, attachments_config)
        if not rule:
            logger.warning(f"No matching rule for: {filename}")
            continue

        col_range = rule.get("range")
        if not col_range:
            logger.warning(f"No 'range' in rule for: {filename}")
            continue

        try:
            df = pd.read_csv(file_path, header=0)
            start_idx, end_idx = parse_excel_range(col_range)
            df = df.iloc[:, start_idx:end_idx + 1]

            # Add date column if not already present
            if "email_received_date" not in df.columns:
                df.insert(0, "email_received_date", date_str)

            sheet_name = rule.get("sheet_name", os.path.splitext(filename)[0].split("__")[0])
            result_data.setdefault(sheet_name[:31], []).append(df)

            # Archive the file
            archived_path = os.path.join(ARCHIVE_DIR, filename)
            shutil.move(file_path, archived_path)
            logger.info(f"Archived: {filename}")

        except Exception as e:
            logger.error(f"Failed to process {filename}: {e}", exc_info=True)

    if not result_data:
        logger.warning("No matching CSVs found to transform.")
        return

    output_path = os.path.join(OUTPUT_DIR, f"report_{date_str}.xlsx")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet_name, df_list in result_data.items():
            combined_df = pd.concat(df_list, ignore_index=True)
            combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f"Excel report generated: {output_path}")
