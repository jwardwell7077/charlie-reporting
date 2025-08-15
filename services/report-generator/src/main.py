"""Main application entry point.

Initializes and runs the Report Generator Service.
"""

import os  # noqa: I001
import sys
from pathlib import Path
from typing import Any

import uvicorn

from infrastructure.config import get_config_manager
from infrastructure.logging import get_logger, initialize_logging
from interface.app import app

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))


def create_directories(config: Any) -> None:  # noqa: ANN401 - dynamic config object
    """Create necessary directories if they don't exist.

    The concrete config object originates from application configuration manager
    and supplies directory paths as string-like values.
    """
    directories: list[str | Path | None] = [
        getattr(config, "default_raw_directory", None),
        getattr(config, "default_archive_directory", None),
        getattr(config, "default_output_directory", None),
        getattr(config, "temp_directory", None),
    ]

    for directory in directories:
        if directory:
            Path(str(directory)).mkdir(parents=True, exist_ok=True)


def setup_application() -> Any:  # noqa: ANN401 - dynamic config object
    """Setup application with configuration and logging."""
    # Load configuration
    config_file = os.environ.get("REPORT_GENERATOR_CONFIG_FILE")
    config_manager = get_config_manager(config_file)
    config = config_manager.get_config()

    # Initialize logging
    logging_config = config_manager.get_logging_config()
    initialize_logging(
        service_name="report-generator",
        log_level=logging_config["log_level"],
        log_file=logging_config["log_file"],
        enable_console=logging_config["enable_console_logging"],
    )

    # Create necessary directories
    create_directories(config)

    return config


def main() -> None:
    """Main application entry point."""
    try:
        # Setup application
        _config = setup_application()

        # Get server configuration
        server_config = get_config_manager().get_server_config()

        # Run the application
        uvicorn.run(
            app,
            host=server_config["host"],
            port=server_config["port"],
            reload=server_config.get("reload", False),
            log_level="info",
            access_log=True,
        )

    except Exception as e:  # noqa: BLE001
        logger = get_logger("startup")
        logger.log_exception(e, operation="startup")
        sys.exit(1)


if __name__ == "__main__":
    main()
