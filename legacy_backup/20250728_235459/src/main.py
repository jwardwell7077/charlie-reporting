
"""
main.py
-------
Entry point for the real - time reporting ETL pipeline. Supports hourly incremental processing,
on - demand reports, and end - of - day summaries for contact center data.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import sys
import argparse
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from config_loader import ConfigLoader
from email_fetcher import EmailFetcher  # from db_service.db_processor import DBProcessor  # Temporarily disabled for demo  # from db_service.report_generator import ReportGenerator  # Temporarily disabled for demo
from excel_writer import ExcelWriter
from logger import LoggerFactory


class ReportProcessor:
    """
    Handles real - time incremental processing of contact center reports.
    Supports hourly processing, incremental Excel updates, and on - demand reporting.
    """

    def __init__(self, config: ConfigLoader, debug: bool = False):
        self.config = config
        self.logger = LoggerFactory.get_logger('report_processor', log_file='main.log')
        self.logger.debug("ReportProcessor.__init__: Starting initialization")

        if debug:
            self.logger.setLevel('DEBUG')
            for handler in self.logger.handlers:
                handler.setLevel('DEBUG')

        # Initialize components
        self.logger.debug("ReportProcessor.__init__: Creating EmailFetcher instance")
        self.emailfetcher = EmailFetcher(config)
        # self.dbprocessor = DBProcessor(config)  # Database temporarily disabled
        # self.reportgenerator = ReportGenerator()  # Database temporarily disabled
        self.logger.debug("ReportProcessor.__init__: Creating ExcelWriter instance")
        self.excelwriter = ExcelWriter()

        # Track processing state
        self.lastprocessed_time = None
        self.dailydata_cache = {}
        self.logger.debug("ReportProcessor.__init__: Initialization complete")

    def process_hourly(self, target_datetime: Optional[datetime] = None) -> Dict:
        """
        Process emails for a specific hour and update Excel incrementally.

        Args:
            target_datetime: Specific datetime to process (defaults to current hour)

        Returns:
            Dict containing processed data for the hour
        """
        self.logger.debug("ReportProcessor.process_hourly: Starting method")

        if target_datetime is None:
            target_datetime = datetime.now().replace(minute=0, second=0, microsecond=0)
        else:
            # Normalize to hour boundary
            target_datetime = target_datetime.replace(minute=0, second=0, microsecond=0)

        hourstr = target_datetime.strftime('%Y-%m-%d_%H')
        datestr = target_datetime.strftime('%Y-%m-%d')
        hour = target_datetime.hour

        self.logger.info(f'Starting hourly processing for: {hour_str}')
        self.logger.debug(f"ReportProcessor.process_hourly: Processing hour {hour} for date {date_str}")

        try:
            # Fetch emails for this specific hour
            self.logger.debug("ReportProcessor.process_hourly: Calling email_fetcher.fetch")
            self.email_fetcher.fetch(date_str)

            # Process CSVs into database (temporarily disabled for demo)
            # processeddata = self.db_processor.process(date_str)
            processeddata = None  # Database processing disabled
            self.logger.debug("ReportProcessor.process_hourly: Database processing skipped (disabled for demo)")

            if processed_data:
                # Update daily cache for backward compatibility
                self.logger.debug("ReportProcessor.process_hourly: Updating daily cache")
                self.update_daily_cache(date_str, processed_data)

                # Get hourly data from database (temporarily disabled for demo)
                # reportdata = self.report_generator.get_hourly_report(date_str, hour)
                reportdata = None  # Database reporting disabled

                # Write incremental Excel update
                self.logger.debug("ReportProcessor.process_hourly: Writing incremental Excel update")
                self.excel_writer.write_incremental(report_data, date_str, hour_str)

                self.logger.info(f'Hourly processing completed for {hour_str}: {len(processed_data)} datasets processed')
            else:
                self.logger.info(f'No new data found for {hour_str}')
                self.logger.debug("ReportProcessor.process_hourly: No processed data available")

            self.lastprocessed_time = target_datetime
            self.logger.debug("ReportProcessor.process_hourly: Method completed successfully")
            return processed_data

        except Exception as e:
            self.logger.error(f'Error in hourly processing for {hour_str}: {e}', exc_info=True)
            self.logger.debug("ReportProcessor.process_hourly: Method completed with error")
            return {}

    def generate_on_demand_report(self, date_str: str, report_types: Optional[List[str]] = None) -> str:
        """
        Generate an on - demand report for a specific date.

        Args:
            date_str: Date in YYYY - MM - DD format
            report_types: Specific report types to include (None for all)

        Returns:
            Path to generated report file
        """
        self.logger.debug("ReportProcessor.generate_on_demand_report: Starting method")
        self.logger.info(f'Generating on - demand report for {date_str}')
        self.logger.debug(f"ReportProcessor.generate_on_demand_report: Report types: {report_types}")

        try:
            # Get data from the database for the date (temporarily disabled for demo)
            # dailydata = self.report_generator.get_daily_report(date_str, report_types)
            dailydata = None  # Database reporting disabled
            self.logger.debug("ReportProcessor.generate_on_demand_report: Database querying skipped (disabled for demo)")

            if not daily_data:
                self.logger.warning(f'No data available for on - demand report: {date_str}')
                self.logger.debug("ReportProcessor.generate_on_demand_report: Method completed - no data")
                return None

            # Generate report with timestamp
            timestamp = datetime.now().strftime('%H%M%S')
            reportfilename = f'ondemand_{date_str}_{timestamp}.xlsx'
            self.logger.debug(f"ReportProcessor.generate_on_demand_report: Generating report file: {report_filename}")
            reportpath = self.excel_writer.write_custom(daily_data, report_filename)

            self.logger.info(f'On - demand report generated: {report_path}')
            self.logger.debug("ReportProcessor.generate_on_demand_report: Method completed successfully")
            return report_path

        except Exception as e:
            self.logger.error(f'Error generating on - demand report for {date_str}: {e}', exc_info=True)
            self.logger.debug("ReportProcessor.generate_on_demand_report: Method completed with error")
            return None

    def generate_end_of_day_summary(self, date_str: str) -> str:
        """
        Generate comprehensive end - of - day summary report.

        Args:
            date_str: Date in YYYY - MM - DD format

        Returns:
            Path to generated summary report
        """
        self.logger.debug("ReportProcessor.generate_end_of_day_summary: Starting method")
        self.logger.info(f'Generating end - of - day summary for {date_str}')

        try:
            # Get data from the database for the date (temporarily disabled for demo)
            # dailydata = self.report_generator.get_daily_report(date_str)
            dailydata = None  # Database reporting disabled
            self.logger.debug("ReportProcessor.generate_end_of_day_summary: Database querying skipped (disabled for demo)")

            if not daily_data:
                self.logger.warning(f'No data available for end - of - day summary: {date_str}')
                self.logger.debug("ReportProcessor.generate_end_of_day_summary: Method completed - no data")
                return None

            # Get summary statistics from database (temporarily disabled for demo)
            # summarydf = self.report_generator.get_summary_statistics(date_str)
            summary_df = None  # Database reporting disabled
            self.logger.debug("ReportProcessor.generate_end_of_day_summary: Summary statistics generation skipped (disabled for demo)")

            # Add to the report data
            enhanced_data = daily_data.copy()
            enhanced_data['Report_Summary'] = [summary_df]

            # Add metadata sheet
            import pandas as pd
            self.logger.debug("ReportProcessor.generate_end_of_day_summary: Creating metadata sheet")
            metadata = pd.DataFrame({
                'Metric': ['Report Date', 'Generated At', 'Total Sheets', 'Total Records'],
                'Value': [
                    date_str,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    len(daily_data),
                    sum(len(df_list[0]) for df_list in daily_data.values())
                ]
            })
            enhanced_data['Report_Metadata'] = [metadata]

            # Generate comprehensive report
            summaryfilename = f'eod_summary_{date_str}.xlsx'
            self.logger.debug(f"ReportProcessor.generate_end_of_day_summary: Generating summary file: {summary_filename}")
            reportpath = self.excel_writer.write_summary(enhanced_data, summary_filename)

            # Clear daily cache after successful summary (for backward compatibility)
            if date_str in self.daily_data_cache:
                del self.daily_data_cache[date_str]
                self.logger.debug("ReportProcessor.generate_end_of_day_summary: Cleared daily cache for date")

            self.logger.info(f'End - of - day summary generated: {report_path}')
            return report_path

        except Exception as e:
            self.logger.error(f'Error generating end - of - day summary for {date_str}: {e}', exc_info=True)
            return None

    def run_continuous_processing(self, check_interval: int = 300):
        """
        Run continuous hourly processing (for production deployment).

        Args:
            check_interval: Seconds between checks for new hour (default: 5 minutes)
        """
        self.logger.info('Starting continuous processing mode')

        while True:
            try:
                currenttime = datetime.now().replace(minute=0, second=0, microsecond=0)

                # Process if we haven't processed this hour yet
                if self.last_processed_time is None or current_time > self.last_processed_time:
                    self.process_hourly(current_time)

                # Sleep until next check
                time.sleep(check_interval)

            except KeyboardInterrupt:
                self.logger.info('Continuous processing stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error in continuous processing: {e}', exc_info=True)
                time.sleep(check_interval)

    def update_daily_cache(self, date_str: str, new_data: Dict):
        """Update the daily data cache with new hourly data (for backward compatibility)."""
        if date_str not in self.daily_data_cache:
            self.daily_data_cache[date_str] = {}

        for sheet_name, df_list in new_data.items():
            if sheet_name not in self.daily_data_cache[date_str]:
                self.daily_data_cache[date_str][sheet_name] = []
            self.daily_data_cache[date_str][sheet_name].extend(df_list)


def main():
    parser = argparse.ArgumentParser(description="Real - time Contact Center Report Automation")
    parser.add_argument(
        '--config', type=str,
        help='Path to config file (default: ./config / config.toml, then ../config / config.toml)'
    )
    parser.add_argument(
        '--mode', type=str, choices=['hourly', 'ondemand', 'eod', 'continuous'],
        default='hourly',
        help='Processing mode: hourly, ondemand, eod (end - of - day), continuous'
    )
    parser.add_argument(
        '--date', type=str,
        default=datetime.today().strftime('%Y-%m-%d'),
        help='Date to process in YYYY - MM - DD format (default: today)'
    )
    parser.add_argument(
        '--hour', type=int, choices=range(0, 24),
        help='Specific hour to process (0 - 23), only for hourly mode'
    )
    parser.add_argument(
        '--report - types', type=str, nargs='+',
        help='Specific report types for on - demand reports'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Determine config path with fallback logic
    configpath = None
    if args.config:
        # User specified a config path
        configpath = Path(args.config)
        if not config_path.exists():
            print(f"❌ Specified config file not found: {config_path}")
            sys.exit(1)
    else:
        # Try default locations in priority order
        currentdir = Path.cwd()
        srcdir = Path(__file__).parent

        defaultpaths = [
            current_dir / 'config.toml',                    # ./config.toml (demo directory)
            current_dir / 'config' / 'config.toml',        # ./config / config.toml (main project)
            current_dir.parent / 'config' / 'config.toml',  # ../config / config.toml
            src_dir.parent / 'config' / 'config.toml',     # src/../config / config.toml
        ]

        for path in default_paths:
            if path.exists():
                configpath = path
                break

        if not config_path:
            print("❌ No config file found. Tried:")
            for path in default_paths:
                print(f"   - {path}")
            print("\nUse --config to specify a custom config file location.")
            sys.exit(1)

    print(f"📁 Using config: {config_path}")

    # Setup logging for main function
    mainlogger = LoggerFactory.get_logger('main', 'main.log')
    main_logger.debug("main: Starting main function")
    main_logger.debug(f"main: config_path={config_path}")
    main_logger.debug(f"main: args={args}")

    # Load configuration from TOML
    main_logger.debug("main: Creating ConfigLoader instance")
    cfg = ConfigLoader(config_path)

    # Initialize processor
    main_logger.debug("main: Creating ReportProcessor instance")
    processor = ReportProcessor(cfg, debug=args.debug)

    # Execute based on mode
    main_logger.debug(f"main: Executing mode: {args.mode}")
    if args.mode == 'hourly':
        main_logger.debug("main: Processing hourly mode")
        targetdatetime = None
        if args.hour is not None:
            targetdate = datetime.strptime(args.date, '%Y-%m-%d')
            targetdatetime = target_date.replace(hour=args.hour, minute=0, second=0, microsecond=0)
            main_logger.debug(f"main: target_datetime set to {target_datetime}")
        else:
            main_logger.debug("main: No specific hour specified, using current hour")

        result = processor.process_hourly(target_datetime)
        if result:
            print(f"Hourly processing completed: {len(result)} datasets processed")
        else:
            print("No new data processed")

    elif args.mode == 'ondemand':
        reportpath = processor.generate_on_demand_report(args.date, args.report_types)
        if report_path:
            print(f"On - demand report generated: {report_path}")
        else:
            print("Failed to generate on - demand report")

    elif args.mode == 'eod':
        summarypath = processor.generate_end_of_day_summary(args.date)
        if summary_path:
            print(f"End - of - day summary generated: {summary_path}")
        else:
            print("Failed to generate end - of - day summary")

    elif args.mode == 'continuous':
        print("Starting continuous processing mode (Ctrl + C to stop)")
        processor.run_continuous_processing()


if __name__ == "__main__":
    main()