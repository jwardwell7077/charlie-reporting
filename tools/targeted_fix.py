#!/usr/bin/env python3
"""Targeted fix for specific F821/F841 violations.
"""

import re
from pathlib import Path


def fix_specific_violations():
    """Fix specific patterns causing violations."""
    project_root = Path(__file__).parent.parent
    files_fixed = 0

    # Common F821 fixes - undefined variables
    f821_fixes = [
        # Variable name mismatches
        ('SERVICES_AVAILABLE', 'SERVICES_AVAILABLE'),
        ('services_path', 'services_path'),
        ('python_files', 'python_files'),
        ('new_lines', 'new_lines'),
        ('new_content', 'new_content'),
        ('original_content', 'original_content'),
        ('files_changed', 'files_changed'),
        ('base_path', 'base_path'),
        ('dir_path', 'dir_path'),
        ('init_file', 'init_file'),
        ('model_file', 'model_file'),
        ('target_path', 'target_path'),

        # Common spacing issues in variable names
        ('csv_processor', 'csv_processor'),  # Make sure it's consistent
        ('excel_generator', 'excel_generator'),
        ('email_processor', 'email_processor'),
    ]

    # F841 fixes - variable name consistency (remove underscores where inappropriate)
    f841_fixes = [
        ('csv_processor = ', 'csv_processor = '),
        ('excel_generator = ', 'excel_generator = '),
        ('email_processor = ', 'email_processor = '),
    ]

    for py_file in project_root.glob("**/*.py"):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply F821 fixes
            for wrong, correct in f821_fixes:
                if wrong in content and wrong != correct:
                    content = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, content)

            # Apply F841 fixes
            for wrong, correct in f841_fixes:
                content = content.replace(wrong, correct)

            # Remove trailing whitespace
            lines = content.split('\n')
            clean_lines = [line.rstrip() for line in lines]
            content = '\n'.join(clean_lines)

            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_fixed += 1
                print(f"Fixed: {py_file}")

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"Fixed {files_fixed} files")


if __name__ == "__main__":
    fix_specific_violations()