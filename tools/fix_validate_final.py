#!/usr/bin/env python3
"""
Fix validate_final.py variable naming issues specifically.
"""

import re
from pathlib import Path


def fix_validate_final():
    """Fix variable naming issues in validate_final.py."""
    file_path = Path("services/report-generator/validate_final.py")
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Variable name fixes specific to this file
    variable_fixes = {
        'testcode': 'test_code',
        'srcpath': 'src_path',
        'interfacescode': 'interfaces_code',
        'businessdir': 'business_dir',
        'infrastructuredir': 'infrastructure_dir',
        'testsdir': 'tests_dir',
        'requiredfiles': 'required_files',
        'orgscore': 'org_score',
        'passedcriteria': 'passed_criteria',
        'completioncriteria': 'completion_criteria',
        'validationresults': 'validation_results',
        'successfulchecks': 'successful_checks',
        'totalchecks': 'total_checks',
        'finalscore': 'final_score',
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply variable name fixes using word boundaries
        for wrong, correct in variable_fixes.items():
            pattern = r'\b' + re.escape(wrong) + r'\b'
            content = re.sub(pattern, correct, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed variable names in {file_path}")
            return True
        else:
            print(f"No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


if __name__ == "__main__":
    fix_validate_final()
