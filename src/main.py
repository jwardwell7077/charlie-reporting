import argparse
from datetime import datetime

from logger import LoggerFactory
from config_loader import ConfigLoader
from email_fetcher import EmailFetcher
from transformer import CSVTransformer
from excel_writer import ExcelWriter


def main():
    parser = argparse.ArgumentParser(description="Daily Report Automation")
    parser.add_argument(
        '--date', type=str,
        default=datetime.today().strftime('%Y-%m-%d'),
        help='Date to process in YYYY-MM-DD format (default: today)'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debug logging'
    )
    args = parser.parse_args()
    date_str = args.date

    # Initialize logger for main
    logger = LoggerFactory.get_logger('main', log_file='main.log')
    if args.debug:
        logger.setLevel('DEBUG')
        for handler in logger.handlers:
            handler.setLevel('DEBUG')
        logger.debug('Debug logging enabled')

    logger.info(f'Running report pipeline for date: {date_str}')

    # Load configuration from TOML
    cfg = ConfigLoader(os.path.join(os.getcwd(), 'config', 'config.toml'))

    # Fetch emails and save CSVs
    fetcher = EmailFetcher(cfg)
    fetcher.fetch(date_str)

    # Transform CSVs to DataFrames
    transformer = CSVTransformer(cfg)
    report_data = transformer.transform(date_str)

    # Write to Excel
    writer = ExcelWriter()
    writer.write(report_data, date_str)

    logger.info('Workflow completed.')


if __name__ == '__main__':
    import os
    main()
