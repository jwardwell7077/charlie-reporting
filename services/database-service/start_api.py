#!/usr/bin/env python3
"""Startup script for the Database Service API
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add database service to path
db_service_path = Path(__file__).parent
sys.path.insert(0, str(db_service_path))


def main():
    """Start the FastAPI server"""
    logger = logging.getLogger("database_service.startup")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
    try:
        import uvicorn

        from src.interfaces.rest.main import create_app

        # Create the FastAPI app
        app = create_app()

        logger.info("🚀 Starting Database Service API...")
        logger.info("📖 API Documentation: http://localhost:8000/docs")
        logger.info("🏥 Health Check: http://localhost:8000/health")
        logger.info("⏹️  Press Ctrl+C to stop")

        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to True for development
            log_level="info",
        )

    except KeyboardInterrupt:  # pragma: no cover - interactive use
        logger.info("👋 API server stopped")
    except Exception:  # pragma: no cover - startup failure path
        logger.exception("❌ Failed to start API server")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
