#!/usr/bin/env python3
"""
Variable Naming Standardization Script
Systematically fixes variable naming violations in the report-generator service.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple


# Define the variable naming patterns to fix
NAMING_FIXES = {
    # Common concatenated patterns → snake_case
    'csvfiles': 'csv_files',
    'configdict': 'config_dict',
    'processingtime': 'processing_time',
    'taskid': 'task_id',
    'archivepath': 'archive_path',
    'errorcount': 'error_count',
    'successrate': 'success_rate',
    'outputfile': 'output_file',
    'inputdata': 'input_data',
    'resultset': 'result_set',
    'filepath': 'file_path',
    'filename': 'file_name',
    'dirname': 'dir_name',
    'tempfile': 'temp_file',
    'logfile': 'log_file',
    
    # File and path variables
    'inputfilepath': 'input_file_path',
    'outputfilepath': 'output_file_path',
    'tempfilepath': 'temp_file_path',
    'excelfilename': 'excel_file_name',
    'outputfilename': 'output_file_name',
    'archivepath': 'archive_path',
    'outputdirectory': 'output_directory',
    'inputdirectory': 'input_directory',
    
    # Collection variables
    'discoveredfiles': 'discovered_files',
    'matchedfiles': 'matched_files',
    'failedfiles': 'failed_files',
    'transformationresults': 'transformation_results',
    'errormessages': 'error_messages',
    'configsettings': 'config_settings',
    'archivedfiles': 'archived_files',
    'reportsheets': 'report_sheets',
    
    # Time and processing variables
    'starttime': 'start_time',
    'endtime': 'end_time',
    'createdat': 'created_at',
    'completedat': 'completed_at',
    'processingduration': 'processing_duration',
    'processingstart': 'processing_start',
    'processingend': 'processing_end',
    
    # Configuration variables
    'transformconfig': 'transform_config',
    'excelconfig': 'excel_config',
    'databaseconfig': 'database_config',
    'loggingconfig': 'logging_config',
    'appconfig': 'app_config',
    
    # Status and result variables
    'taskstatus': 'task_status',
    'processingresult': 'processing_result',
    'validationresult': 'validation_result',
    'successcount': 'success_count',
    'failurecount': 'failure_count',
    'errormessage': 'error_message',
    'taskresult': 'task_result',
    
    # Service variables
    'csvservice': 'csv_service',
    'excelservice': 'excel_service',
    'filemanager': 'file_manager',
    'configmanager': 'config_manager',
    'metricscollector': 'metrics_collector',
    
    # Validation and Excel specific
    'excelvalidation': 'excel_validation',
    'excelcontent': 'excel_content',
    'excelpath': 'excel_path',
    'exceldata': 'excel_data',
    
    # Request/response variables
    'requestdata': 'request_data',
    'responsedata': 'response_data',
    'requestid': 'request_id',
    'responseid': 'response_id',
    
    # Background task variables
    'backgroundtasks': 'background_tasks',
    'taskstorage': 'task_storage',
    
    # Infrastructure variables
    'infrafiles': 'infra_files',
    'businessdir': 'business_dir',
    'infrastructuredir': 'infrastructure_dir',
    'testdir': 'test_dir',
    
    # Other common patterns
    'keydirectories': 'key_directories',
    'organizeddirs': 'organized_dirs',
    'doccount': 'doc_count',
    'achievementscore': 'achievement_score',
    'maxpossible': 'max_possible',
    'successrate': 'success_rate',
    'keywins': 'key_wins',
    'nextsteps': 'next_steps',
    'passedtests': 'passed_tests',
    'failedresults': 'failed_results',
    'successfulresults': 'successful_results',
    'cleanupcount': 'cleanup_count',
    'labelparts': 'label_parts',
    'consoleformat': 'console_format',
    'consolehandler': 'console_handler',
    'filehandler': 'file_handler',
    'rawdir': 'raw_dir',
    'uniquefiles': 'unique_files',
}


def get_python_files(directory: Path) -> List[Path]:
    """Get all Python files in the directory recursively."""
    python_files = []
    for file_path in directory.rglob("*.py"):
        if "__pycache__" not in str(file_path):
            python_files.append(file_path)
    return python_files


def find_variable_usage(content: str, old_name: str, new_name: str) -> List[Tuple[int, str]]:
    """Find all lines where the variable is used incorrectly."""
    lines = content.split('\n')
    issues = []
    
    # Pattern to match variable assignments and usage
    patterns = [
        rf'\b{old_name}\s*=',  # Assignment
        rf'=\s*{old_name}\b',  # Used in assignment
        rf'\({old_name}\b',    # Function parameter
        rf'\[{old_name}\b',    # List/dict access
        rf'\.{old_name}\b',    # Attribute access
        rf'\b{old_name}\.',    # Object method call
        rf'\b{old_name}\[',    # Indexing
        rf'\b{old_name}\)',    # Function argument
        rf'\b{old_name},',     # In lists/tuples
        rf',\s*{old_name}\b',  # In lists/tuples
    ]
    
    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                issues.append((line_num, line.strip()))
                break
    
    return issues


def analyze_file(file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
    """Analyze a file for variable naming issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}
    
    file_issues = {}
    
    for old_name, new_name in NAMING_FIXES.items():
        issues = find_variable_usage(content, old_name, new_name)
        if issues:
            file_issues[f"{old_name} → {new_name}"] = issues
    
    return file_issues


def main():
    """Main function to analyze variable naming issues."""
    service_path = Path("services/report-generator")
    
    if not service_path.exists():
        print(f"Service path {service_path} does not exist")
        return
    
    print("🔍 Analyzing variable naming issues in report-generator service...")
    print("=" * 80)
    
    python_files = get_python_files(service_path)
    total_issues = 0
    files_with_issues = 0
    
    for file_path in python_files:
        file_issues = analyze_file(file_path)
        
        if file_issues:
            files_with_issues += 1
            relative_path = file_path.relative_to(service_path)
            print(f"\n📄 {relative_path}")
            print("-" * 60)
            
            for naming_issue, line_issues in file_issues.items():
                print(f"  🔧 {naming_issue}")
                for line_num, line_content in line_issues[:3]:  # Show first 3 occurrences
                    print(f"     Line {line_num}: {line_content}")
                    total_issues += 1
                
                if len(line_issues) > 3:
                    print(f"     ... and {len(line_issues) - 3} more occurrences")
                    total_issues += len(line_issues) - 3
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Files analyzed: {len(python_files)}")
    print(f"Files with naming issues: {files_with_issues}")
    print(f"Total naming violations: {total_issues}")
    
    print("\n🎯 TOP PATTERNS TO FIX:")
    print("-" * 40)
    
    # Count occurrences of each pattern
    pattern_counts = {}
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for old_name, new_name in NAMING_FIXES.items():
                count = len(find_variable_usage(content, old_name, new_name))
                if count > 0:
                    pattern_counts[f"{old_name} → {new_name}"] = pattern_counts.get(f"{old_name} → {new_name}", 0) + count
        except:
            continue
    
    # Show top 10 patterns
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (pattern, count) in enumerate(sorted_patterns[:10], 1):
        print(f"{i:2d}. {pattern:<30} ({count} occurrences)")
    
    print(f"\n📝 Next steps:")
    print("1. Use replace_string_in_file to fix these patterns systematically")
    print("2. Start with the highest-count patterns first")
    print("3. Test after each file to ensure no breaking changes")
    print("4. Use flake8 to validate fixes: flake8 --ignore=C901 . | grep -E 'F821|F841'")


if __name__ == "__main__":
    main()
