"""
demo_enhanced_excel_operations.py
---------------------------------
Demonstrates the enhanced Excel operations with incremental updates, custom reports, and summaries.

This script shows:
- Incremental Excel updates for hourly data
- Custom report generation with flexible formatting
- End-of-day summary reports with metadata
- Workbook manipulation and data merging

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import sys
import os
import tempfile
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_writer import ExcelWriter


def create_sample_hourly_data():
    """Create sample data for different hours"""
    
    # Hour 9 data
    hour_9_data = {
        'IB_Calls': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'Handle': [45, 38, 52],
            'Avg Handle': ['00:02:15', '00:01:58', '00:02:45'],
            'Hour': [9, 9, 9]
        })],
        'Dials': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'Handle': [120, 98, 135],
            'Avg Handle': ['00:01:30', '00:01:22', '00:01:45'],
            'Hour': [9, 9, 9]
        })]
    }
    
    # Hour 10 data
    hour_10_data = {
        'IB_Calls': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
            'Handle': [52, 41, 48, 39],
            'Avg Handle': ['00:02:20', '00:02:05', '00:02:30', '00:01:55'],
            'Hour': [10, 10, 10, 10]
        })],
        'Dials': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
            'Handle': [115, 103, 127, 89],
            'Avg Handle': ['00:01:25', '00:01:35', '00:01:40', '00:01:18'],
            'Hour': [10, 10, 10, 10]
        })]
    }
    
    # Hour 11 data
    hour_11_data = {
        'IB_Calls': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
            'Handle': [48, 43, 51, 44],
            'Avg Handle': ['00:02:10', '00:02:12', '00:02:35', '00:02:00'],
            'Hour': [11, 11, 11, 11]
        })],
        'Productivity': [pd.DataFrame({
            'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
            'Logged In': ['08:00:00', '08:15:00', '08:00:00', '08:30:00'],
            'On Queue': ['07:45:00', '08:00:00', '07:30:00', '08:15:00'],
            'Idle': ['00:15:00', '00:15:00', '00:30:00', '00:15:00'],
            'Hour': [11, 11, 11, 11]
        })]
    }
    
    return hour_9_data, hour_10_data, hour_11_data


def demo_incremental_excel_updates():
    """Demonstrate incremental Excel updates"""
    print("=== Incremental Excel Updates Demo ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = ExcelWriter(output_dir=temp_dir)
        
        # Get sample data
        hour_9_data, hour_10_data, hour_11_data = create_sample_hourly_data()
        
        date_str = '2025-07-28'
        
        print("1. Creating initial daily file with Hour 9 data...")
        daily_file = writer.write_incremental(hour_9_data, date_str, '2025-07-28_09')
        print(f"   ✓ Created: {os.path.basename(daily_file)}")
        
        print("\n2. Adding Hour 10 data incrementally...")
        daily_file = writer.write_incremental(hour_10_data, date_str, '2025-07-28_10')
        print(f"   ✓ Updated: {os.path.basename(daily_file)}")
        
        print("\n3. Adding Hour 11 data with new sheet (Productivity)...")
        daily_file = writer.write_incremental(hour_11_data, date_str, '2025-07-28_11')
        print(f"   ✓ Updated: {os.path.basename(daily_file)}")
        
        # Verify the final file
        print(f"\n4. Analyzing final incremental file...")
        try:
            final_data = pd.read_excel(daily_file, sheet_name=None)
            print(f"   Sheets in file: {list(final_data.keys())}")
            
            for sheet_name, df in final_data.items():
                print(f"   Sheet '{sheet_name}': {len(df)} rows")
                if 'Hour' in df.columns:
                    hours = sorted(df['Hour'].unique())
                    print(f"     Hours covered: {hours}")
                
        except Exception as e:
            print(f"   Error reading file: {e}")


def demo_custom_report_generation():
    """Demonstrate custom report generation"""
    print("\n=== Custom Report Generation Demo ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = ExcelWriter(output_dir=temp_dir)
        
        # Create custom report data
        custom_data = {
            'Agent_Performance': [pd.DataFrame({
                'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
                'Total_Calls': [145, 123, 156, 132],
                'Avg_Handle_Time': ['00:02:15', '00:02:02', '00:02:37', '00:01:58'],
                'Quality_Score': [94.5, 97.2, 91.8, 95.1],
                'Department': ['Sales', 'Support', 'Sales', 'Support']
            })],
            'Department_Summary': [pd.DataFrame({
                'Department': ['Sales', 'Support'],
                'Total_Agents': [2, 2],
                'Total_Calls': [301, 255],
                'Avg_Quality': [93.15, 96.15],
                'Peak_Hour': ['10:00-11:00', '09:00-10:00']
            })],
            'Hourly_Trends': [pd.DataFrame({
                'Hour': [9, 10, 11, 12, 13, 14, 15, 16],
                'Total_Calls': [189, 206, 194, 178, 165, 172, 158, 143],
                'Avg_Wait_Time': [45, 38, 42, 52, 48, 41, 47, 51],
                'Agent_Utilization': [87.5, 92.3, 89.1, 85.6, 82.4, 86.7, 83.2, 79.8]
            })]
        }
        
        print("1. Generating custom performance report...")
        custom_file = writer.write_custom(custom_data, 'custom_performance_report_20250728.xlsx')
        print(f"   ✓ Created: {os.path.basename(custom_file)}")
        
        print("\n2. Generating on-demand filtered report...")
        # Filter data for just Sales department
        sales_data = {
            'Sales_Agents': [custom_data['Agent_Performance'][0][
                custom_data['Agent_Performance'][0]['Department'] == 'Sales'
            ]],
            'Sales_Trends': [custom_data['Hourly_Trends'][0]]  # Full hourly data
        }
        
        timestamp = datetime.now().strftime('%H%M%S')
        ondemand_file = writer.write_custom(sales_data, f'ondemand_sales_report_{timestamp}.xlsx')
        print(f"   ✓ Created: {os.path.basename(ondemand_file)}")
        
        # Verify custom files
        print(f"\n3. Analyzing custom reports...")
        for file_path, report_type in [(custom_file, 'Performance'), (ondemand_file, 'Sales')]:
            try:
                data = pd.read_excel(file_path, sheet_name=None)
                print(f"   {report_type} Report:")
                print(f"     Sheets: {list(data.keys())}")
                total_rows = sum(len(df) for df in data.values())
                print(f"     Total data rows: {total_rows}")
            except Exception as e:
                print(f"     Error reading {report_type} report: {e}")


def demo_end_of_day_summary():
    """Demonstrate end-of-day summary generation"""
    print("\n=== End-of-Day Summary Demo ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = ExcelWriter(output_dir=temp_dir)
        
        # Create comprehensive daily data
        all_data = {
            'IB_Calls': [pd.DataFrame({
                'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'] * 8,
                'Handle': [45, 38, 52, 39] * 8,
                'Avg Handle': ['00:02:15', '00:01:58', '00:02:45', '00:01:55'] * 8,
                'Hour': [h for h in range(9, 17) for _ in range(4)],
                'Date': ['2025-07-28'] * 32
            })],
            'Dials': [pd.DataFrame({
                'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'] * 8,
                'Handle': [120, 98, 135, 89] * 8,
                'Avg Handle': ['00:01:30', '00:01:22', '00:01:45', '00:01:18'] * 8,
                'Hour': [h for h in range(9, 17) for _ in range(4)],
                'Date': ['2025-07-28'] * 32
            })],
            'Productivity': [pd.DataFrame({
                'Agent Name': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown'],
                'Logged In': ['08:00:00', '08:15:00', '08:00:00', '08:30:00'],
                'On Queue': ['07:45:00', '08:00:00', '07:30:00', '08:15:00'],
                'Idle': ['00:15:00', '00:15:00', '00:30:00', '00:15:00'],
                'Off Queue': ['00:15:00', '00:15:00', '00:30:00', '00:15:00'],
                'Date': ['2025-07-28'] * 4
            })]
        }
        
        # Add metadata
        metadata_df = pd.DataFrame({
            'Metric': [
                'Report Date',
                'Data Sources',
                'Total Records',
                'Time Range',
                'Agents Included',
                'Generated At'
            ],
            'Value': [
                '2025-07-28',
                'Email Attachments, Directory Scan',
                str(sum(len(df) for df_list in all_data.values() for df in df_list)),
                '09:00 - 17:00',
                '4 Active Agents',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        })
        
        enhanced_data = dict(all_data)
        enhanced_data['Report_Metadata'] = [metadata_df]
        
        print("1. Generating end-of-day summary with metadata...")
        summary_file = writer.write_summary(enhanced_data, 'eod_summary_20250728.xlsx')
        print(f"   ✓ Created: {os.path.basename(summary_file)}")
        
        print("\n2. Analyzing summary report structure...")
        try:
            # Read all sheets
            summary_data = pd.read_excel(summary_file, sheet_name=None)
            print(f"   Sheets in summary: {list(summary_data.keys())}")
            
            # Show metadata if available
            if 'Summary' in summary_data:
                print(f"   Metadata rows: {len(summary_data['Summary'])}")
                print("   Key metrics:")
                for _, row in summary_data['Summary'].head(3).iterrows():
                    print(f"     {row['Metric']}: {row['Value']}")
            
            # Show data sheets
            data_sheets = [s for s in summary_data.keys() if s != 'Summary']
            for sheet in data_sheets:
                df = summary_data[sheet]
                print(f"   {sheet}: {len(df)} rows")
                if 'Hour' in df.columns:
                    hours_covered = sorted(df['Hour'].unique())
                    print(f"     Hours: {min(hours_covered)} - {max(hours_covered)}")
                    
        except Exception as e:
            print(f"   Error analyzing summary: {e}")


def demo_error_handling_and_edge_cases():
    """Demonstrate error handling in Excel operations"""
    print("\n=== Error Handling Demo ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        writer = ExcelWriter(output_dir=temp_dir)
        
        print("1. Testing empty data handling...")
        empty_result = writer.write({}, '2025-07-28')
        print(f"   Empty data result: {empty_result}")
        
        print("\n2. Testing incremental update with empty data...")
        empty_incremental = writer.write_incremental({}, '2025-07-28', '2025-07-28_09')
        print(f"   Empty incremental result: {empty_incremental}")
        
        print("\n3. Testing custom report with minimal data...")
        minimal_data = {
            'Single_Record': [pd.DataFrame({
                'Column1': ['Value1'],
                'Column2': ['Value2']
            })]
        }
        minimal_file = writer.write_custom(minimal_data, 'minimal_report.xlsx')
        print(f"   ✓ Minimal report created: {os.path.basename(minimal_file)}")
        
        print("\n4. Testing summary with metadata only...")
        metadata_only = {
            'Report_Metadata': [pd.DataFrame({
                'Info': ['Test'],
                'Value': ['Demo']
            })]
        }
        metadata_file = writer.write_summary(metadata_only, 'metadata_only.xlsx')
        print(f"   ✓ Metadata-only summary: {os.path.basename(metadata_file)}")


def demo_performance_metrics():
    """Show performance characteristics"""
    print("\n=== Performance Characteristics ===\n")
    
    print("1. Incremental Updates:")
    print("   - Loads existing workbook for appending")
    print("   - Merges new data with existing sheets")
    print("   - Preserves data from previous hours")
    print("   - Memory efficient for large daily files")
    
    print("\n2. Custom Reports:")
    print("   - Creates new workbook each time")
    print("   - Flexible sheet structure")
    print("   - Supports filtered/transformed data")
    print("   - Fast generation for on-demand requests")
    
    print("\n3. Summary Reports:")
    print("   - Enhanced formatting with metadata")
    print("   - Statistics calculations per sheet")
    print("   - Comprehensive data overview")
    print("   - Professional report presentation")
    
    print("\n4. Error Recovery:")
    print("   - Graceful handling of missing files")
    print("   - Automatic directory creation")
    print("   - Transaction-like operations")
    print("   - Detailed error logging")


if __name__ == "__main__":
    print("Enhanced Excel Operations Demo")
    print("=" * 50)
    
    demo_incremental_excel_updates()
    demo_custom_report_generation()
    demo_end_of_day_summary()
    demo_error_handling_and_edge_cases()
    demo_performance_metrics()
    
    print(f"\nDemo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNote: This demo creates temporary Excel files.")
    print("In production, files are saved to the configured output directory.")
