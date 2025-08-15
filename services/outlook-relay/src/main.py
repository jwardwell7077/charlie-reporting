"""
Outlook-Relay Service - Main Entry Point
Email proxy for Outlook/Exchange operations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config.settings import load_config

try:
    from shared.base_service import BaseService
    from shared.logging import setup_service_logging
    from shared.metrics import ServiceMetrics
    from shared.health import HealthMonitor
except ImportError:
    # Fallback implementations
    class BaseService:
        def __init__(self, *args, **kwargs): pass
        async def startup(self): pass
        async def shutdown(self): pass
        async def run(self): pass
    
    def setup_service_logging(name, level=None):
        import logging
        return logging.getLogger(name)
    
    class ServiceMetrics:
        def __init__(self, name): pass
    
    class HealthMonitor:
        def __init__(self, name): pass

class OutlookrelayService(BaseService):
    """
    Outlook-Relay Service
    Email proxy for Outlook/Exchange operations
    """
    
    def __init__(self):
        self.config = load_config()
        
        self.logger = setup_service_logging(
            self.config.service_name,
            self.config.log_level if hasattr(self.config, 'log_level') else 'INFO'
        )
        
        self.metrics = ServiceMetrics(self.config.service_name)
        self.health_monitor = HealthMonitor(self.config.service_name)
        
        super().__init__(self.logger, self.metrics, self.health_monitor)
    
    async def startup(self):
        """Service startup logic"""
        self.logger.info("Starting Outlook-Relay Service", version="1.0.0")
        
        # TODO: Initialize service-specific components
        
        self.logger.info(
            "Outlook-Relay Service started successfully",
            port=self.config.service_port
        )
    
    async def shutdown(self):
        """Service shutdown logic"""
        self.logger.info("Shutting down Outlook-Relay Service")
        
        # TODO: Cleanup service-specific components

async def main():
    """Main entry point"""
    service = OutlookrelayService()
    
    try:
        await service.startup()
        await service.run()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    except Exception as e:
        print(f"Service error: {e}")
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
