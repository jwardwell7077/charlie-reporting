#!/usr/bin/env python3
"""Fix variable naming inconsistencies causing F821/F841 violations.
"""

import re
from pathlib import Path


def fix_variable_naming():
    """Fix variable naming issues systematically."""
    project_root = Path(__file__).parent.parent
    files_fixed = 0

    # Mapping of incorrect variable names to correct ones
    variable_fixes = {
        # F821 - undefined names (using wrong variable name)
        'infra_dir': 'infra_dir',
        'init_dirs': 'init_dirs',
        'requirements_content': 'requirements_content',
        'config_content': 'config_content',
        'readme_content': 'readme_content',
        'service_models': 'service_models',
        'model_file': 'model_file',
        'target_path': 'target_path',
        'transformed_content': 'transformed_content',
        'transform_func': 'transform_func',
        'shared_source': 'shared_source',
        'shared_link': 'shared_link',
        'exit_code': 'exit_code',
        'python_files': 'python_files',
        'new_lines': 'new_lines',
        'original_content': 'original_content',
        'new_content': 'new_content',
        'files_changed': 'files_changed',
        'fixes_applied': 'fixes_applied',
        'base_path': 'base_path',
        'dir_path': 'dir_path',
        'init_file': 'init_file',
    }

    for py_file in project_root.glob("**/*.py"):
        if any(exclude in str(py_file) for exclude in ['.venv', '__pycache__', '.git']):
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply variable name fixes
            for wrong_name, correct_name in variable_fixes.items():
                # Replace variable assignments
                content = re.sub(r'\b' + re.escape(wrong_name) + r'\b', correct_name, content)

            # Remove trailing whitespace from all lines
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

    print(f"Fixed variable naming in {files_fixed} files")


if __name__ == "__main__":
    fix_variable_naming()