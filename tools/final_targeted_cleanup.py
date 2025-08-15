#!/usr/bin/env python3
"""Final targeted cleanup for remaining violations."""

import re
from pathlib import Path


class FinalTargetedCleanup:
    """Targeted cleanup for specific remaining violations."""

    def __init__(self, root_dir: str):
        self.rootdir = Path(root_dir)
        self.files_changed = 0
        self.fixes_applied = 0

    def run_cleanup(self):
        """Run targeted cleanup on all Python files."""
        print("Starting final targeted cleanup...")

        for python_file in self.root_dir.glob("**/*.py"):
            # Skip excluded directories
            if any(excluded in str(python_file) for excluded in ['.venv', '__pycache__', '.git', 'database-service']):
                continue

            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                # Skip empty files
                if not original_content.strip():
                    continue

                cleanedcontent = self.clean_file_content(original_content)

                if cleaned_content != original_content:
                    with open(python_file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    self.files_changed += 1
                    print(f"Fixed: {python_file}")

            except Exception as e:
                print(f"Error processing {python_file}: {e}")

        print(f"\nCompleted: {self.files_changed} files changed, {self.fixes_applied} fixes applied")

    def clean_file_content(self, content: str) -> str:
        """Apply targeted cleaning to file content."""
        # Fix F821: undefined name issues caused by previous cleanup
        # Revert problematic underscore prefixes
        content = re.sub(r'_([a-zA-Z_][a-zA-Z0-9_]*) = ', r'\1 = ', content)

        # Fix E999: IndentationError - ensure proper indentation after except/function
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            # Fix indentation after except statements
            if (line.strip().startswith('except') and line.rstrip().endswith(':')
                i + 1 < len(lines) and lines[i + 1].strip() == 'pass'
                not lines[i + 1].startswith('    ')):
                new_lines.append(line)
                new_lines.append('    pass')
                self.fixes_applied += 1
                continue

            # Fix function definition indentation
            if (line.strip().endswith(':')
                ('def ' in line or 'class ' in line)
                i + 1 < len(lines) and lines[i + 1].strip() == 'pass'
                not lines[i + 1].startswith('    ')):
                new_lines.append(line)
                new_lines.append('    pass')
                self.fixes_applied += 1
                continue

            # Fix E226: missing whitespace around arithmetic operator (specific *= case)
            if '*' in line and '=' in line and not re.search(r'["\'].*\*.*["\']', line):
                fixedline = re.sub(r'(\w)(\*)(\d)', r'\1 \2 \3', line)
                if fixed_line != line:
                    new_lines.append(fixed_line)
                    self.fixes_applied += 1
                    continue

            # Fix E302: expected 2 blank lines before top-level functions/classes
            if (re.match(r'^(def|class|@\w+)', line)
                new_lines and new_lines[-1].strip() != ''
                not any(new_lines[-j].strip() == '' for j in range(1, min(3, len(new_lines) + 1)))):
                # Add two blank lines before
                new_lines.append('')
                new_lines.append('')
                new_lines.append(line)
                self.fixes_applied += 1
                continue

            # Fix E304: blank lines found after function decorator
            if (line.strip().startswith('@') and i + 1 < len(lines)
                lines[i + 1].strip() == '' and i + 2 < len(lines)
                lines[i + 2].strip().startswith(('def ', 'class '))):
                # Remove blank line after decorator
                new_lines.append(line)
                # Skip the blank line
                continue

            new_lines.append(line)

        content = '\n'.join(new_lines)

        # Fix common unused import patterns (only if clearly unused)
        unusedimports = [
            r'^import os$',
            r'^import ast$',
            r'^from typing import Set$',
            r'^from typing import Tuple$',
            r'^from typing import Dict$',
        ]

        lines = content.split('\n')
        filteredlines = []

        for line in lines:
            # Check if it's an unused import
            isunused_import = False
            for pattern in unused_imports:
                if re.match(pattern, line.strip()):
                    # Check if actually used
                    importname = line.split()[-1] if 'import' in line else ''
                    if import_name and import_name not in content.replace(line, ''):
                        isunused_import = True
                        self.fixes_applied += 1
                        break

            if not is_unused_import:
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)


def main():
    """Main function to run the final cleanup."""
    scriptdir = Path(__file__).parent
    projectroot = script_dir.parent

    cleanup = FinalTargetedCleanup(str(project_root))
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()