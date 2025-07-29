#!/usr/bin/env python3
"""
Application Entry Point
Migrated to use new microservices architecture
"""
import asyncio
import sys
from pathlib import Path

# Add service paths
services_path = Path(__file__).parent / 'services'
sys.path.append(str(services_path / 'report-generator'))
sys.path.append(str(services_path / 'email-service'))
sys.path.append(str(Path(__file__).parent / 'shared'))

from csv_processor import CSVProcessor
from excel_generator import ExcelGenerator
from email_processor import EmailProcessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point using new services."""
    try:
        logger.info("Starting application with new microservices architecture")
        
        # Initialize services
        csv_processor = CSVProcessor()
        excel_generator = ExcelGenerator()
        email_processor = EmailProcessor()
        
        # Example workflow
        logger.info("Services initialized successfully")
        logger.info("Use FastAPI service at: uvicorn services.report-generator.main:app --reload")
        logger.info("Or import and use services directly")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
