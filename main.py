import argparse
from datetime import datetime
from fetch_csv_emails import fetch_csv_emails
from transformer import transform_and_generate_excel
from logger import get_logger

logger = get_logger("main")

def main():
    parser = argparse.ArgumentParser(description="Daily Report Automation")
    parser.add_argument("--date", type=str, default=datetime.today().strftime('%Y-%m-%d'),
                        help="Date to process in YYYY-MM-DD format (default: today)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    date_str = args.date

    if args.debug:
        for handler in logger.handlers:
            handler.setLevel("DEBUG")
        logger.setLevel("DEBUG")
        logger.debug("Debug mode enabled")

    logger.info(f"Running report pipeline for date: {date_str}")
    fetch_csv_emails(date_str)
    transform_and_generate_excel()

    logger.info("Workflow complete.")

if __name__ == "__main__":
    main()
