import os
import logging
from logging.handlers import TimedRotatingFileHandler


class LoggerFactory:
    """
    LoggerFactory configures and returns loggers with both console and rotating file handlers.
    """
    LOG_DIR = os.path.join(os.getcwd(), 'logs')

    @staticmethod
    def get_logger(name: str, log_file: str = 'app.log') -> logging.Logger:
        # Ensure log directory exists
        os.makedirs(LoggerFactory.LOG_DIR, exist_ok=True)

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers if already configured
        if logger.handlers:
            return logger

        # Log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handler: rotate logs weekly, keep 4 backups
        file_path = os.path.join(LoggerFactory.LOG_DIR, log_file)
        file_handler = TimedRotatingFileHandler(
            file_path, when='W0', interval=1, backupCount=4
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger
