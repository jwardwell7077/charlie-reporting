"""
Standard Metrics and Monitoring System
Prometheus-compatible metrics for all services
"""

from typing import Dict, Any, Optional, List
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
import threading

# Metrics implementations (compatible with prometheus_client when available)
class MetricCollector:
    """Base metric collector that can work with or without prometheus_client"""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary"""
        with self._lock:
            return dict(self._metrics)


class Counter:
    """Counter metric - only increases"""
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values = defaultdict(float)
        self._lock = threading.Lock()
    
    def inc(self, amount: float = 1.0, **label_values):
        """Increment counter"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            self._values[label_key] += amount
    
    def labels(self, **label_values):
        """Return labeled counter"""
        return LabeledCounter(self, label_values)
    
    def _make_label_key(self, label_values: Dict[str, str]) -> str:
        """Create key from label values"""
        if not self.labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(label_values.items()))
    
    def get_value(self, **label_values) -> float:
        """Get counter value"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            return self._values[label_key]


class LabeledCounter:
    """Labeled counter for fluent API"""
    
    def __init__(self, counter: Counter, label_values: Dict[str, str]):
        self.counter = counter
        self.label_values = label_values
    
    def inc(self, amount: float = 1.0):
        """Increment labeled counter"""
        self.counter.inc(amount, **self.label_values)


class Histogram:
    """Histogram metric for measuring distributions"""
    
    def __init__(self, name: str, description: str, labels: List[str] = None, buckets: List[float] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        self._observations = defaultdict(list)
        self._lock = threading.Lock()
    
    def observe(self, value: float, **label_values):
        """Record an observation"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            self._observations[label_key].append(value)
    
    def labels(self, **label_values):
        """Return labeled histogram"""
        return LabeledHistogram(self, label_values)
    
    def _make_label_key(self, label_values: Dict[str, str]) -> str:
        """Create key from label values"""
        if not self.labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(label_values.items()))
    
    def get_stats(self, **label_values) -> Dict[str, float]:
        """Get histogram statistics"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            observations = self._observations[label_key]
            
            if not observations:
                return {"count": 0, "sum": 0, "avg": 0}
            
            return {
                "count": len(observations),
                "sum": sum(observations),
                "avg": sum(observations) / len(observations),
                "min": min(observations),
                "max": max(observations)
            }


class LabeledHistogram:
    """Labeled histogram for fluent API"""
    
    def __init__(self, histogram: Histogram, label_values: Dict[str, str]):
        self.histogram = histogram
        self.label_values = label_values
    
    def observe(self, value: float):
        """Record observation on labeled histogram"""
        self.histogram.observe(value, **self.label_values)


class Gauge:
    """Gauge metric - can go up and down"""
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values = defaultdict(float)
        self._lock = threading.Lock()
    
    def set(self, value: float, **label_values):
        """Set gauge value"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            self._values[label_key] = value
    
    def inc(self, amount: float = 1.0, **label_values):
        """Increment gauge"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            self._values[label_key] += amount
    
    def dec(self, amount: float = 1.0, **label_values):
        """Decrement gauge"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            self._values[label_key] -= amount
    
    def labels(self, **label_values):
        """Return labeled gauge"""
        return LabeledGauge(self, label_values)
    
    def _make_label_key(self, label_values: Dict[str, str]) -> str:
        """Create key from label values"""
        if not self.labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(label_values.items()))
    
    def get_value(self, **label_values) -> float:
        """Get gauge value"""
        with self._lock:
            label_key = self._make_label_key(label_values)
            return self._values[label_key]


class LabeledGauge:
    """Labeled gauge for fluent API"""
    
    def __init__(self, gauge: Gauge, label_values: Dict[str, str]):
        self.gauge = gauge
        self.label_values = label_values
    
    def set(self, value: float):
        """Set labeled gauge value"""
        self.gauge.set(value, **self.label_values)
    
    def inc(self, amount: float = 1.0):
        """Increment labeled gauge"""
        self.gauge.inc(amount, **self.label_values)
    
    def dec(self, amount: float = 1.0):
        """Decrement labeled gauge"""
        self.gauge.dec(amount, **self.label_values)


class ServiceMetrics:
    """
    Standard metrics collection for all Charlie Reporting services.
    
    Provides consistent metrics across all services:
    - Request metrics (count, duration, status)
    - Business operation metrics
    - Health status metrics
    - Resource utilization metrics
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        # === HTTP Request Metrics ===
        self.http_requests_total = Counter(
            name="http_requests_total",
            description="Total number of HTTP requests",
            labels=["service", "endpoint", "method", "status"]
        )
        
        self.http_request_duration_seconds = Histogram(
            name="http_request_duration_seconds",
            description="HTTP request duration in seconds",
            labels=["service", "endpoint", "method"]
        )
        
        # === Business Operation Metrics ===
        self.business_operations_total = Counter(
            name="business_operations_total",
            description="Total number of business operations",
            labels=["service", "operation", "status"]
        )
        
        self.business_operation_duration_seconds = Histogram(
            name="business_operation_duration_seconds",
            description="Business operation duration in seconds",
            labels=["service", "operation"]
        )
        
        # === Health and Status Metrics ===
        self.service_health_status = Gauge(
            name="service_health_status",
            description="Service health status (1=healthy, 0=unhealthy)",
            labels=["service"]
        )
        
        self.service_uptime_seconds = Gauge(
            name="service_uptime_seconds",
            description="Service uptime in seconds",
            labels=["service"]
        )
        
        # === Resource Metrics ===
        self.active_connections = Gauge(
            name="active_connections",
            description="Number of active connections",
            labels=["service"]
        )
        
        self.memory_usage_bytes = Gauge(
            name="memory_usage_bytes",
            description="Memory usage in bytes",
            labels=["service"]
        )
        
        # === Error Metrics ===
        self.errors_total = Counter(
            name="errors_total",
            description="Total number of errors",
            labels=["service", "error_type", "component"]
        )
        
        # Track service start time
        self._start_time = time.time()
    
    def record_http_request(self, endpoint: str, method: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        status = "success" if 200 <= status_code < 400 else "error"
        
        self.http_requests_total.labels(
            service=self.service_name,
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.http_request_duration_seconds.labels(
            service=self.service_name,
            endpoint=endpoint,
            method=method
        ).observe(duration)
    
    def record_business_operation(self, operation: str, status: str, duration: float):
        """Record business operation metrics"""
        self.business_operations_total.labels(
            service=self.service_name,
            operation=operation,
            status=status
        ).inc()
        
        self.business_operation_duration_seconds.labels(
            service=self.service_name,
            operation=operation
        ).observe(duration)
    
    def set_health_status(self, healthy: bool):
        """Set service health status"""
        self.service_health_status.labels(service=self.service_name).set(1 if healthy else 0)
    
    def update_uptime(self):
        """Update service uptime"""
        uptime = time.time() - self._start_time
        self.service_uptime_seconds.labels(service=self.service_name).set(uptime)
    
    def record_error(self, error_type: str, component: str = "unknown"):
        """Record an error occurrence"""
        self.errors_total.labels(
            service=self.service_name,
            error_type=error_type,
            component=component
        ).inc()
    
    def set_active_connections(self, count: int):
        """Set number of active connections"""
        self.active_connections.labels(service=self.service_name).set(count)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary for debugging/monitoring"""
        return {
            "http_requests_total": dict(self.http_requests_total._values),
            "business_operations_total": dict(self.business_operations_total._values),
            "service_health": self.service_health_status.get_value(service=self.service_name),
            "uptime_seconds": time.time() - self._start_time,
            "errors_total": dict(self.errors_total._values)
        }


def time_operation(metrics: ServiceMetrics, operation_name: str):
    """Decorator to time business operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                metrics.record_error(type(e).__name__, operation_name)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_business_operation(operation_name, status, duration)
        
        return wrapper
    return decorator


class MetricsExporter:
    """Export metrics in Prometheus format"""
    
    @staticmethod
    def export_prometheus_format(metrics: ServiceMetrics) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        # Add help and type information
        lines.append(f"# HELP http_requests_total Total HTTP requests")
        lines.append(f"# TYPE http_requests_total counter")
        
        # Export counter values
        for label_key, value in metrics.http_requests_total._values.items():
            if label_key:
                lines.append(f"http_requests_total{{{label_key}}} {value}")
            else:
                lines.append(f"http_requests_total {value}")
        
        # Add more metrics as needed...
        
        return "\n".join(lines)
