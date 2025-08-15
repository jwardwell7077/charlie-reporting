"""Main entry point for Outlook Relay service (packaged)."""
from __future__ import annotations

import asyncio

from config.settings import load_config  # type: ignore

try:
    from shared.base_service import BaseService  # type: ignore
    from shared.health import HealthMonitor  # type: ignore
    from shared.metrics import ServiceMetrics  # type: ignore
    from shared.service_logging import setup_service_logging  # unified logger
except ImportError:  # pragma: no cover

    class BaseService:  # type: ignore
        def __init__(self, *_: object, **__: object) -> None: ...
        async def startup(self) -> None: ...  # pragma: no cover
        async def shutdown(self) -> None: ...  # pragma: no cover
        async def run(self) -> None:  # pragma: no cover
            await asyncio.sleep(0.01)

     # local fallback removed; rely on shared.logging

    class ServiceMetrics:  # type: ignore
        def __init__(self, name: str) -> None: self.name = name

    class HealthMonitor:  # type: ignore
        def __init__(self, name: str) -> None: self.name = name


class OutlookRelayService(BaseService):
    """Outlook Relay Service core container."""
    def __init__(self) -> None:
        self.config = load_config()
        self.logger = setup_service_logging(
            getattr(self.config, "service_name", "outlook-relay"),
            getattr(self.config, "log_level", "INFO"),
        )
        self.metrics = ServiceMetrics(getattr(self.config, "service_name", "outlook-relay"))
        self.health_monitor = HealthMonitor(getattr(self.config, "service_name", "outlook-relay"))
        super().__init__(self.logger, self.metrics, self.health_monitor)  # type: ignore[arg-type]

    async def startup(self) -> None:  # type: ignore[override]
        self.logger.info("Starting Outlook Relay Service")
        self.logger.info("Config loaded: service_port=%s", getattr(self.config, "service_port", "n/a"))

    async def shutdown(self) -> None:  # type: ignore[override]
        self.logger.info("Shutting down Outlook Relay Service")


async def main() -> None:
    service = OutlookRelayService()
    try:
        await service.startup()
        await service.run()
    except KeyboardInterrupt:  # pragma: no cover
        service.logger.info("Interrupt received")
    except Exception:  # pragma: no cover
        service.logger.exception("Service error")
    finally:
        await service.shutdown()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
