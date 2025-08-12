"""
Shared Base Service Framework
Base classes and utilities shared across all microservices
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import signal
import structlog
import uvloop
from datetime import datetime
import os


class BaseService(ABC):
    """
    Base class for all Charlie Reporting microservices.

    Provides:
    - Standardized startup / shutdown lifecycle
    - Signal handling for graceful shutdown
    - Infrastructure initialization
    - Health monitoring
    - Structured logging
    """

    def __init__(self, name: str, config: Any):
        self.name = name
        self.config = config
        self.logger = structlog.get_logger(service=name)
        self.running = False
        self.healthstatus = "starting"

        # Infrastructure components (initialized by subclasses)
        self.metrics = None
        self.database = None
        self.messageclient = None
        self.apiserver = None

        # Internal state
        self.shutdown_event = asyncio.Event()
        self.tasks: List[asyncio.Task] = []

    async def start(self):
        """Start the service with full lifecycle management"""
        try:
            self.logger.info("Starting service", service=self.name, version=self.config.service_version)

            # 1. Initialize infrastructure layer
            await self.initialize_infrastructure()

            # 2. Initialize business layer
            await self.initialize_business_logic()

            # 3. Initialize interface layer (APIs, event handlers)
            await self.initialize_interfaces()

            # 4. Setup graceful shutdown
            self.setup_signal_handlers()

            # 5. Start background tasks
            await self.start_background_tasks()

            self.running = True
            self.healthstatus = "healthy"

            self.logger.info(
                "Service started successfully",
                service=self.name,
                port=getattr(self.config, 'port', None),
                health_status=self.health_status
            )

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.logger.error("Failed to start service", service=self.name, error=str(e), exc_info=True)
            self.healthstatus = "failed"
            raise

    async def stop(self):
        """Stop the service gracefully"""
        if not self.running:
            return

        self.logger.info("Stopping service", service=self.name)
        self.running = False
        self.healthstatus = "stopping"

        try:
            # 1. Stop accepting new requests
            await self.stop_interfaces()

            # 2. Cancel background tasks
            await self.stop_background_tasks()

            # 3. Stop business logic
            await self.stop_business_logic()

            # 4. Cleanup infrastructure
            await self.cleanup_infrastructure()

            self.healthstatus = "stopped"
            self.logger.info("Service stopped gracefully", service=self.name)

        except Exception as e:
            self.logger.error("Error during service shutdown", service=self.name, error=str(e), exc_info=True)
            self.healthstatus = "error"
        finally:
            self.shutdown_event.set()

    # Abstract methods - must be implemented by each service
    @abstractmethod
    async def initialize_infrastructure(self):
        """Initialize infrastructure components (metrics, database, messaging)"""
        pass

    @abstractmethod
    async def initialize_business_logic(self):
        """Initialize business logic components"""
        pass

    @abstractmethod
    async def initialize_interfaces(self):
        """Initialize interface components (REST API, event handlers)"""
        pass

    @abstractmethod
    async def start_background_tasks(self):
        """Start background tasks (schedulers, workers, etc.)"""
        pass

    @abstractmethod
    async def stop_interfaces(self):
        """Stop interface components"""
        pass

    @abstractmethod
    async def stop_background_tasks(self):
        """Stop background tasks"""
        pass

    @abstractmethod
    async def stop_business_logic(self):
        """Stop business logic components"""
        pass

    @abstractmethod
    async def cleanup_infrastructure(self):
        """Cleanup infrastructure components"""
        pass

    # Helper methods
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info("Received shutdown signal", signal=signum, service=self.name)
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def add_background_task(self, coro):
        """Add a background task to be managed by the service"""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task

    async def cancel_tasks(self):
        """Cancel all background tasks"""
        for task in self.tasks:
            if not task.done():
                task.cancel()

        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            "service": self.name,
            "version": self.config.service_version,
            "status": self.health_status,
            "running": self.running,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self.get_uptime(),
            "dependencies": self.check_dependencies()
        }

    def get_uptime(self) -> Optional[float]:
        """Get service uptime in seconds"""
        # This would be implemented with start time tracking
        return None

    def check_dependencies(self) -> Dict[str, Any]:
        """Check health of service dependencies"""
        dependencies = {}

        if self.database:
            dependencies["database"] = {"status": "healthy"}  # Implement actual check

        if self.message_client:
            dependencies["messaging"] = {"status": "healthy"}  # Implement actual check

        return dependencies


class ServiceRunner:
    """
    Utility class to run services with proper async event loop setup
    """

    @staticmethod
    def run(service: BaseService):
        """Run a service with optimized event loop"""
        try:
            # Use uvloop for better performance on Unix systems
            if os.name != 'nt':  # Not Windows
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

            # Run the service
            asyncio.run(service.start())

        except KeyboardInterrupt:
            print(f"\n{service.name} interrupted by user")
        except Exception as e:
            print(f"Failed to run {service.name}: {e}")
            raise


class ServiceManager:
    """
    Manages multiple services for local development (Windows batch file scenario)
    """

    def __init__(self):
        self.services: Dict[str, BaseService] = {}
        self.running = False

    def add_service(self, service: BaseService):
        """Add a service to be managed"""
        self.services[service.name] = service

    async def start_all(self):
        """Start all services concurrently"""
        self.running = True

        # Start all services as background tasks
        tasks = [
            asyncio.create_task(service.start())
            for service in self.services.values()
        ]

        try:
            # Wait for all services to complete (or shutdown)
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in service manager: {e}")
        finally:
            self.running = False

    async def stop_all(self):
        """Stop all services gracefully"""
        self.running = False

        # Send stop signal to all services
        stoptasks = [
            asyncio.create_task(service.stop())
            for service in self.services.values()
        ]

        # Wait for all services to stop
        await asyncio.gather(*stop_tasks, return_exceptions=True)


# Service lifecycle states


class ServiceState:
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    ERROR = "error"