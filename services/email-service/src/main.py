"""Email - Service Service - Main Entry Point
Outbound email delivery and templates
"""

import asyncio
import os
import sys

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config.settings import load_config

try:
    from shared.base_service import BaseService  # type: ignore
    from shared.health import HealthMonitor  # type: ignore
    from shared.metrics import ServiceMetrics  # type: ignore
    from shared.service_logging import setup_service_logging  # unified logger
except ImportError:  # pragma: no cover - fallback minimal shims

    class BaseService:  # type: ignore
        def __init__(self, *_: object, **__: object) -> None:
            pass

        async def startup(self) -> None:  # pragma: no cover
            pass

        async def shutdown(self) -> None:  # pragma: no cover
            pass

        async def run(self) -> None:  # pragma: no cover
            await asyncio.sleep(0.01)

     # fallback removed; rely on shared.logging

    class ServiceMetrics:  # type: ignore
        def __init__(self, name: str) -> None:  # pragma: no cover
            self.name = name

    class HealthMonitor:  # type: ignore
        def __init__(self, name: str) -> None:  # pragma: no cover
            self.name = name


class EmailserviceService(BaseService):
    """Email - Service Service
    Outbound email delivery and templates
    """

    def __init__(self):
        self.config = load_config()

        self.logger = setup_service_logging(
            self.config.service_name,
            getattr(self.config, 'log_level', 'INFO')
        )
        # Remaining runtime components
        self.metrics = ServiceMetrics(self.config.service_name)
        self.health_monitor = HealthMonitor(self.config.service_name)
        super().__init__(self.logger, self.metrics, self.health_monitor)  # type: ignore[arg-type]

    async def startup(self) -> None:  # type: ignore[override]
        """Service startup logic"""
        self.logger.info("Starting Email-Service Service v1.0.0")
        # TODO: Initialize outbound email channels, templates, queues
        self.logger.info(
            "Email-Service Service started successfully on port %s",
            getattr(self.config, "service_port", "n/a"),
        )

    async def shutdown(self) -> None:  # type: ignore[override]
        """Service shutdown logic"""
        self.logger.info("Shutting down Email-Service Service")
        # TODO: Cleanup resources


async def main() -> None:
    """Main entry point"""
    service = EmailserviceService()
    try:
        await service.startup()
        await service.run()
    except KeyboardInterrupt:  # pragma: no cover
        service.logger.info("Received interrupt signal")
    except Exception:  # pragma: no cover
        service.logger.exception("Service error")
    finally:
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())