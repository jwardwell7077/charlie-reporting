"""
Metrics Collection Infrastructure
Prometheus-compatible metrics collection for monitoring and observability
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque


@dataclass
class MetricData:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProcessingMetric:
    """Processing-specific metric data"""
    operation_type: str
    duration_seconds: float
    success: bool
    files_count: int = 0
    records_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MetricsCollector:
    """
    Infrastructure service for collecting and exposing metrics
    Compatible with Prometheus monitoring but works standalone
    """
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self._lock = threading.Lock()
        self._start_time = time.time()
        
        # Metric storage
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._processing_metrics: deque = deque(maxlen=1000)  # Keep last 1000 operations
        
        # Request tracking
        self._requests_total = 0
        self._requests_success = 0
        self._requests_failed = 0
        self._request_durations: List[float] = []
        
        # Processing tracking
        self._files_processed_total = 0
        self._records_processed_total = 0
        self._processing_errors: List[str] = []
        
        # Health status
        self._healthy = True
        self._last_health_check = datetime.utcnow()
    
    def initialize(self):
        """Initialize the metrics collector"""
        with self._lock:
            self._start_time = time.time()
            self._healthy = True
            self._last_health_check = datetime.utcnow()
    
    def cleanup(self):
        """Cleanup resources"""
        with self._lock:
            self._healthy = False
    
    def is_healthy(self) -> bool:
        """Check if metrics collector is healthy"""
        return self._healthy
    
    def record_request(self, method: str, path: str, status_code: int, duration_seconds: float):
        """Record HTTP request metrics"""
        with self._lock:
            self._requests_total += 1
            
            if 200 <= status_code < 400:
                self._requests_success += 1
                self._counters[f"requests_success_total"] += 1
            else:
                self._requests_failed += 1
                self._counters[f"requests_failed_total"] += 1
            
            # Track request duration
            self._request_durations.append(duration_seconds)
            self._histograms[f"request_duration_seconds"].append(duration_seconds)
            
            # Keep only recent durations (last 1000)
            if len(self._request_durations) > 1000:
                self._request_durations = self._request_durations[-1000:]
            
            # Update gauges
            self._gauges["requests_total"] = self._requests_total
            self._gauges["requests_success"] = self._requests_success
            self._gauges["requests_failed"] = self._requests_failed
            
            # Calculate average duration
            if self._request_durations:
                self._gauges["avg_request_duration_seconds"] = sum(self._request_durations) / len(self._request_durations)
    
    def record_directory_processing(self, files_processed: int, records_processed: int, 
                                  success: bool, duration_seconds: float):
        """Record directory processing metrics"""
        with self._lock:
            metric = ProcessingMetric(
                operation_type="directory_processing",
                duration_seconds=duration_seconds,
                success=success,
                files_count=files_processed,
                records_count=records_processed
            )
            self._processing_metrics.append(metric)
            
            if success:
                self._counters["directory_processing_success_total"] += 1
                self._files_processed_total += files_processed
                self._records_processed_total += records_processed
            else:
                self._counters["directory_processing_failed_total"] += 1
            
            # Update processing histograms
            self._histograms["processing_duration_seconds"].append(duration_seconds)
            self._histograms["files_per_operation"].append(files_processed)
            self._histograms["records_per_operation"].append(records_processed)
            
            # Update gauges
            self._gauges["files_processed_total"] = self._files_processed_total
            self._gauges["records_processed_total"] = self._records_processed_total
    
    def record_file_processing(self, file_name: str, records_processed: int, 
                             success: bool, duration_seconds: float):
        """Record single file processing metrics"""
        with self._lock:
            metric = ProcessingMetric(
                operation_type="file_processing",
                duration_seconds=duration_seconds,
                success=success,
                files_count=1,
                records_count=records_processed
            )
            self._processing_metrics.append(metric)
            
            if success:
                self._counters["file_processing_success_total"] += 1
                self._files_processed_total += 1
                self._records_processed_total += records_processed
            else:
                self._counters["file_processing_failed_total"] += 1
            
            # Update gauges
            self._gauges["files_processed_total"] = self._files_processed_total
            self._gauges["records_processed_total"] = self._records_processed_total
    
    def record_processing_error(self, operation_type: str, error_message: str):
        """Record processing error"""
        with self._lock:
            self._processing_errors.append(f"{operation_type}: {error_message}")
            self._counters[f"{operation_type}_errors_total"] += 1
            
            # Keep only recent errors (last 100)
            if len(self._processing_errors) > 100:
                self._processing_errors = self._processing_errors[-100:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self._lock:
            uptime_seconds = time.time() - self._start_time
            
            # Calculate processing rates
            files_per_second = self._files_processed_total / uptime_seconds if uptime_seconds > 0 else 0
            records_per_second = self._records_processed_total / uptime_seconds if uptime_seconds > 0 else 0
            
            # Calculate success rates
            total_operations = len(self._processing_metrics)
            successful_operations = sum(1 for m in self._processing_metrics if m.success)
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            # Processing efficiency assessment
            avg_processing_time = self._calculate_average_processing_time()
            efficiency = self._assess_processing_efficiency(avg_processing_time)
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            return {
                # Basic metrics
                "uptime_seconds": uptime_seconds,
                "total_requests": self._requests_total,
                "successful_requests": self._requests_success,
                "failed_requests": self._requests_failed,
                "avg_processing_time": self._gauges.get("avg_request_duration_seconds", 0.0),
                
                # Processing metrics
                "total_files_processed": self._files_processed_total,
                "total_records_processed": self._records_processed_total,
                "files_per_second": files_per_second,
                "records_per_second": records_per_second,
                "success_rate": success_rate,
                "processing_efficiency": efficiency,
                "recommendations": recommendations,
                
                # Detailed metrics
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "recent_errors": list(self._processing_errors),
                
                # Health
                "healthy": self._healthy,
                "last_health_check": self._last_health_check.isoformat()
            }
    
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        with self._lock:
            lines = []
            
            # Add help and type information
            lines.append("# HELP report_generator_uptime_seconds Service uptime")
            lines.append("# TYPE report_generator_uptime_seconds gauge")
            lines.append(f"report_generator_uptime_seconds {time.time() - self._start_time}")
            
            lines.append("# HELP report_generator_requests_total Total HTTP requests")
            lines.append("# TYPE report_generator_requests_total counter")
            lines.append(f"report_generator_requests_total {self._requests_total}")
            
            lines.append("# HELP report_generator_files_processed_total Total files processed")
            lines.append("# TYPE report_generator_files_processed_total counter")
            lines.append(f"report_generator_files_processed_total {self._files_processed_total}")
            
            lines.append("# HELP report_generator_records_processed_total Total records processed")
            lines.append("# TYPE report_generator_records_processed_total counter")
            lines.append(f"report_generator_records_processed_total {self._records_processed_total}")
            
            # Add counter metrics
            for name, value in self._counters.items():
                lines.append(f"# TYPE report_generator_{name} counter")
                lines.append(f"report_generator_{name} {value}")
            
            # Add gauge metrics
            for name, value in self._gauges.items():
                lines.append(f"# TYPE report_generator_{name} gauge")
                lines.append(f"report_generator_{name} {value}")
            
            return "\n".join(lines)
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health-specific metrics"""
        with self._lock:
            recent_errors = len([e for e in self._processing_errors 
                               if "error" in e.lower() or "failed" in e.lower()])
            
            return {
                "healthy": self._healthy,
                "uptime_seconds": time.time() - self._start_time,
                "recent_error_count": recent_errors,
                "success_rate": self._calculate_success_rate(),
                "avg_response_time": self._gauges.get("avg_request_duration_seconds", 0.0),
                "last_health_check": self._last_health_check.isoformat()
            }
    
    def reset_metrics(self):
        """Reset all metrics (for testing)"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._processing_metrics.clear()
            self._request_durations.clear()
            self._processing_errors.clear()
            
            self._requests_total = 0
            self._requests_success = 0
            self._requests_failed = 0
            self._files_processed_total = 0
            self._records_processed_total = 0
            
            self._start_time = time.time()
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time for recent operations"""
        if not self._processing_metrics:
            return 0.0
        
        recent_operations = [m for m in self._processing_metrics 
                           if m.timestamp > datetime.utcnow() - timedelta(hours=1)]
        
        if not recent_operations:
            return 0.0
        
        return sum(op.duration_seconds for op in recent_operations) / len(recent_operations)
    
    def _assess_processing_efficiency(self, avg_time: float) -> str:
        """Assess processing efficiency based on average time"""
        if avg_time < 5:
            return "excellent"
        elif avg_time < 15:
            return "good"
        elif avg_time < 30:
            return "moderate"
        else:
            return "slow"
    
    def _calculate_success_rate(self) -> float:
        """Calculate recent success rate"""
        if not self._processing_metrics:
            return 100.0
        
        recent_operations = [m for m in self._processing_metrics 
                           if m.timestamp > datetime.utcnow() - timedelta(hours=1)]
        
        if not recent_operations:
            return 100.0
        
        successful = sum(1 for op in recent_operations if op.success)
        return (successful / len(recent_operations)) * 100
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations based on metrics"""
        recommendations = []
        
        # Check success rate
        success_rate = self._calculate_success_rate()
        if success_rate < 95:
            recommendations.append("Success rate below 95% - investigate processing errors")
        
        # Check processing time
        avg_time = self._calculate_average_processing_time()
        if avg_time > 30:
            recommendations.append("High processing times detected - consider optimizing data operations")
        
        # Check error frequency
        recent_errors = len(self._processing_errors)
        if recent_errors > 10:
            recommendations.append("High error frequency - review input data quality")
        
        # Check memory usage (approximate)
        if len(self._processing_metrics) > 800:
            recommendations.append("Consider increasing retention settings or implementing data archival")
        
        return recommendations
