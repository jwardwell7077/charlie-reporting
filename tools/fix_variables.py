#!/usr/bin/env python3
"""Targeted fix for specific F821/F841 variable naming issues.
"""

import re
from pathlib import Path


def fix_variable_issues():
    """Fix specific variable naming consistency issues."""
    service_root = Path(__file__).parent.parent / 'services' / 'report-generator'
    fixes_applied = 0
    
    # Specific variable name fixes needed
    variable_fixes = {
        'coveragefile': 'coverage_file',
        'coveragedata': 'coverage_data', 
        'totalcoverage': 'total_coverage',
        'validationdata': 'validation_data',
        'testdata': 'test_data',
        'resultdata': 'result_data',
        'configvalue': 'config_value',
        'csvfile': 'csv_file',
        'excelfile': 'excel_file',
        'filepath': 'file_path',
        'dirname': 'dir_name',
        'filename': 'file_name',
        'testresult': 'test_result',
        'errormsg': 'error_msg',
        'successmsg': 'success_msg',
        'interfacesexist': 'interfaces_exist',
        'implementationsexist': 'implementations_exist',
        'testsexist': 'tests_exist',
        'businessisolated': 'business_isolated',
        'testresults': 'test_results',
        'architecturechecks': 'architecture_checks',
        'projectsummary': 'project_summary',
        'architecturescore': 'architecture_score',
        'testscore': 'test_score',
        'overallscore': 'overall_score',
        'performancedata': 'performance_data',
        'metricsdata': 'metrics_data',
        'logdata': 'log_data',
        'outputdata': 'output_data',
        'inputdata': 'input_data',
    }
    
    for py_file in service_root.glob("**/*.py"):
        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply variable name fixes
            for wrong_var, correct_var in variable_fixes.items():
                if wrong_var in content:
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(wrong_var) + r'\b'
                    content = re.sub(pattern, correct_var, content)
            
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes_applied += 1
                print(f"Fixed variables in: {py_file.relative_to(service_root)}")
                
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    print(f"Applied variable fixes to {fixes_applied} files")


if __name__ == "__main__":
    fix_variable_issues()
