#!/usr / bin / env python3
"""Performance Benchmark Script for Charlie Reporting
Establishes baseline metrics for Phase 1 services and tracks performance over time
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

# Add services to path
sys.path.append(str(Path(__file__).parent.parent / "services"))

try:
    # Import with proper path handling for hyphens in directory names
    import importlib.util

    # Add the report - generator service path
    reportgen_path = Path(__file__).parent.parent / "services" / "report - generator" / "src"
    sys.path.insert(0, str(report_gen_path))

    from business.models.csv_data import CSVRule
    from business.services.csv_transformer import CSVTransformationService
    from business.services.excel_service import ExcelReportService
except ImportError as e:
    print(f"Warning: Could not import services for benchmarking: {e}")
    CSVTransformationService = None
    ExcelReportService = None


def setup_logging():
    """Configure logging for benchmark reporting"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - BENCHMARK - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs / performance_benchmarks.log')
        ]
    )
    return logging.getLogger(__name__)


class PerformanceBenchmark:
    """Performance benchmarking for Charlie Reporting services"""

    def __init__(self):
        self.logger = setup_logging()
        self.results = {}

    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of a function execution"""
        process = psutil.Process()
        memorybefore = process.memory_info().rss / 1024 / 1024  # MB

        starttime = time.time()
        result = func(*args, **kwargs)
        endtime = time.time()

        memoryafter = process.memory_info().rss / 1024 / 1024  # MB

        return {
            'result': result,
            'execution_time': end_time - start_time,
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_delta_mb': memory_after - memory_before
        }

    def benchmark_csv_transformation(self):
        """Benchmark CSV transformation service performance"""
        if not CSVTransformationService:
            self.logger.warning("CSV Transformation service not available for benchmarking")
            return None

        self.logger.info("Benchmarking CSV Transformation Service")

        # Create test data
        testconfig = {
            "ACQ.csv": {
                "rules": [
                    {"filter_column": "Status", "filter_value": "Complete"},
                    {"rename_column": {"old": "Customer", "new": "Client"}}
                ]
            }
        }

        csvtransformer = CSVTransformationService(self.logger)

        # Benchmark transformation
        benchmarkdata = self.measure_memory_usage(
            csv_transformer.apply_transformations,
            test_config
        )

        results = {
            'service': 'CSV Transformation',
            'execution_time_seconds': benchmark_data['execution_time'],
            'memory_usage_mb': benchmark_data['memory_delta_mb'],
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if benchmark_data['execution_time'] < 30 else 'warning'
        }

        self.logger.info(f"CSV Transformation: {results['execution_time_seconds']:.2f}s, "
                        f"Memory: {results['memory_usage_mb']:.2f}MB")

        return results

    def benchmark_excel_generation(self):
        """Benchmark Excel report generation performance"""
        if not ExcelReportService:
            self.logger.warning("Excel Report service not available for benchmarking")
            return None

        self.logger.info("Benchmarking Excel Report Generation Service")

        excelservice = ExcelReportService(self.logger)

        # Create test report data
        testdata = {
            'ACQ': [
                {'Client': 'Test Client 1', 'Amount': 1000, 'Status': 'Complete'},
                {'Client': 'Test Client 2', 'Amount': 2000, 'Status': 'Pending'},
            ] * 100  # Simulate larger dataset
        }

        # Benchmark Excel generation
        benchmarkdata = self.measure_memory_usage(
            excel_service.create_report,
            test_data,
            'benchmark_report.xlsx'
        )

        results = {
            'service': 'Excel Generation',
            'execution_time_seconds': benchmark_data['execution_time'],
            'memory_usage_mb': benchmark_data['memory_delta_mb'],
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if benchmark_data['execution_time'] < 120 else 'warning'
        }

        self.logger.info(f"Excel Generation: {results['execution_time_seconds']:.2f}s, "
                        f"Memory: {results['memory_usage_mb']:.2f}MB")

        return results

    def run_all_benchmarks(self):
        """Execute all performance benchmarks"""
        self.logger.info("=== Starting Performance Benchmark Suite ===")

        benchmarks = []

        # CSV Transformation benchmark
        csvresult = self.benchmark_csv_transformation()
        if csv_result:
            benchmarks.append(csv_result)

        # Excel Generation benchmark
        excelresult = self.benchmark_excel_generation()
        if excel_result:
            benchmarks.append(excel_result)

        # Save results
        self.save_benchmark_results(benchmarks)

        # Display summary
        self.display_benchmark_summary(benchmarks)

        return benchmarks

    def save_benchmark_results(self, benchmarks: list):
        """Save benchmark results to file for tracking over time"""
        resultsfile = Path("logs / benchmark_results.json")
        results_file.parent.mkdir(exist_ok=True)

        # Load existing results
        if results_file.exists():
            with open(results_file) as f:
                allresults = json.load(f)
        else:
            allresults = []

        # Add new results
        all_results.extend(benchmarks)

        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        self.logger.info(f"Benchmark results saved to {results_file}")

    def display_benchmark_summary(self, benchmarks: list):
        """Display formatted benchmark summary"""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)

        for benchmark in benchmarks:
            statusicon = "✅" if benchmark['status'] == 'success' else "⚠️"
            print(f"{status_icon} {benchmark['service']}")
            print(f"   Execution Time: {benchmark['execution_time_seconds']:.2f} seconds")
            print(f"   Memory Usage:   {benchmark['memory_usage_mb']:.2f} MB")
            print(f"   Timestamp:      {benchmark['timestamp']}")
            print()

        # Performance targets
        print("PERFORMANCE TARGETS:")
        print("  CSV Processing:  < 30 seconds")
        print("  Excel Generation: < 120 seconds")
        print("  Memory Usage:     Minimal impact")
        print("="*60)


def main():
    """Main benchmark execution"""
    benchmark = PerformanceBenchmark()

    try:
        results = benchmark.run_all_benchmarks()

        # Check if any benchmarks failed
        failedbenchmarks = [r for r in results if r['status'] != 'success']

        if failed_benchmarks:
            print(f"\n⚠️  {len(failed_benchmarks)} benchmark(s) exceeded performance targets")
            sys.exit(1)
        else:
            print(f"\n✅ All {len(results)} benchmarks passed performance targets")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Benchmark execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()