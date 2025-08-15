"""Metrics Collection Infrastructure
Prometheus - compatible metrics collection for monitoring and observability
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..business.interfaces import IMetricsCollector


@dataclass


class MetricData:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


@dataclass


class ProcessingMetric:
    """Processing - specific metric data"""
    operation_type: str
    duration_seconds: float
    success: bool
    files_count: int = 0
    records_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsCollector:
    """Infrastructure service for collecting and exposing metrics
    Compatible with Prometheus monitoring but works standalone
    """

    def __init__(self, retention_hours: int = 24):
        self.retentionhours = retention_hours
        self.lock = threading.Lock()
        self.start_time = time.time()

        # Metric storage
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = defaultdict(float)
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self.processing_metrics: deque = deque(maxlen=1000)  # Keep last 1000 operations

        # Request tracking
        self.requests_total = 0
        self.requests_success = 0
        self.requests_failed = 0
        self.request_durations: list[float] = []

        # Processing tracking
        self.files_processed_total = 0
        self.records_processed_total = 0
        self.processing_errors: list[str] = []

        # Health status
        self.healthy = True
        self.last_health_check = datetime.utcnow()

    def initialize(self):
        """Initialize the metrics collector"""
        with self.lock:
            self.start_time = time.time()
            self.healthy = True
            self.last_health_check = datetime.utcnow()

    def cleanup(self):
        """Cleanup resources"""
        with self.lock:
            self.healthy = False

    def is_healthy(self) -> bool:
        """Check if metrics collector is healthy"""
        return self.healthy

    def record_request(self, method: str, path: str, status_code: int, duration_seconds: float):
        """Record HTTP request metrics"""
        with self.lock:
            self.requests_total += 1

            if 200 <= status_code < 400:
                self.requests_success += 1
                self.counters["requests_success_total"] += 1
            else:
                self.requests_failed += 1
                self.counters["requests_failed_total"] += 1

            # Track request duration
            self.request_durations.append(duration_seconds)
            self.histograms["request_duration_seconds"].append(duration_seconds)

            # Keep only recent durations (last 1000)
            if len(self.request_durations) > 1000:
                self.request_durations = self.request_durations[-1000:]

            # Update gauges
            self.gauges["requests_total"] = self.requests_total
            self.gauges["requests_success"] = self.requests_success
            self.gauges["requests_failed"] = self.requests_failed

            # Calculate average duration
            if self.request_durations:
                self.gauges["avg_request_duration_seconds"] = sum(self.request_durations) / len(self.request_durations)

    def record_directory_processing(self, files_processed: int, records_processed: int,
                                  success: bool, duration_seconds: float):
        """Record directory processing metrics"""
        with self.lock:
            metric = ProcessingMetric(
                operation_type="directory_processing",
                duration_seconds=duration_seconds,
                success=success,
                files_count=files_processed,
                records_count=records_processed
            )
            self.processing_metrics.append(metric)

            if success:
                self.counters["directory_processing_success_total"] += 1
                self.files_processed_total += files_processed
                self.records_processed_total += records_processed
            else:
                self.counters["directory_processing_failed_total"] += 1

            # Update processing histograms
            self.histograms["processing_duration_seconds"].append(duration_seconds)
            self.histograms["files_per_operation"].append(files_processed)
            self.histograms["records_per_operation"].append(records_processed)

            # Update gauges
            self.gauges["files_processed_total"] = self.files_processed_total
            self.gauges["records_processed_total"] = self.records_processed_total

    def record_file_processing(self, file_name: str, records_processed: int,
                             success: bool, duration_seconds: float):
        """Record single file processing metrics"""
        with self.lock:
            metric = ProcessingMetric(
                operation_type="file_processing",
                duration_seconds=duration_seconds,
                success=success,
                files_count=1,
                records_count=records_processed
            )
            self.processing_metrics.append(metric)

            if success:
                self.counters["file_processing_success_total"] += 1
                self.files_processed_total += 1
                self.records_processed_total += records_processed
            else:
                self.counters["file_processing_failed_total"] += 1

            # Update gauges
            self.gauges["files_processed_total"] = self.files_processed_total
            self.gauges["records_processed_total"] = self.records_processed_total

    def record_processing_error(self, operation_type: str, error_message: str):
        """Record processing error"""
        with self.lock:
            self.processing_errors.append(f"{operation_type}: {error_message}")
            self.counters[f"{operation_type}errors_total"] += 1

            # Keep only recent errors (last 100)
            if len(self.processing_errors) > 100:
                self.processing_errors = self.processing_errors[-100:]

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics"""
        with self.lock:
            uptime_seconds = time.time() - self.start_time

            # Calculate processing rates
            files_per_second = self.files_processed_total / uptime_seconds if uptime_seconds > 0 else 0
            records_per_second = self.records_processed_total / uptime_seconds if uptime_seconds > 0 else 0

            # Calculate success rates
            total_operations = len(self.processing_metrics)
            successful_operations = sum(1 for m in self.processing_metrics if m.success)
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0

            # Processing efficiency assessment
            avg_processing_time = self.calculate_average_processing_time()
            efficiency = self.assess_processing_efficiency(avg_processing_time)

            # Generate recommendations
            recommendations = self.generate_recommendations()

            return {
                # Basic metrics
                "uptime_seconds": uptime_seconds,
                "total_requests": self.requests_total,
                "successful_requests": self.requests_success,
                "failed_requests": self.requests_failed,
                "avg_processing_time": self.gauges.get("avg_request_duration_seconds", 0.0),

                # Processing metrics
                "total_files_processed": self.files_processed_total,
                "total_records_processed": self.records_processed_total,
                "files_per_second": files_per_second,
                "records_per_second": records_per_second,
                "success_rate": success_rate,
                "processing_efficiency": efficiency,
                "recommendations": recommendations,

                # Detailed metrics
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "recent_errors": list(self.processing_errors),

                # Health
                "healthy": self.healthy,
                "last_health_check": self.last_health_check.isoformat()
            }

    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        with self.lock:
            lines = []

            # Add help and type information
            lines.append("# HELP report_generator_uptime_seconds Service uptime")
            lines.append("# TYPE report_generator_uptime_seconds gauge")
            lines.append(f"report_generator_uptime_seconds {time.time() - self.start_time}")

            lines.append("# HELP report_generator_requests_total Total HTTP requests")
            lines.append("# TYPE report_generator_requests_total counter")
            lines.append(f"report_generator_requests_total {self.requests_total}")

            lines.append("# HELP report_generator_files_processed_total Total files processed")
            lines.append("# TYPE report_generator_files_processed_total counter")
            lines.append(f"report_generator_files_processed_total {self.files_processed_total}")

            lines.append("# HELP report_generator_records_processed_total Total records processed")
            lines.append("# TYPE report_generator_records_processed_total counter")
            lines.append(f"report_generator_records_processed_total {self.records_processed_total}")

            # Add counter metrics
            for name, value in self.counters.items():
                lines.append(f"# TYPE report_generator_{name} counter")
                lines.append(f"report_generator_{name} {value}")

            # Add gauge metrics
            for name, value in self.gauges.items():
                lines.append(f"# TYPE report_generator_{name} gauge")
                lines.append(f"report_generator_{name} {value}")

            return "\n".join(lines)

    def get_health_metrics(self) -> dict[str, Any]:
        """Get health-specific metrics"""
        with self.lock:
            recent_error_count = len([
                e for e in self.processing_errors
                if "error" in e.lower() or "failed" in e.lower()
            ])

            return {
                "healthy": self.healthy,
                "uptime_seconds": time.time() - self.start_time,
                "recent_error_count": recent_error_count,
                "success_rate": self.calculate_success_rate(),
                "avg_response_time": self.gauges.get("avg_request_duration_seconds", 0.0),
                "last_health_check": self.last_health_check.isoformat(),
            }

    def reset_metrics(self):
        """Reset all metrics (for testing)"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.processing_metrics.clear()
            self.request_durations.clear()
            self.processing_errors.clear()

            self.requests_total = 0
            self.requests_success = 0
            self.requests_failed = 0
            self.files_processed_total = 0
            self.records_processed_total = 0

            self.start_time = time.time()

    def calculate_average_processing_time(self) -> float:
        """Calculate average processing time for recent operations (last hour)"""
        if not self.processing_metrics:
            return 0.0

        recent_operations = [
            m for m in self.processing_metrics
            if m.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]

        if not recent_operations:
            return 0.0

        return sum(op.duration_seconds for op in recent_operations) / len(recent_operations)

    def assess_processing_efficiency(self, avg_time: float) -> str:
        """Assess processing efficiency based on average time"""
        if avg_time < 5:
            return "excellent"
        elif avg_time < 15:
            return "good"
        elif avg_time < 30:
            return "moderate"
        else:
            return "slow"

    def calculate_success_rate(self) -> float:
        """Calculate success rate for operations in the last hour"""
        if not self.processing_metrics:
            return 100.0

        recent_operations = [
            m for m in self.processing_metrics
            if m.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]

        if not recent_operations:
            return 100.0

        successful = sum(1 for op in recent_operations if op.success)
        return (successful / len(recent_operations)) * 100

    def generate_recommendations(self) -> list[str]:
        """Generate performance recommendations based on metrics"""
        recommendations: list[str] = []

        # Success rate assessment
        success_rate = self.calculate_success_rate()
        if success_rate < 95:
            recommendations.append("Success rate below 95% - investigate processing errors")

        # Processing time assessment
        avg_time = self.calculate_average_processing_time()
        if avg_time > 30:
            recommendations.append("High processing times detected - consider optimizing data operations")

        # Error frequency assessment
        recent_error_count = len(self.processing_errors)
        if recent_error_count > 10:
            recommendations.append("High error frequency - review input data quality")

        # Retention / memory usage heuristic
        if len(self.processing_metrics) > 800:
            recommendations.append("High metrics volume - consider increasing retention window or archiving older entries")

        return recommendations


# Global metrics collector instance
global_metrics: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    global global_metrics

    if global_metrics is None:
        global_metrics = MetricsCollector()

    return global_metrics


class MetricsCollectorImpl(IMetricsCollector):
    """Implementation of IMetricsCollector interface
    Adapter for the existing MetricsCollector
    """

    def __init__(self):
        self.metrics = get_metrics_collector()

    async def increment_counter(
        self, name: str, value: float = 1.0, **labels
    ) -> None:
        """Increment a counter metric"""
        # Use the existing counters storage directly
        with self.metrics.lock:
            self.metrics.counters[name] += value

    async def set_gauge(self, name: str, value: float, **labels) -> None:
        """Set a gauge metric value"""
        # Use the existing gauges storage directly
        with self.metrics.lock:
            self.metrics.gauges[name] = value

    async def record_histogram(
        self, name: str, value: float, **labels
    ) -> None:
        """Record a value in histogram metric"""
        # Use the existing histograms storage directly
        with self.metrics.lock:
            self.metrics.histograms[name].append(value)

    async def record_processing_time(
        self,
        operation: str,
        duration_seconds: float,
        success: bool = True,
        **metadata
    ) -> None:
        """Record processing operation timing"""
        # Map to existing methods based on operation type
        if operation == "directory_processing":
            self.metrics.record_directory_processing(
                files_processed=metadata.get("files_count", 0),
                records_processed=metadata.get("records_count", 0),
                duration_seconds=duration_seconds,
                success=success
            )
        elif operation == "file_processing":
            self.metrics.record_file_processing(
                file_name=metadata.get("file_name", "unknown"),
                records_processed=metadata.get("records_count", 0),
                duration_seconds=duration_seconds,
                success=success
            )
        else:
            # Generic processing metric
            metric = ProcessingMetric(
                operation_type=operation,
                duration_seconds=duration_seconds,
                success=success,
                files_count=metadata.get("files_count", 0),
                records_count=metadata.get("records_count", 0)
            )
            self.metrics.processing_metrics.append(metric)

    async def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all metrics"""
        return self.metrics.get_metrics()
