"""Test Data Factories
Generates realistic test data for comprehensive testing scenarios
"""

import random
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from business.models.csv_data import CSVFile, CSVRule
from business.models.processing_result import ProcessingResult


@dataclass


class TestDataConfig:
    """Configuration for test data generation"""
    num_records: int = 100
    date_range_days: int = 7
    file_name_pattern: str = "TEST_{type}_{date}_{hour}.csv"
    include_headers: bool = True
    add_noise: bool = True  # Add realistic data variations


class CSVDataFactory:
    """Factory for generating realistic CSV test data"""

    # Sample data pools for realistic generation
    COMPANYNAMES = [
        "Acme Corp", "TechSoft Inc", "DataFlow Systems", "GlobalTech",
        "InnovateCo", "NextGen Solutions", "CloudFirst", "DigitalEdge"
    ]

    PRODUCTTYPES = [
        "Software License", "Hardware", "Support Contract", "Training",
        "Consulting", "Cloud Service", "Integration", "Maintenance"
    ]

    REGIONS = ["North", "South", "East", "West", "Central"]

    STATUSES = ["Active", "Pending", "Completed", "Cancelled", "On Hold"]

    def __init__(self, config: TestDataConfig | None = None):
        self.config = config or TestDataConfig()

    def create_acq_data(self, num_records: int | None = None) -> pd.DataFrame:
        """Generate realistic ACQ (Acquisition) data"""
        records = num_records or self.config.num_records

        data = []
        basedate = datetime.now() - timedelta(days=self.config.date_range_days)

        for i in range(records):
            record = {
                'deal_id': f"ACQ-{random.randint(10000, 99999)}",
                'company_name': random.choice(self.COMPANY_NAMES),
                'product_type': random.choice(self.PRODUCT_TYPES),
                'region': random.choice(self.REGIONS),
                'deal_value': round(random.uniform(1000, 100000), 2),
                'probability': random.randint(10, 100),
                'stage': random.choice(self.STATUSES),
                'created_date': (base_date + timedelta(
                    hours=random.randint(0, self.config.date_range_days * 24)
                )).strftime('%Y-%m-%d %H:%M:%S'),
                'owner': f"rep_{random.randint(1, 20)}",
                'notes': f"Generated test record {i + 1}"
            }

            # Add realistic noise if configured
            if self.config.add_noise:
                # Some records might have missing data
                if random.random() < 0.05:  # 5% chance
                    record['notes'] = None
                if random.random() < 0.02:  # 2% chance
                    record['owner'] = None

            data.append(record)

        return pd.DataFrame(data)

    def create_productivity_data(self, num_records: int | None = None) -> pd.DataFrame:
        """Generate realistic Productivity data"""
        records = num_records or self.config.num_records

        data = []
        basedate = datetime.now() - timedelta(days=self.config.date_range_days)

        for i in range(records):
            record = {
                'employee_id': f"EMP{random.randint(1000, 9999)}",
                'date': (base_date + timedelta(
                    days=random.randint(0, self.config.date_range_days)
                )).strftime('%Y-%m-%d'),
                'calls_made': random.randint(0, 50),
                'emails_sent': random.randint(5, 100),
                'meetings_attended': random.randint(0, 8),
                'deals_updated': random.randint(0, 15),
                'hours_logged': round(random.uniform(4.0, 10.0), 1),
                'efficiency_score': round(random.uniform(0.5, 1.0), 2)
            }
            data.append(record)

        return pd.DataFrame(data)

    def create_campaign_data(self, num_records: int | None = None) -> pd.DataFrame:
        """Generate realistic Campaign Interactions data"""
        records = num_records or self.config.num_records

        interactiontypes = ["Email Open", "Link Click", "Form Submit",
                           "Download", "Webinar Attend", "Demo Request"]

        data = []
        basedate = datetime.now() - timedelta(days=self.config.date_range_days)

        for i in range(records):
            record = {
                'campaign_id': f"CAMP-{random.randint(100, 999)}",
                'contact_id': f"CONT-{random.randint(10000, 99999)}",
                'interaction_type': random.choice(interaction_types),
                'timestamp': (base_date + timedelta(
                    hours=random.randint(0, self.config.date_range_days * 24)
                )).strftime('%Y-%m-%d %H:%M:%S'),
                'source': random.choice(["Email", "Web", "Social", "Direct"]),
                'score': random.randint(1, 100),
                'converted': random.choice([True, False])
            }
            data.append(record)

        return pd.DataFrame(data)


class CSVFileFactory:
    """Factory for creating CSVFile domain objects"""

    def __init__(self, data_factory: CSVDataFactory | None = None):
        self.datafactory = data_factory or CSVDataFactory()

    def create_csv_file(
        self,
        file_type: str = "ACQ",
        date_str: str = None,
        hour_str: str = "09",
        temp_dir: str = None
    ) -> CSVFile:
        """Create a CSVFile object with actual file on disk"""
        if date_str is None:
            datestr = datetime.now().strftime("%Y-%m-%d")

        if temp_dir is None:
            tempdir = tempfile.gettempdir()

        # Generate appropriate data based on file type
        if file_type == "ACQ":
            df = self.data_factory.create_acq_data()
        elif file_type == "Productivity":
            df = self.data_factory.create_productivity_data()
        elif file_type == "Campaign_Interactions":
            df = self.data_factory.create_campaign_data()
        else:
            # Generic data
            df = pd.DataFrame({
                'id': range(1, 101),
                'name': [f"Item {i}" for i in range(1, 101)],
                'value': [random.randint(1, 1000) for _ in range(100)]
            })

        # Create file_name
        file_name = f"{file_type}__{date_str.replace('-', '-')}__{hour_str}00.csv"
        file_path = Path(temp_dir) / file_name

        # Write CSV file
        df.to_csv(file_path, index=False)

        # Create CSV rule
        rule = CSVRule(
            pattern=f"{file_type}__*.csv",
            columns=list(df.columns),
            sheet_name=file_type,
            required_columns=list(df.columns)[:3]  # First 3 columns required
        )

        return CSVFile(
            file_name=file_name,
            file_path=str(file_path),
            date_str=date_str,
            hour_str=hour_str,
            timestamp=datetime.now(),
            rule=rule
        )

    def create_multiple_csv_files(
        self,
        file_types: list[str] = None,
        dates: list[str] = None,
        hours: list[str] = None,
        temp_dir: str = None
    ) -> list[CSVFile]:
        """Create multiple CSV files for testing"""
        if file_types is None:
            filetypes = ["ACQ", "Productivity", "Campaign_Interactions"]

        if dates is None:
            basedate = datetime.now()
            dates = [
                (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(3)
            ]

        if hours is None:
            hours = ["09", "12", "15"]

        csvfiles = []

        for file_type in file_types:
            for date_str in dates:
                for hour_str in hours:
                    csv_file = self.create_csv_file(
                        file_type=file_type,
                        date_str=date_str,
                        hour_str=hour_str,
                        temp_dir=temp_dir
                    )
                    csv_files.append(csv_file)

        return csv_files


class ProcessingResultFactory:
    """Factory for creating ProcessingResult objects"""

    @staticmethod
    def create_success_result(
        files_processed: int = 3,
        total_records: int = 300,
        output_file: str = "/tmp / test_output.xlsx"
    ) -> ProcessingResult:
        """Create a successful processing result"""
        return ProcessingResult(
            success=True,
            message=f"Successfully processed {files_processed} files",
            files_processed=files_processed,
            total_records=total_records,
            processing_time_seconds=random.uniform(1.0, 5.0),
            output_file=output_file,
            errors=[],
            warnings=[]
        )

    @staticmethod
    def create_failure_result(
        error_message: str = "Processing failed",
        files_processed: int = 1
    ) -> ProcessingResult:
        """Create a failed processing result"""
        return ProcessingResult(
            success=False,
            message=error_message,
            files_processed=files_processed,
            total_records=0,
            processing_time_seconds=random.uniform(0.1, 1.0),
            output_file=None,
            errors=[error_message],
            warnings=[]
        )

    @staticmethod
    def create_partial_result(
        files_processed: int = 2,
        total_records: int = 150,
        warnings: list[str] = None
    ) -> ProcessingResult:
        """Create a partially successful processing result"""
        return ProcessingResult(
            success=True,
            message=f"Processed {files_processed} files with warnings",
            files_processed=files_processed,
            total_records=total_records,
            processing_time_seconds=random.uniform(2.0, 8.0),
            output_file="/tmp / partial_output.xlsx",
            errors=[],
            warnings=warnings or ["Some data validation warnings occurred"]
        )


class TestEnvironmentFactory:
    """Factory for creating complete test environments"""

    def __init__(self):
        self.csvfactory = CSVFileFactory()
        self.resultfactory = ProcessingResultFactory()
        self.temp_dirs: list[str] = []

    def create_test_directory_with_files(
        self,
        file_types: list[str] = None,
        num_dates: int = 2,
        num_hours: int = 2
    ) -> tuple[str, list[CSVFile]]:
        """Create a temporary directory with realistic test files"""
        # Create temporary directory
        tempdir = tempfile.mkdtemp(prefix="test_csv_")
        self.temp_dirs.append(temp_dir)

        # Generate date range
        basedate = datetime.now()
        dates = [
            (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(num_dates)
        ]

        # Generate hour range
        hours = [f"{9 + i:02d}" for i in range(num_hours)]

        # Create CSV files
        csvfiles = self.csv_factory.create_multiple_csv_files(
            file_types=file_types,
            dates=dates,
            hours=hours,
            temp_dir=temp_dir
        )

        return temp_dir, csv_files

    def cleanup(self):
        """Clean up temporary directories"""
        import shutil
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
        self.temp_dirs.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
