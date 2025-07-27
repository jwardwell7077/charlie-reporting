
"""
main.py
-------
Entry point for the real-time reporting ETL pipeline. Supports hourly incremental processing,
on-demand reports, and end-of-day summaries for contact center data.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import sys
import os
import argparse
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config_loader import ConfigLoader
from email_fetcher import EmailFetcher
from transformer import CSVTransformer
from excel_writer import ExcelWriter
from logger import LoggerFactory


class ReportProcessor:
    """
    Handles real-time incremental processing of contact center reports.
    Supports hourly processing, incremental Excel updates, and on-demand reporting.
    """
    
    def __init__(self, config: ConfigLoader, debug: bool = False):
        self.config = config
        self.logger = LoggerFactory.get_logger('report_processor', log_file='main.log')
        
        if debug:
            self.logger.setLevel('DEBUG')
            for handler in self.logger.handlers:
                handler.setLevel('DEBUG')
        
        # Initialize components
        self.email_fetcher = EmailFetcher(config)
        self.transformer = CSVTransformer(config)
        self.excel_writer = ExcelWriter()
        
        # Track processing state
        self.last_processed_time = None
        self.daily_data_cache = {}
        
    def process_hourly(self, target_datetime: Optional[datetime] = None) -> Dict:
        """
        Process emails for a specific hour and update Excel incrementally.
        
        Args:
            target_datetime: Specific datetime to process (defaults to current hour)
            
        Returns:
            Dict containing processed data for the hour
        """
        if target_datetime is None:
            target_datetime = datetime.now().replace(minute=0, second=0, microsecond=0)
        else:
            # Normalize to hour boundary
            target_datetime = target_datetime.replace(minute=0, second=0, microsecond=0)
            
        hour_str = target_datetime.strftime('%Y-%m-%d_%H')
        date_str = target_datetime.strftime('%Y-%m-%d')
        
        self.logger.info(f'Starting hourly processing for: {hour_str}')
        
        try:
            # Fetch emails for this specific hour
            self.email_fetcher.fetch(date_str)
            
            # Transform any new CSVs
            report_data = self.transformer.transform(date_str)
            
            if report_data:
                # Update daily cache
                self._update_daily_cache(date_str, report_data)
                
                # Write incremental Excel update
                self.excel_writer.write_incremental(report_data, date_str, hour_str)
                
                self.logger.info(f'Hourly processing completed for {hour_str}: {len(report_data)} datasets processed')
            else:
                self.logger.info(f'No new data found for {hour_str}')
                
            self.last_processed_time = target_datetime
            return report_data
            
        except Exception as e:
            self.logger.error(f'Error in hourly processing for {hour_str}: {e}', exc_info=True)
            return {}
    
    def generate_on_demand_report(self, date_str: str, report_types: Optional[List[str]] = None) -> str:
        """
        Generate an on-demand report for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            report_types: Specific report types to include (None for all)
            
        Returns:
            Path to generated report file
        """
        self.logger.info(f'Generating on-demand report for {date_str}')
        
        try:
            # Get all data for the date (from cache or by reprocessing)
            daily_data = self._get_daily_data(date_str)
            
            if not daily_data:
                self.logger.warning(f'No data available for on-demand report: {date_str}')
                return None
                
            # Filter by report types if specified
            if report_types:
                daily_data = {k: v for k, v in daily_data.items() if k in report_types}
            
            # Generate report with timestamp
            timestamp = datetime.now().strftime('%H%M%S')
            report_filename = f'ondemand_{date_str}_{timestamp}.xlsx'
            report_path = self.excel_writer.write_custom(daily_data, report_filename)
            
            self.logger.info(f'On-demand report generated: {report_path}')
            return report_path
            
        except Exception as e:
            self.logger.error(f'Error generating on-demand report for {date_str}: {e}', exc_info=True)
            return None
    
    def generate_end_of_day_summary(self, date_str: str) -> str:
        """
        Generate comprehensive end-of-day summary report.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Path to generated summary report
        """
        self.logger.info(f'Generating end-of-day summary for {date_str}')
        
        try:
            # Get complete daily data
            daily_data = self._get_daily_data(date_str)
            
            if not daily_data:
                self.logger.warning(f'No data available for end-of-day summary: {date_str}')
                return None
            
            # Add summary statistics and metadata
            enhanced_data = self._add_summary_statistics(daily_data, date_str)
            
            # Generate comprehensive report
            summary_filename = f'eod_summary_{date_str}.xlsx'
            report_path = self.excel_writer.write_summary(enhanced_data, summary_filename)
            
            # Clear daily cache after successful summary
            if date_str in self.daily_data_cache:
                del self.daily_data_cache[date_str]
            
            self.logger.info(f'End-of-day summary generated: {report_path}')
            return report_path
            
        except Exception as e:
            self.logger.error(f'Error generating end-of-day summary for {date_str}: {e}', exc_info=True)
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
                current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
                
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
    
    def _update_daily_cache(self, date_str: str, new_data: Dict):
        """Update the daily data cache with new hourly data."""
        if date_str not in self.daily_data_cache:
            self.daily_data_cache[date_str] = {}
        
        for sheet_name, df_list in new_data.items():
            if sheet_name not in self.daily_data_cache[date_str]:
                self.daily_data_cache[date_str][sheet_name] = []
            self.daily_data_cache[date_str][sheet_name].extend(df_list)
    
    def _get_daily_data(self, date_str: str) -> Dict:
        """Get all data for a date, from cache or by reprocessing."""
        if date_str in self.daily_data_cache:
            return self.daily_data_cache[date_str]
        
        # If not in cache, try to reprocess from archived files
        self.logger.info(f'Reprocessing data for {date_str} from archives')
        return self.transformer.transform(date_str)
    
    def _add_summary_statistics(self, daily_data: Dict, date_str: str) -> Dict:
        """Add summary statistics and metadata to daily data."""
        enhanced_data = daily_data.copy()
        
        # Add metadata sheet
        import pandas as pd
        metadata = pd.DataFrame({
            'Metric': ['Report Date', 'Generated At', 'Total Sheets', 'Total Records'],
            'Value': [
                date_str,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                len(daily_data),
                sum(len(df_list) for df_list in daily_data.values())
            ]
        })
        enhanced_data['Report_Metadata'] = [metadata]
        
        return enhanced_data


def main():
    parser = argparse.ArgumentParser(description="Real-time Contact Center Report Automation")
    parser.add_argument(
        '--mode', type=str, choices=['hourly', 'ondemand', 'eod', 'continuous'],
        default='hourly',
        help='Processing mode: hourly, ondemand, eod (end-of-day), continuous'
    )
    parser.add_argument(
        '--date', type=str,
        default=datetime.today().strftime('%Y-%m-%d'),
        help='Date to process in YYYY-MM-DD format (default: today)'
    )
    parser.add_argument(
        '--hour', type=int, choices=range(0, 24),
        help='Specific hour to process (0-23), only for hourly mode'
    )
    parser.add_argument(
        '--report-types', type=str, nargs='+',
        help='Specific report types for on-demand reports'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()

    # Load configuration from TOML
    config_path = os.path.join(os.getcwd(), 'config', 'config.toml')
    cfg = ConfigLoader(config_path)
    
    # Initialize processor
    processor = ReportProcessor(cfg, debug=args.debug)
    
    # Execute based on mode
    if args.mode == 'hourly':
        target_datetime = None
        if args.hour is not None:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
            target_datetime = target_date.replace(hour=args.hour, minute=0, second=0, microsecond=0)
        
        result = processor.process_hourly(target_datetime)
        if result:
            print(f"Hourly processing completed: {len(result)} datasets processed")
        else:
            print("No new data processed")
            
    elif args.mode == 'ondemand':
        report_path = processor.generate_on_demand_report(args.date, args.report_types)
        if report_path:
            print(f"On-demand report generated: {report_path}")
        else:
            print("Failed to generate on-demand report")
            
    elif args.mode == 'eod':
        summary_path = processor.generate_end_of_day_summary(args.date)
        if summary_path:
            print(f"End-of-day summary generated: {summary_path}")
        else:
            print("Failed to generate end-of-day summary")
            
    elif args.mode == 'continuous':
        print("Starting continuous processing mode (Ctrl+C to stop)")
        processor.run_continuous_processing()


if __name__ == "__main__":
    main()
