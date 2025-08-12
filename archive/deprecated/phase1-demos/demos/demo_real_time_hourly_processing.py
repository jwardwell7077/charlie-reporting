"""
demo_real_time_hourly_processing.py
-----------------------------------
Demonstrates the real - time hourly processing capabilities of the enhanced EmailFetcher and ReportProcessor.

This script shows:
- Hourly email fetching with timestamped filenames
- Incremental Excel updates for each hour
- On - demand report generation
- Continuous processing mode

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import ReportProcessor
from config_loader import ConfigLoader


def demo_hourly_processing():
    """Demonstrate hourly processing capabilities"""
    print("=== Real - time Hourly Processing Demo ===\n")

    try:
        # Load configuration
        config = ConfigLoader()
        processor = ReportProcessor(config)

        print("1. Processing current hour...")
        currenthour_data = processor.process_hourly()
        if current_hour_data:
            print(f"   ✓ Processed {len(current_hour_data)} datasets for current hour")
            print(f"   ✓ Last processed time: {processor.last_processed_time}")
        else:
            print("   ℹ No new data found for current hour")

        print("\n2. Processing specific hour (2 hours ago)...")
        twohours_ago = datetime.now() - timedelta(hours=2)
        specifichour_data = processor.process_hourly(two_hours_ago)
        if specific_hour_data:
            print(f"   ✓ Processed {len(specific_hour_data)} datasets for {two_hours_ago.strftime('%Y-%m-%d %H:00')}")
        else:
            print(f"   ℹ No data found for {two_hours_ago.strftime('%Y-%m-%d %H:00')}")

        print("\n3. Generating on - demand report for today...")
        today = datetime.now().strftime('%Y-%m-%d')
        reportpath = processor.generate_on_demand_report(today)
        if report_path:
            print(f"   ✓ On - demand report generated: {report_path}")
        else:
            print("   ℹ No data available for on - demand report")

        print("\n4. Generating end - of - day summary...")
        summarypath = processor.generate_end_of_day_summary(today)
        if summary_path:
            print(f"   ✓ End - of - day summary generated: {summary_path}")
        else:
            print("   ℹ No data available for summary")

        print("\n5. Demonstrating continuous processing (simulated)...")
        print("   ℹ In production, you would run:")
        print("   processor.run_continuous_processing(interval_minutes=60)")
        print("   This would process new data every hour automatically")

    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


def demo_command_line_interface():
    """Demonstrate command - line interface options"""
    print("\n=== Command - line Interface Demo ===\n")

    print("Available command - line options:")
    print("1. Hourly processing:")
    print("   python src / main.py --mode hourly")
    print("   python src / main.py --mode hourly --datetime '2025 - 07 - 28 14:00:00'")

    print("\n2. On - demand reports:")
    print("   python src / main.py --mode ondemand --date 2025 - 07 - 28")
    print("   python src / main.py --mode ondemand --date 2025 - 07 - 28 --types IB_Calls,Dials")

    print("\n3. End - of - day summaries:")
    print("   python src / main.py --mode eod --date 2025 - 07 - 28")

    print("\n4. Continuous processing:")
    print("   python src / main.py --mode continuous --interval 60")


if __name__ == "__main__":
    print("Real - time Hourly Processing Demo")
    print("=" * 50)

    demo_hourly_processing()
    demo_command_line_interface()

    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")