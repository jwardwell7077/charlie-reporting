"""
db_connector.py
--------------
Provides database connectivity for storing and retrieving report data.
Uses a file-based database for local development and production.

Author: Jonathan Wardwell
License: MIT
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple

from src.logger import LoggerFactory


class DBConnector:
    """
    Database connector for the reporting system.
    Handles storage and retrieval of report data using SQLite.
    """

    def __init__(self, db_path: str = 'data/reports.db'):
        """
        Initialize the database connector.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = LoggerFactory.get_logger('db_connector', log_file='db.log')

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database if it doesn't exist
        self._init_db()

    def _init_db(self):
        """
        Initialize the database schema if needed.
        """
        try:
            self.logger.info(f"Initializing database at {self.db_path}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create metadata table for tracking report types and schemas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_metadata (
                report_type TEXT PRIMARY KEY,
                schema_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Create table for tracking raw data imports
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                report_type TEXT,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                record_count INTEGER,
                status TEXT
            )
            """)

            conn.commit()
            conn.close()

            self.logger.info("Database initialization complete")

        except Exception as e:
            self.logger.error(f"Database initialization error: {e}", exc_info=True)
            raise

    def store_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """
        Store a DataFrame in the database.

        Args:
            df: DataFrame to store
            table_name: Name of the table
            if_exists: How to behave if the table exists ('fail', 'replace', or 'append')

        Returns:
            Success status
        """
        try:
            self.logger.info(f"Storing {len(df)} rows to table {table_name}")

            conn = sqlite3.connect(self.db_path)

            # Store the data
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)

            conn.close()

            self.logger.info(f"Successfully stored data in table {table_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error storing data in table {table_name}: {e}", exc_info=True)
            return False

    def store_multiple_dataframes(self, data_dict: Dict[str, List[pd.DataFrame]]) -> Dict[str, bool]:
        """
        Store multiple DataFrames in the database.

        Args:
            data_dict: Dictionary mapping table names to lists of DataFrames

        Returns:
            Dictionary of table names to success status
        """
        results = {}

        for table_name, df_list in data_dict.items():
            self.logger.info(f"Processing {len(df_list)} DataFrames for table {table_name}")

            success = True
            for df in df_list:
                if not self.store_dataframe(df, table_name):
                    success = False

            results[table_name] = success

        return results

    def query(self, sql: str, params: Optional[Union[Tuple, Dict]] = None) -> pd.DataFrame:
        """
        Execute a query and return results as a DataFrame.

        Args:
            sql: SQL query string
            params: Query parameters (optional)

        Returns:
            DataFrame with query results
        """
        try:
            self.logger.debug(f"Executing query: {sql}")

            conn = sqlite3.connect(self.db_path)

            if params:
                result = pd.read_sql_query(sql, conn, params=params)
            else:
                result = pd.read_sql_query(sql, conn)

            conn.close()

            self.logger.debug(f"Query returned {len(result)} rows")
            return result

        except Exception as e:
            self.logger.error(f"Query error: {e}", exc_info=True)
            return pd.DataFrame()  # Return empty DataFrame on error

    def execute(self, sql: str, params: Optional[Union[Tuple, Dict]] = None) -> bool:
        """
        Execute a non-query SQL statement.

        Args:
            sql: SQL statement
            params: Statement parameters (optional)

        Returns:
            Success status
        """
        try:
            self.logger.debug(f"Executing statement: {sql}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.logger.error(f"Statement execution error: {e}", exc_info=True)
            return False

    def get_report_types(self) -> List[str]:
        """
        Get a list of all report types in the database.

        Returns:
            List of report type names
        """
        try:
            df = self.query("SELECT report_type FROM report_metadata")
            return df['report_type'].tolist()
        except Exception as e:
            self.logger.error(f"Error getting report types: {e}", exc_info=True)
            return []

    def register_report_type(self, report_type: str, schema_json: str) -> bool:
        """
        Register a new report type with its schema.

        Args:
            report_type: Name of the report type
            schema_json: JSON string describing the schema

        Returns:
            Success status
        """
        sql = """
        INSERT INTO report_metadata (report_type, schema_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(report_type) DO UPDATE SET 
            schema_json = excluded.schema_json,
            updated_at = CURRENT_TIMESTAMP
        """

        return self.execute(sql, (report_type, schema_json))

    def log_import(self, filename: str, report_type: str, record_count: int, status: str) -> bool:
        """
        Log an import operation.

        Args:
            filename: Name of the imported file
            report_type: Type of report
            record_count: Number of records imported
            status: Status of the import ('success', 'partial', 'failed')

        Returns:
            Success status
        """
        sql = """
        INSERT INTO import_history 
        (filename, report_type, record_count, status)
        VALUES (?, ?, ?, ?)
        """

        return self.execute(sql, (filename, report_type, record_count, status))
