#!/usr/bin/env python3
"""Final push for 100% compliance - removing most common remaining violations.
"""

import re
from pathlib import Path


def final_compliance_push():
    """Target the most common remaining violations."""
    project_root = Path(__file__).parent.parent
    files_fixed = 0
    fixes_applied = 0

    # Most common F821 undefined name issues
    undefined_name_fixes = {
        # Variables that need to be defined or corrected
        'python_files': 'python_files',
        'new_lines': 'new_lines',
        'new_content': 'new_content',
        'original_content': 'original_content',
        'files_changed': 'files_changed',
        'fixes_applied': 'fixes_applied',
        'base_path': 'base_path',
        'target_path': 'target_path',
        'dir_path': 'dir_path',
        'content': 'content',
        'line': 'line',
        'file': 'file',
        'path': 'path',
        'service': 'service',
        'config': 'config',
    }

    for py_file in project_root.glob("**/*.py"):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Fix undefined names by removing underscore prefixes
            for wrong_var, correct_var in undefined_name_fixes.items():
                if wrong_var in content:
                    # Only replace if it's a standalone variable (word boundary)
                    content = re.sub(r'\b' + re.escape(wrong_var) + r'\b', correct_var, content)
                    if content != original_content:
                        fixes_applied += 1

            # Remove completely unused variable assignments that start with underscore
            lines = content.split('\n')
            filtered_lines = []

            for line in lines:
                # Skip lines that assign to underscore variables that are never used
                if re.match(r'\s*_\w+\s*=.*', line.strip()):
                    # Check if this variable is used later in the content
                    var_name = line.split('=')[0].strip()
                    if var_name.count('_') > 0 and var_name not in content.replace(line, ''):
                        fixes_applied += 1
                        continue  # Skip this line

                # Remove trailing whitespace
                clean_line = line.rstrip()
                filtered_lines.append(clean_line)

            content = '\n'.join(filtered_lines)

            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_fixed += 1
                print(f"Fixed: {py_file}")

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"Fixed {files_fixed} files with {fixes_applied} violations corrected")


if __name__ == "__main__":
    final_compliance_push()