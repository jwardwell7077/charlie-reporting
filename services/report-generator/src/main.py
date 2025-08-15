"""Main Application Entry Point
Initializes and runs the Report Generator Service
"""

import os
import sys
from pathlib import Path

import uvicorn
from infrastructure.config import get_config_manager
from infrastructure.logging import initialize_logging
from interface.app import app

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))


def create_directories(config):
    """Create necessary directories if they don't exist"""
    directories = [
        config.default_raw_directory,
        config.default_archive_directory,
        config.default_output_directory,
        config.temp_directory
    ]

    for directory in directories:
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)


def setup_application():
    """Setup application with configuration and logging"""
    # Load configuration
    config_file = os.environ.get('REPORT_GENERATOR_CONFIG_FILE')
    config_manager = get_config_manager(config_file)
    config = config_manager.get_config()

    # Initialize logging
    logging_config = config_manager.get_logging_config()
    initialize_logging(
        service_name="report - generator",
        log_level=logging_config["log_level"],
        log_file=logging_config["log_file"],
        enable_console=logging_config["enable_console_logging"]
    )

    # Create necessary directories
    create_directories(config)

    return config


def main():
    """Main application entry point"""
    try:
        # Setup application
        config = setup_application()

        # Get server configuration
        server_config = get_config_manager().get_server_config()

        # Run the application
        uvicorn.run(
            app,
            host=server_config["host"],
            port=server_config["port"],
            reload=server_config.get("reload", False),
            log_level="info",
            access_log=True
        )

    except Exception as e:
        print(f"Failed to start Report Generator Service: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
