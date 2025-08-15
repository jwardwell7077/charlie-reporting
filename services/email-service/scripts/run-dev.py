#!/usr/bin/env python3
"""Development runner for Email - Service Service
"""

import logging
import sys
from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

shared_dir = current_dir / "shared"
if shared_dir.exists():
    sys.path.insert(0, str(shared_dir))


def main() -> int:
    """Run the service in development mode"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("email_service.dev")
    logger.info("🚀 Starting Email-Service (Development Mode)")
    logger.info("%s", "=" * 50)

    if not shared_dir.exists():
        logger.warning("Shared components not found. Creating symlink...")
        try:
            shared_source = current_dir.parent.parent / "shared"
            if shared_source.exists():
                shared_dir.symlink_to(shared_source)
                logger.info("Created shared components symlink")
            else:
                logger.error("Shared components source not found")
                return 1
        except Exception:
            logger.exception("Failed to create symlink")
            return 1

    try:
        import asyncio

        from legacy_bridge import main as service_main  # type: ignore
        asyncio.run(service_main())
    except ImportError:
        logger.exception("Import error starting legacy bridge")
        return 1
    except Exception:
        logger.exception("Service error during dev run")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())