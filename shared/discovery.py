"""
Service Discovery and Communication for Charlie Reporting Microservices
Provides service registry and inter-service communication patterns
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import threading
import time


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_name: str
    service_id: str
    host: str
    port: int
    version: str
    status: ServiceStatus
    health_check_url: str
    api_base_url: str
    tags: List[str]
    metadata: Dict[str, Any]
    registered_at: datetime
    last_heartbeat: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["registered_at"] = self.registered_at.isoformat()
        data["last_heartbeat"] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceRegistration':
        """Create from dictionary"""
        data["registered_at"] = datetime.fromisoformat(data["registered_at"])
        data["last_heartbeat"] = datetime.fromisoformat(data["last_heartbeat"])
        data["status"] = ServiceStatus(data["status"])
        return cls(**data)


class ServiceRegistry(ABC):
    """Abstract service registry interface"""
    
    @abstractmethod
    async def register_service(self, registration: ServiceRegistration) -> bool:
        """Register a service"""
        pass
    
    @abstractmethod
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service"""
        pass
    
    @abstractmethod
    async def update_heartbeat(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service heartbeat"""
        pass
    
    @abstractmethod
    async def get_service(self, service_name: str) -> Optional[ServiceRegistration]:
        """Get a service by name"""
        pass
    
    @abstractmethod
    async def get_all_services(self) -> List[ServiceRegistration]:
        """Get all registered services"""
        pass
    
    @abstractmethod
    async def get_healthy_services(self, service_name: str) -> List[ServiceRegistration]:
        """Get all healthy instances of a service"""
        pass


class InMemoryServiceRegistry(ServiceRegistry):
    """
    In-memory service registry for development and testing
    In production, this would be replaced with Consul, etcd, or similar
    """
    
    def __init__(self, heartbeat_timeout_seconds: float = 30.0):
        self._services: Dict[str, ServiceRegistration] = {}
        self._lock = threading.RLock()
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the registry cleanup task"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the registry"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def register_service(self, registration: ServiceRegistration) -> bool:
        """Register a service"""
        with self._lock:
            self._services[registration.service_id] = registration
            return True
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service"""
        with self._lock:
            if service_id in self._services:
                del self._services[service_id]
                return True
            return False
    
    async def update_heartbeat(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service heartbeat"""
        with self._lock:
            if service_id in self._services:
                self._services[service_id].last_heartbeat = datetime.utcnow()
                self._services[service_id].status = status
                return True
            return False
    
    async def get_service(self, service_name: str) -> Optional[ServiceRegistration]:
        """Get a service by name (returns first healthy instance)"""
        healthy_services = await self.get_healthy_services(service_name)
        return healthy_services[0] if healthy_services else None
    
    async def get_all_services(self) -> List[ServiceRegistration]:
        """Get all registered services"""
        with self._lock:
            return list(self._services.values())
    
    async def get_healthy_services(self, service_name: str) -> List[ServiceRegistration]:
        """Get all healthy instances of a service"""
        with self._lock:
            now = datetime.utcnow()
            healthy_services = []
            
            for service in self._services.values():
                if service.service_name == service_name:
                    # Check if service is healthy and heartbeat is recent
                    heartbeat_age = (now - service.last_heartbeat).total_seconds()
                    
                    if (service.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED] and
                        heartbeat_age < self.heartbeat_timeout_seconds):
                        healthy_services.append(service)
            
            return healthy_services
    
    async def _cleanup_loop(self):
        """Cleanup stale services"""
        while self._running:
            try:
                await self._cleanup_stale_services()
                await asyncio.sleep(10)  # Cleanup every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Service registry cleanup error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_stale_services(self):
        """Remove services with stale heartbeats"""
        with self._lock:
            now = datetime.utcnow()
            stale_services = []
            
            for service_id, service in self._services.items():
                heartbeat_age = (now - service.last_heartbeat).total_seconds()
                
                if heartbeat_age > self.heartbeat_timeout_seconds * 2:  # 2x timeout for removal
                    stale_services.append(service_id)
            
            for service_id in stale_services:
                del self._services[service_id]


class ServiceClient:
    """
    HTTP client for inter-service communication with service discovery
    """
    
    def __init__(self, registry: ServiceRegistry, timeout_seconds: float = 30.0):
        self.registry = registry
        self.timeout_seconds = timeout_seconds
        self._session = None
    
    async def _get_session(self):
        """Get or create HTTP session"""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)
            )
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def call_service(self, service_name: str, method: str, path: str, 
                          **kwargs) -> Any:
        """
        Make HTTP call to a service
        
        Args:
            service_name: Name of the target service
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/api/v1/resource")
            **kwargs: Additional arguments for the HTTP request
        
        Returns:
            Response data
        """
        service = await self.registry.get_service(service_name)
        if not service:
            raise ServiceNotFoundError(f"Service '{service_name}' not found or unhealthy")
        
        url = f"{service.api_base_url}{path}"
        session = await self._get_session()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    return await response.json()
                else:
                    return await response.text()
                    
        except Exception as e:
            raise ServiceCallError(f"Failed to call {service_name}: {str(e)}")
    
    async def get(self, service_name: str, path: str, **kwargs) -> Any:
        """Make GET request to service"""
        return await self.call_service(service_name, "GET", path, **kwargs)
    
    async def post(self, service_name: str, path: str, **kwargs) -> Any:
        """Make POST request to service"""
        return await self.call_service(service_name, "POST", path, **kwargs)
    
    async def put(self, service_name: str, path: str, **kwargs) -> Any:
        """Make PUT request to service"""
        return await self.call_service(service_name, "PUT", path, **kwargs)
    
    async def delete(self, service_name: str, path: str, **kwargs) -> Any:
        """Make DELETE request to service"""
        return await self.call_service(service_name, "DELETE", path, **kwargs)


class ServiceDiscoveryMixin:
    """
    Mixin for services to integrate with service discovery
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registry: Optional[ServiceRegistry] = None
        self.service_registration: Optional[ServiceRegistration] = None
        self.service_client: Optional[ServiceClient] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._heartbeat_interval = 15.0  # seconds
    
    def setup_service_discovery(self, registry: ServiceRegistry, 
                               service_name: str, service_id: str,
                               host: str, port: int, version: str = "1.0.0"):
        """Setup service discovery integration"""
        self.registry = registry
        self.service_client = ServiceClient(registry)
        
        # Create service registration
        self.service_registration = ServiceRegistration(
            service_name=service_name,
            service_id=service_id,
            host=host,
            port=port,
            version=version,
            status=ServiceStatus.STARTING,
            health_check_url=f"http://{host}:{port}/health",
            api_base_url=f"http://{host}:{port}",
            tags=[],
            metadata={},
            registered_at=datetime.utcnow(),
            last_heartbeat=datetime.utcnow()
        )
    
    async def register_with_discovery(self):
        """Register service with discovery system"""
        if not self.registry or not self.service_registration:
            return
        
        await self.registry.register_service(self.service_registration)
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def deregister_from_discovery(self):
        """Deregister service from discovery system"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.registry and self.service_registration:
            await self.registry.deregister_service(self.service_registration.service_id)
        
        if self.service_client:
            await self.service_client.close()
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to registry"""
        while True:
            try:
                if self.registry and self.service_registration:
                    # Determine current health status
                    # This could be enhanced to check actual service health
                    status = ServiceStatus.HEALTHY
                    
                    await self.registry.update_heartbeat(
                        self.service_registration.service_id, 
                        status
                    )
                
                await asyncio.sleep(self._heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(self._heartbeat_interval)


# Exception classes
class ServiceDiscoveryError(Exception):
    """Base exception for service discovery errors"""
    pass


class ServiceNotFoundError(ServiceDiscoveryError):
    """Service not found in registry"""
    pass


class ServiceCallError(ServiceDiscoveryError):
    """Error calling another service"""
    pass


# Factory function for easy setup
def create_service_registry() -> ServiceRegistry:
    """Create a service registry instance"""
    # In production, this might return a Consul or etcd-based registry
    return InMemoryServiceRegistry()


# Example usage patterns
"""
Example Usage:

# Setup service discovery
registry = create_service_registry()
await registry.start()

# Register a service (typically done in BaseService)
class OutlookRelayService(BaseService, ServiceDiscoveryMixin):
    async def startup(self):
        self.setup_service_discovery(
            registry, "outlook-relay", "outlook-relay-1", "localhost", 8080
        )
        await self.register_with_discovery()
        await super().startup()
    
    async def shutdown(self):
        await self.deregister_from_discovery()
        await super().shutdown()

# Call another service
client = ServiceClient(registry)
try:
    result = await client.get("db-service", "/api/v1/reports")
    print(result)
finally:
    await client.close()

# Get service information
db_service = await registry.get_service("db-service")
if db_service:
    print(f"DB Service available at {db_service.api_base_url}")
"""
