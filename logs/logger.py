import os
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str, log_file: str = "fetch_csv.log") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # Prevent duplicate handlers if called more than once

    # Format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Rotating File Handler (weekly)
    file_handler = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, log_file),
        when="W0", interval=1, backupCount=4  # rotates weekly on Monday
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Stream Handler (console output)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
