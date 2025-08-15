"""Database Service entrypoint (packaged)."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from .config.settings import load_config  # type: ignore

try:
    from shared.base_service import BaseService  # type: ignore
    from shared.health import HealthMonitor  # type: ignore
    from shared.metrics import ServiceMetrics  # type: ignore
    from shared.service_logging import setup_service_logging  # type: ignore
except Exception:  # pragma: no cover
    class BaseService:  # type: ignore
        def __init__(self, *_: Any, **__: Any) -> None: ...
        async def startup(self) -> None: ...
        async def shutdown(self) -> None: ...
        async def run(self) -> None: await asyncio.sleep(0.01)

    # fallback minimal logger
    def setup_service_logging(name: str, level: str | None = None) -> logging.Logger:  # type: ignore
        logging.basicConfig(level=level or "INFO")
        return logging.getLogger(name)

    class ServiceMetrics:  # type: ignore
        def __init__(self, *_: Any, **__: Any) -> None: self._counters: dict[str,int] = {}
    class HealthMonitor:  # type: ignore
        def __init__(self, *_: Any, **__: Any) -> None: self.status = "healthy"


class DatabaseService(BaseService):  # type: ignore[misc]
    def __init__(self) -> None:
        self.config = load_config()
        self.logger = setup_service_logging(
            getattr(self.config, "service_name", "database-service"),
            getattr(self.config, "log_level", "INFO"),
        )
        self.metrics = ServiceMetrics(self.config.service_name)  # type: ignore[arg-type]
        self.health_monitor = HealthMonitor(self.config.service_name)  # type: ignore[arg-type]
        super().__init__(self.logger, self.metrics, self.health_monitor)  # type: ignore[arg-type]

    async def startup(self) -> None:  # type: ignore[override]
        self.logger.info("Starting database-service v1.0.0")
        self.logger.info("database-service started on port %s", getattr(self.config, "service_port", "?"))

    async def shutdown(self) -> None:  # type: ignore[override]
        self.logger.info("Shutting down database-service")

    async def run(self) -> None:  # type: ignore[override]
        await asyncio.sleep(0.01)


async def _async_main() -> int:
    service = DatabaseService()
    try:
        await service.startup()
        await service.run()
    except KeyboardInterrupt:  # pragma: no cover
        service.logger.info("Interrupt signal received")
    except Exception:  # pragma: no cover
        service.logger.exception("Service error")
        return 1
    finally:
        await service.shutdown()
    return 0


def main() -> int:  # console_script entry
    return asyncio.run(_async_main())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
