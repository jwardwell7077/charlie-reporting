"""
Metrics Collection Implementation
Production implementation of IMetricsCollector interface.
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict
import threading
from dataclasses import dataclass, field
from datetime import datetime

from business.interfaces import IMetricsCollector


@dataclass
class MetricData:
    """Container for metric data with timestamp."""
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollectorImpl(IMetricsCollector):
    """
    Production implementation of metrics collection.

    Features:
    - Thread - safe metric collection
    - Counter, gauge, and timing metrics
    - Label support for dimensional metrics
    - Memory - efficient storage with retention limits
    """

    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.lock = threading.RLock()

        # Metric storage
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, MetricData] = {}
        self.timings: Dict[str, list] = defaultdict(list)
        self.histogram_data: Dict[str, list] = defaultdict(list)

        # Metadata
        self.start_time = time.time()
        self.metric_count = 0

    async def increment_counter(self, metric_name: str, value: float = 1.0,
                                labels: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.

        Args:
            metric_name: Name of the counter metric
            value: Value to increment by (default: 1.0)
            labels: Optional labels for dimensional metrics
        """
        key = self.build_metric_key(metric_name, labels)

        with self.lock:
            self.counters[key] += value
            self.metric_count += 1
            self.cleanup_if_needed()

    async def set_gauge(self, metric_name: str, value: float,
                        labels: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric value.

        Args:
            metric_name: Name of the gauge metric
            value: Current value of the gauge
            labels: Optional labels for dimensional metrics
        """
        key = self.build_metric_key(metric_name, labels)

        with self.lock:
            self.gauges[key] = MetricData(
                value=value,
                labels=labels or {}
            )
            self.metric_count += 1
            self.cleanup_if_needed()

    async def record_timing(self, metric_name: str, duration_seconds: float,
                            labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a timing metric.

        Args:
            metric_name: Name of the timing metric
            duration_seconds: Duration in seconds
            labels: Optional labels for dimensional metrics
        """
        key = self.build_metric_key(metric_name, labels)

        with self.lock:
            self.timings[key].append(MetricData(
                value=duration_seconds,
                labels=labels or {}
            ))

            # Keep only recent timings to prevent memory growth
            if len(self.timings[key]) > 1000:
                self.timings[key] = self.timings[key][-500:]

            self.metric_count += 1
            self.cleanup_if_needed()

    async def record_histogram(self, metric_name: str, value: float,
                               labels: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram metric value.

        Args:
            metric_name: Name of the histogram metric
            value: Value to record
            labels: Optional labels for dimensional metrics
        """
        key = self.build_metric_key(metric_name, labels)

        with self.lock:
            self.histogram_data[key].append(MetricData(
                value=value,
                labels=labels or {}
            ))

            # Keep only recent values
            if len(self.histogram_data[key]) > 1000:
                self.histogram_data[key] = self.histogram_data[key][-500:]

            self.metric_count += 1
            self.cleanup_if_needed()

    def build_metric_key(self, metric_name: str,
                         labels: Optional[Dict[str, str]]) -> str:
        """Build a unique key for metric with labels."""
        if not labels:
            return metric_name

        # Sort labels for consistent key generation
        label_parts = [f"{k}={v}" for k, v in sorted(labels.items())]
        return f"{metric_name}{{{','.join(label_parts)}}}"

    def cleanup_if_needed(self) -> None:
        """Cleanup old metrics if we exceed the limit."""
        if self.metric_count > self.max_metrics:
            # Remove oldest 25% of metrics
            cleanup_count = self.max_metrics // 4

            # Clean up timing data first (most memory intensive)
            for key in list(self.timings.keys())[:cleanup_count]:
                if key in self.timings:
                    del self.timings[key]

            # Clean up histogram data
            remaining = cleanup_count - len(self.timings)
            if remaining > 0:
                for key in list(self.histogram_data.keys())[:remaining]:
                    if key in self.histogram_data:
                        del self.histogram_data[key]

            self.metric_count = len(self.counters) + len(self.gauges) + \
                len(self.timings) + len(self.histogram_data)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all collected metrics.

        Returns:
            Dictionary containing metric summaries
        """
        with self.lock:
            summary = {
                'counters': dict(self.counters),
                'gauges': {
                    k: {'value': v.value, 'timestamp': v.timestamp.isoformat()}
                    for k, v in self.gauges.items()
                },
                'timing_stats': {},
                'histogram_stats': {},
                'system': {
                    'uptime_seconds': time.time() - self.start_time,
                    'total_metrics': self.metric_count,
                    'memory_usage': {
                        'counters': len(self.counters),
                        'gauges': len(self.gauges),
                        'timings': sum(len(v) for v in self.timings.values()),
                        'histograms': sum(len(v) for v in
                                          self.histogram_data.values())
                    }
                }
            }

            # Calculate timing statistics
            for key, timings in self.timings.items():
                if timings:
                    values = [t.value for t in timings]
                    summary['timing_stats'][key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'latest': values[-1] if values else 0
                    }

            # Calculate histogram statistics
            for key, hist_data in self.histogram_data.items():
                if hist_data:
                    values = [h.value for h in hist_data]
                    summary['histogram_stats'][key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values)
                    }

            return summary
