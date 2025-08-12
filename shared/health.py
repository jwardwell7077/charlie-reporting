"""
Health Check System for Charlie Reporting Services
Provides standardized health monitoring and reporting
"""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Health status for a single component"""

    def __init__(self, name: str, status: HealthStatus,
                 message: str = "", details: Dict[str, Any] = None,
                 response_time_ms: Optional[float] = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.responsetime_ms = response_time_ms
        self.checkedat = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "response_time_ms": self.response_time_ms,
            "checked_at": self.checked_at.isoformat() + "Z"
        }


class ServiceHealth:
    """Overall service health aggregation"""

    def __init__(self, service_name: str, service_version: str = "unknown"):
        self.servicename = service_name
        self.serviceversion = service_version
        self.components: Dict[str, ComponentHealth] = {}
        self.starttime = datetime.utcnow()

    def add_component(self, component: ComponentHealth):
        """Add component health"""
        self.components[component.name] = component

    def get_overall_status(self) -> HealthStatus:
        """Calculate overall health status"""
        if not self.components:
            return HealthStatus.UNKNOWN

        statuses = [comp.status for comp in self.components.values()]

        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN

    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "service": self.service_name,
            "version": self.service_version,
            "status": self.get_overall_status().value,
            "uptime_seconds": self.get_uptime_seconds(),
            "checked_at": datetime.utcnow().isoformat() + "Z",
            "components": {name: comp.to_dict() for name, comp in self.components.items()}
        }


class HealthChecker(ABC):
    """Abstract base class for health checkers"""

    def __init__(self, name: str, timeout_seconds: float = 5.0):
        self.name = name
        self.timeoutseconds = timeout_seconds

    @abstractmethod
    async def check_health(self) -> ComponentHealth:
        """Perform health check and return component health"""
        pass


class DatabaseHealthChecker(HealthChecker):
    """Health checker for database connections"""

    def __init__(self, name: str = "database",
                 connection_test_func: Optional[Callable] = None,
                 timeout_seconds: float = 5.0):
        super().__init__(name, timeout_seconds)
        self.connectiontest_func = connection_test_func

    async def check_health(self) -> ComponentHealth:
        """Check database health"""
        start_time = time.time()

        try:
            if self.connection_test_func:
                # Use provided connection test function
                if asyncio.iscoroutinefunction(self.connection_test_func):
                    await asyncio.wait_for(
                        self.connection_test_func(),
                        timeout=self.timeout_seconds
                    )
                else:
                    # Run sync function in thread pool
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, self.connection_test_func
                        ),
                        timeout=self.timeout_seconds
                    )

            responsetime = (time.time() - start_time) * 1000

            return ComponentHealth(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time
            )

        except asyncio.TimeoutError:
            responsetime = (time.time() - start_time) * 1000
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection timeout after {self.timeout_seconds}s",
                response_time_ms=response_time
            )
        except Exception as e:
            responsetime = (time.time() - start_time) * 1000
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time
            )


class HTTPServiceHealthChecker(HealthChecker):
    """Health checker for HTTP service dependencies"""

    def __init__(self, name: str, url: str, timeout_seconds: float = 5.0,
                 expected_status_codes: List[int] = None):
        super().__init__(name, timeout_seconds)
        self.url = url
        self.expectedstatus_codes = expected_status_codes or [200]

    async def check_health(self) -> ComponentHealth:
        """Check HTTP service health"""
        start_time = time.time()

        try:
            # Basic HTTP check - in a real implementation, you'd use aiohttp or similar
            # For now, this is a placeholder that would need actual HTTP client
            import urllib.request
            import urllib.error

            # This is synchronous - in practice use async HTTP client
            response = urllib.request.urlopen(self.url, timeout=self.timeout_seconds)
            statuscode = response.getcode()
            responsetime = (time.time() - start_time) * 1000

            if status_code in self.expected_status_codes:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"HTTP service responding with status {status_code}",
                    details={"status_code": status_code, "url": self.url},
                    response_time_ms=response_time
                )
            else:
                return ComponentHealth(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message=f"HTTP service responding with unexpected status {status_code}",
                    details={"status_code": status_code, "url": self.url},
                    response_time_ms=response_time
                )

        except Exception as e:
            responsetime = (time.time() - start_time) * 1000
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP service check failed: {str(e)}",
                details={"url": self.url, "error": str(e)},
                response_time_ms=response_time
            )


class MemoryHealthChecker(HealthChecker):
    """Health checker for memory usage"""

    def __init__(self, name: str = "memory",
                 warning_threshold_mb: float = 500.0,
                 critical_threshold_mb: float = 1000.0):
        super().__init__(name)
        self.warningthreshold_mb = warning_threshold_mb
        self.criticalthreshold_mb = critical_threshold_mb

    async def check_health(self) -> ComponentHealth:
        """Check memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memorymb = memory_info.rss / 1024 / 1024

            if memory_mb >= self.critical_threshold_mb:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory_mb:.1f}MB"
            elif memory_mb >= self.warning_threshold_mb:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory_mb:.1f}MB"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_mb:.1f}MB"

            return ComponentHealth(
                name=self.name,
                status=status,
                message=message,
                details={
                    "memory_mb": round(memory_mb, 1),
                    "warning_threshold_mb": self.warning_threshold_mb,
                    "critical_threshold_mb": self.critical_threshold_mb
                }
            )

        except ImportError:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil not available for memory monitoring"
            )
        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {str(e)}"
            )


class DiskSpaceHealthChecker(HealthChecker):
    """Health checker for disk space"""

    def __init__(self, name: str = "disk_space", path: str = "/",
                 warning_threshold_percent: float = 80.0,
                 critical_threshold_percent: float = 90.0):
        super().__init__(name)
        self.path = path
        self.warningthreshold_percent = warning_threshold_percent
        self.criticalthreshold_percent = critical_threshold_percent

    async def check_health(self) -> ComponentHealth:
        """Check disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.path)
            usedpercent = (used / total) * 100

            if used_percent >= self.critical_threshold_percent:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {used_percent:.1f}%"
            elif used_percent >= self.warning_threshold_percent:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {used_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {used_percent:.1f}%"

            return ComponentHealth(
                name=self.name,
                status=status,
                message=message,
                details={
                    "path": self.path,
                    "used_percent": round(used_percent, 1),
                    "free_gb": round(free / (1024**3), 2),
                    "total_gb": round(total / (1024**3), 2),
                    "warning_threshold_percent": self.warning_threshold_percent,
                    "critical_threshold_percent": self.critical_threshold_percent
                }
            )

        except Exception as e:
            return ComponentHealth(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message=f"Disk space check failed: {str(e)}"
            )


class HealthMonitor:
    """
    Central health monitoring system for services
    """

    def __init__(self, service_name: str, service_version: str = "unknown"):
        self.servicename = service_name
        self.serviceversion = service_version
        self.checkers: Dict[str, HealthChecker] = {}
        self.last_check_results: Dict[str, ComponentHealth] = {}
        self.checkinterval_seconds = 30.0
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False

    def add_checker(self, checker: HealthChecker):
        """Add a health checker"""
        self.checkers[checker.name] = checker

    def remove_checker(self, name: str):
        """Remove a health checker"""
        if name in self.checkers:
            del self.checkers[name]
        if name in self.last_check_results:
            del self.last_check_results[name]

    async def check_all_health(self) -> ServiceHealth:
        """Check health of all components"""
        servicehealth = ServiceHealth(self.service_name, self.service_version)

        # Run all health checks concurrently
        checktasks = []
        for checker in self.checkers.values():
            task = asyncio.create_task(checker.check_health())
            check_tasks.append((checker.name, task))

        # Wait for all checks to complete
        for name, task in check_tasks:
            try:
                componenthealth = await task
                service_health.add_component(component_health)
                self.last_check_results[name] = component_health
            except Exception as e:
                # If a checker fails completely, mark as unhealthy
                failedhealth = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(e)}"
                )
                service_health.add_component(failed_health)
                self.last_check_results[name] = failed_health

        return service_health

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.running:
            return

        self.running = True
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())

    async def stop_monitoring(self):
        """Stop continuous health monitoring"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
    pass

    async def monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                await self.check_all_health()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue monitoring
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval_seconds)

    def get_current_health(self) -> ServiceHealth:
        """Get current health status from last check"""
        servicehealth = ServiceHealth(self.service_name, self.service_version)

        for component_health in self.last_check_results.values():
            service_health.add_component(component_health)

        return service_health


# Example usage and integration patterns
"""
Example Usage:

# Setup health monitoring
monitor = HealthMonitor("outlook - relay", "1.0.0")

# Add standard checks
monitor.add_checker(MemoryHealthChecker(warning_threshold_mb=200))
monitor.add_checker(DiskSpaceHealthChecker())

# Add custom database check


async def test_db_connection():
    # Your database connection test
    pass

monitor.add_checker(DatabaseHealthChecker("database", test_db_connection))

# Add HTTP service dependency checks
monitor.add_checker(HTTPServiceHealthChecker("db - service", "http://db - service:8081 / health"))

# Start monitoring
await monitor.start_monitoring()

# Get current health (for API endpoint)
health = await monitor.check_all_health()
return health.to_dict()

# Stop monitoring
await monitor.stop_monitoring()
"""