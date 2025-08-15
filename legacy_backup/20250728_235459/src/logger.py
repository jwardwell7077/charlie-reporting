import logging
import os
from logging.handlers import TimedRotatingFileHandler


class LoggerFactory:
    """LoggerFactory configures and returns loggers with both console and rotating file handlers.
    """
    LOGDIR = os.path.join(os.getcwd(), 'logs')

    @staticmethod
    def get_logger(name: str, log_file: str = 'app.log') -> logging.Logger:
        # Ensure log directory exists
        os.makedirs(LoggerFactory.LOG_DIR, exist_ok=True)

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels

        # Prevent adding multiple handlers if already configured
        if logger.handlers:
            return logger

        # Log format with module, class, and method information
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s'
        )

        # File handler: rotate logs weekly, keep 4 backups
        filepath = os.path.join(LoggerFactory.LOG_DIR, log_file)
        filehandler = TimedRotatingFileHandler(
            file_path, when='W0', interval=1, backupCount=4
        )
        file_handler.setLevel(logging.DEBUG)  # Set file handler to DEBUG
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        consolehandler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Keep console at INFO level for readability
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger