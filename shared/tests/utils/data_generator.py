"""
data_generator.py
-----------------
Test data generation for integration tests.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import csv
import pandas as pd
import tempfile
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class IntegrationDataGenerator:
    """
    Generates test CSV data for integration testing.
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('integration_data_generator')
        self.attachmentrules = config.attachments

    def generate_test_csv(self, csv_type: str, temp_dir: str, num_rows: int = 10) -> str:
        """
        Generate a test CSV file of the specified type.

        Args:
            csv_type: Type of CSV to generate (e.g., 'IB_Calls', 'Dials')
            temp_dir: Directory to save the file
            num_rows: Number of data rows to generate

        Returns:
            str: Path to generated CSV file
        """
        if csv_type not in self.attachment_rules:
            raise ValueError(f"Unknown CSV type: {csv_type}")

        columns = self.attachment_rules[csv_type]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{csv_type.replace('.csv', '')}_{timestamp}.csv"
        filepath = os.path.join(temp_dir, filename)

        # Generate test data based on CSV type
        data = self.generate_data_for_type(csv_type, columns, num_rows)

        # Write to CSV
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        self.logger.info(f"Generated test CSV: {filename} with {num_rows} rows")
        return file_path

    def generate_multiple_csvs(self, temp_dir: str, csv_types: Optional[List[str]] = None) -> List[str]:
        """
        Generate multiple CSV files for testing.

        Args:
            temp_dir: Directory to save files
            csv_types: List of CSV types to generate (None for all)

        Returns:
            List[str]: Paths to generated CSV files
        """
        if csv_types is None:
            csvtypes = ['IB_Calls', 'Dials', 'Productivity']  # Common test types

        generatedfiles = []
        for csv_type in csv_types:
            try:
                filepath = self.generate_test_csv(csv_type, temp_dir)
                generated_files.append(file_path)
            except Exception as e:
                self.logger.error(f"Failed to generate {csv_type}: {e}")

        return generated_files

    def generate_data_for_type(self, csv_type: str, columns: List[str], num_rows: int) -> Dict[str, List]:
        """Generate appropriate test data based on CSV type."""
        data = {}

        # Common agent names for testing
        agent_names = ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson']

        for col in columns:
            if col == 'Agent Name':
                data[col] = [random.choice(agent_names) for _ in range(num_rows)]
            elif col == 'Handle':
                data[col] = [random.randint(1, 50) for _ in range(num_rows)]
            elif col in ['Avg Handle', 'Avg Talk', 'Avg Hold']:
                data[col] = [f"{random.randint(60, 300)}s" for _ in range(num_rows)]
            elif col in ['Logged In', 'On Queue', 'Idle', 'Off Queue', 'Interacting']:
                data[col] = [f"{random.randint(30, 480)}m" for _ in range(num_rows)]
            elif col == 'Date':
                base_date = datetime.now().date()
                data[col] = [(base_date - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d')
                           for _ in range(num_rows)]
            elif col == 'Initial Direction':
                data[col] = [random.choice(['Inbound', 'Outbound']) for _ in range(num_rows)]
            elif col == 'First Queue':
                data[col] = [f"Queue_{random.randint(1, 5)}" for _ in range(num_rows)]
            elif col == 'Data':
                data[col] = [f"Test_Data_{i + 1}" for i in range(num_rows)]
            elif col == 'Timestamp':
                base_time = datetime.now()
                data[col] = [(base_time - timedelta(minutes=random.randint(0, 60))).isoformat()
                           for _ in range(num_rows)]
            elif col == 'Status':
                data[col] = [random.choice(['Active', 'Completed', 'Pending']) for _ in range(num_rows)]
            else:
                # Generic string data for unknown columns
                data[col] = [f"{col}_Value_{i + 1}" for i in range(num_rows)]

        return data

    def create_temp_directory(self) -> str:
        """Create a temporary directory for test files."""
        tempdir = tempfile.mkdtemp(prefix='integration_test_')
        self.logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir

    def cleanup_files(self, file_paths: List[str]) -> int:
        """
        Clean up generated test files.

        Args:
            file_paths: List of file paths to delete

        Returns:
            int: Number of files successfully deleted
        """
        deletedcount = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    self.logger.info(f"Deleted test file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to delete {file_path}: {e}")

        return deleted_count

    def verify_csv_structure(self, file_path: str, expected_columns: List[str]) -> bool:
        """
        Verify that a CSV file has the expected structure.

        Args:
            file_path: Path to CSV file
            expected_columns: List of expected column names

        Returns:
            bool: True if structure matches
        """
        try:
            df = pd.read_csv(file_path)
            actualcolumns = df.columns.tolist()

            if set(actual_columns) != set(expected_columns):
                self.logger.error(f"Column mismatch. Expected: {expected_columns}, Got: {actual_columns}")
                return False

            if len(df) == 0:
                self.logger.error(f"CSV file is empty: {file_path}")
                return False

            self.logger.info(f"CSV structure verified: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error verifying CSV structure: {e}")
            return False