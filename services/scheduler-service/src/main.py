"""Scheduler Service entrypoint.

This file formerly contained ad-hoc fallback logging and partially generated
code that became corrupted. It is rewritten to use the unified structured
logging utility in ``shared.logging`` while keeping the service extremely
simple until full scheduler implementation is provided.
"""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass

try:  # Prefer the shared base & logging; fall back gracefully for isolation.
    from shared.base_service import BaseService  # type: ignore
    from shared.service_logging import setup_service_logging  # type: ignore
except Exception:  # noqa: BLE001
    class BaseService:  # minimal fallback
        def __init__(self, name: str, config):
            self.name = name
            self.config = config
        async def start(self):  # pragma: no cover - simple fallback
            pass
        async def stop(self):  # pragma: no cover
            pass
    def setup_service_logging(service_name: str, level=None, **initial):  # pragma: no cover
        import logging
        logging.basicConfig(level=level or "INFO")
        return logging.getLogger(service_name)


@dataclass(slots=True)
class SchedulerConfig:
    service_name: str = "scheduler-service"
    service_version: str = "0.1.0"
    log_level: str = "INFO"
    service_port: int = 0


class SchedulerService(BaseService):
    """Minimal Scheduler service implementation.

    Implements only the BaseService constructor usage; the rich lifecycle
    hooks in ``BaseService`` will be integrated when real scheduling logic
    (jobs, orchestrator, REST, metrics) is added. For now we expose a simple
    run loop that can be stopped with Ctrl+C.
    """

    def __init__(self):
        self.config = SchedulerConfig()
        super().__init__(self.config.service_name, self.config)
        # Replace BaseService's logger with unified configured logger so that
        # processors (timestamp, level, JSON/console) are active immediately.
        self.logger = setup_service_logging(
            self.config.service_name,
            self.config.log_level,
            version=self.config.service_version,
        )
        self._running = False

    async def run_forever(self):
        self.logger.info("scheduler loop starting")
        self._running = True
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:  # pragma: no cover
            self.logger.info("scheduler loop cancelled")
        finally:
            self.logger.info("scheduler loop stopped")

    async def start(self):  # type: ignore[override]
        self.logger.info(
            f"starting service v{self.config.service_version}"
        )
        # Launch background loop
        self._task = asyncio.create_task(self.run_forever())
        self.logger.info("service started")

    async def stop(self):  # type: ignore[override]
        if not getattr(self, "_running", False):
            return
        self.logger.info("stopping service")
        self._running = False
        self._task.cancel()
        with contextlib.suppress(Exception):  # pragma: no cover - best effort
            await self._task
        self.logger.info("service stopped")


async def main():
    service = SchedulerService()
    await service.start()
    try:
        # Wait until cancelled (Ctrl+C)
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:  # pragma: no cover - manual interrupt
        pass
    finally:
        await service.stop()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())