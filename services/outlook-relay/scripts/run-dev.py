#!/usr/bin/env python3
"""Development runner for Outlook - Relay Service
"""

import asyncio
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Expect outlook_relay package to be installed/editable or discoverable via PYTHONPATH


def main() -> int:
    """Run the service in development mode"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("outlook_relay.dev")
    logger.info("Starting Outlook Relay (dev mode) via package entrypoint")
    try:
        from outlook_relay.main import main as service_main  # type: ignore
    except ImportError:
        logger.exception("Package outlook_relay not importable. Ensure editable install or PYTHONPATH set.")
        return 1
    try:
        asyncio.run(service_main())
        return 0
    except Exception:
        logger.exception("Service crashed")
        return 1


if __name__ == "__main__":
    sys.exit(main())