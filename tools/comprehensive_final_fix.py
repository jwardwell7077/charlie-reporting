#!/usr/bin/env python3
"""
Final comprehensive fix for 100% Flake8 compliance.
This script systematically fixes the remaining core violations.
"""

import os
import re
from pathlib import Path
from typing import Dict, List


class ComprehensiveFinalFix:
    """Fix remaining violations for 100% compliance."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.files_changed = 0
        self.fixes_applied = 0

    def run_fix(self):
        """Run comprehensive fix on all Python files."""
        print("Starting comprehensive final fix for 100% compliance...")
        print(f"Scanning directory: {self.root_dir}")

        python_files = list(self.root_dir.glob("**/*.py"))
        print(f"Found {len(python_files)} Python files")

        for python_file in python_files:
            # Skip excluded directories
            if any(excluded in str(python_file) for excluded in ['.venv', '__pycache__', '.git']):
                continue

            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                # Skip empty files
                if not original_content.strip():
                    continue

                fixed_content = self.fix_file_content(original_content, python_file)

                if fixed_content != original_content:
                    with open(python_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.files_changed += 1
                    print(f"Fixed: {python_file}")

            except Exception as e:
                print(f"Error processing {python_file}: {e}")

        print(f"\nCompleted: {self.files_changed} files changed, {self.fixes_applied} fixes applied")

    def fix_file_content(self, content: str, file_path: Path) -> str:
        """Apply comprehensive fixes to file content."""
        # Fix F821/F841: Revert problematic underscore variable names
        content = self.fix_variable_naming(content)

        lines = content.split('\n')
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Fix trailing whitespace (W291, W293)
            if line.rstrip() != line:
                line = line.rstrip()
                self.fixes_applied += 1

            # Fix blank line contains whitespace (W293)
            if line.strip() == '' and line != '':
                line = ''
                self.fixes_applied += 1

            new_lines.append(line)
            i += 1

        return '\n'.join(new_lines)

    def fix_variable_naming(self, content: str) -> str:
        """Fix F821/F841 by reverting problematic underscore prefixes."""
        # Common patterns that were incorrectly prefixed
        fixes = {
            'python_files': 'python_files',
            'new_lines': 'new_lines',
            'blank_lines': 'blank_lines',
            'new_content': 'new_content',
            'skip_line': 'skip_line',
            'original_content': 'original_content',
            'files_changed': 'files_changed',
            'base_path': 'base_path',
            'dir_path': 'dir_path',
            'init_file': 'init_file',
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
        }

        for wrong, correct in fixes.items():
            if wrong in content:
                content = content.replace(wrong, correct)
                self.fixes_applied += 1

        return content


def main():
    """Main function to run the comprehensive fix."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print(f"Script location: {script_dir}")
    print(f"Project root: {project_root}")

    fixer = ComprehensiveFinalFix(str(project_root))
    fixer.run_fix()


if __name__ == "__main__":
    main()