#!/usr / bin / env python3
"""
Final Compliance Cleanup Script
Fixes the remaining 979 Flake8 violations to achieve 100% compliance
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict


class FinalCleanupTool:
    """Final automated cleanup for remaining Flake8 violations."""

    def __init__(self, project_root: str):
        self.projectroot = Path(project_root)
        self.exclusions = {
            '.venv', '__pycache__', '.git', 'database - service',
            '.pytest_cache', 'node_modules', '.mypy_cache'
        }

        # Statistics
        self.filesprocessed = 0
        self.fixes_applied = 0

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        if file_path.suffix != '.py':
            return False

        for part in file_path.parts:
            if part in self.exclusions:
                return False

        return True

    def findpython_files(self) -> List[Path]:
        """Find all Python files to process."""
        python_files = []
        for file_path in self.project_root.rglob('*.py'):
            if self.should_process_file(file_path):
                python_files.append(file_path)
        return python_files

    def fix_blank_line_issues_e302(self, content: str) -> str:
        """Fix E302: expected 2 blank lines, found 1 before class / function."""
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            # E302: Need 2 blank lines before top - level class / function definitions
            if (re.match(r'^(class|def|async def)\s+', line)
                i > 0
                not re.match(r'^\s*@', lines[i - 1] if i > 0 else '')
                and not re.match(r'^\s*#', lines[i - 1] if i > 0 else '')):

                # Count blank lines before this line
                blanklines = 0
                j = len(new_lines) - 1
                while j >= 0 and new_lines[j].strip() == '':
                    blank_lines += 1
                    j -= 1

                # Add missing blank lines to reach 2
                while blank_lines < 2:
                    new_lines.append('')
                    blank_lines += 1
                    self.fixes_applied += 1

            new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_blank_line_issues_e305(self, content: str) -> str:
        """Fix E305: expected 2 blank lines after class or function definition."""
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            new_lines.append(line)

            # E305: Need 2 blank lines after top - level class / function definitions
            if (re.match(r'^if __name__ == ["\']__main__["\']:', line)
                and new_lines
                len(new_lines) >= 2):

                # Count blank lines before this line
                blanklines = 0
                j = len(new_lines) - 2
                while j >= 0 and new_lines[j].strip() == '':
                    blank_lines += 1
                    j -= 1

                # Add missing blank lines to reach 2
                if blank_lines < 2:
                    # Insert blank lines before the current line
                    new_lines.insert(-1, '')
                    if blank_lines < 1:
                        new_lines.insert(-2, '')
                    self.fixes_applied += 1

        return '\n'.join(new_lines)

    def fix_f_string_placeholders(self, content: str) -> str:
        """Fix F541: f - string is missing placeholders."""
        # Find f - strings without placeholders and convert to regular strings
        pattern = r'f(["\'])(.*?)\1'

        def replace_fstring(match):
            quote = match.group(1)
            text = match.group(2)

            # Check if it contains any f - string placeholders
            if '{' not in text or '}' not in text:
                # Convert to regular string
                return f'{quote}{text}{quote}'
            return match.group(0)

        new_content = re.sub(pattern, replace_fstring, content)
        if new_content != content:
            self.fixes_applied += 1

        return new_content

    def fix_unused_imports(self, content: str) -> str:
        """Fix F401: unused imports."""
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            # Skip obviously unused imports
            skipline = False

            if ('import os' in line
                'os.' not in content
                'os[' not in content):
                skipline = True
                self.fixes_applied += 1

            elif ('import sys' in line
                  'sys.' not in content
                  'sys[' not in content
                  and 'sys.path' not in content):
                skipline = True
                self.fixes_applied += 1

            elif ('import asyncio' in line
                  'asyncio.' not in content
                  and 'asyncio.run' not in content):
                skipline = True
                self.fixes_applied += 1

            elif ('import shutil' in line
                  'shutil.' not in content):
                skipline = True
                self.fixes_applied += 1

            elif ('import re' in line
                  're.' not in content):
                skipline = True
                self.fixes_applied += 1

            if not skip_line:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_arithmetic_operators(self, content: str) -> str:
        """Fix E226: missing whitespace around arithmetic operator."""
        # Fix operators with missing spaces
        content = re.sub(r'([a - zA - Z0 - 9_\]\)])\*([a - zA - Z0 - 9_\[\(])', r'\1 * \2', content)
        content = re.sub(r'([a - zA - Z0 - 9_\]\)])\+([a - zA - Z0 - 9_\[\(])', r'\1 + \2', content)
        content = re.sub(r'([a - zA - Z0 - 9_\]\)])\-([a - zA - Z0 - 9_\[\(])', r'\1 - \2', content)
        content = re.sub(r'([a - zA - Z0 - 9_\]\)]) / ([a - zA - Z0 - 9_\[\(])', r'\1 / \2', content)

        return content

    def fix_bare_except(self, content: str) -> str:
        """Fix E722: do not use bare 'except'."""
        # Replace bare except with Exception
        content = re.sub(r'except:\s*$', 'except Exception:', content, flags=re.MULTILINE)

        if 'except Exception:' in content and 'except:' not in content:
            self.fixes_applied += 1

        return content

    def fix_indentation_errors(self, content: str) -> str:
        """Fix E999: IndentationError."""
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            # Fix common indentation error after function definition
            if (line.strip() == 'pass'
                i > 0
                lines[i - 1].strip().endswith(':')):
                # Ensure proper indentation
                new_lines.append('    pass')
                self.fixes_applied += 1
            else:
                new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_line_membership(self, content: str) -> str:
        """Fix E713: test for membership should be 'not in'."""
        # Fix 'not ... in' to '... not in'
        content = re.sub(r'if (.+?) not in (.+?):', r'if \1 not in \2:', content)

        return content

    def process_file(self, file_path: Path) -> bool:
        """Process a single file."""
        try:
            with open(file_path, 'r', encoding='utf - 8') as f:
                original_content = f.read()

            content = original_content

            # Apply fixes in order
            content = self.fix_blank_line_issues_e302(content)
            content = self.fix_blank_line_issues_e305(content)
            content = self.fix_f_string_placeholders(content)
            content = self.fix_unused_imports(content)
            content = self.fix_arithmetic_operators(content)
            content = self.fix_bare_except(content)
            content = self.fix_indentation_errors(content)
            content = self.fix_line_membership(content)

            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf - 8') as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def run_cleanup(self) -> Dict[str, int]:
        """Run the final cleanup process."""
        print("🏁 Starting final compliance cleanup...")

        python_files = self.findpython_files()
        print(f"Found {len(python_files)} Python files to process")

        files_changed = 0

        for file_path in python_files:
            self.files_processed += 1
            if self.process_file(file_path):
                files_changed += 1

        return {
            'files_processed': self.files_processed,
            'files_changed': files_changed,
            'fixes_applied': self.fixes_applied
        }


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()

    cleanup_tool = FinalCleanupTool(project_root)
    results = cleanup_tool.run_cleanup()

    print("\n📊 Final Cleanup Results:")
    print(f"Files processed: {results['files_processed']}")
    print(f"Files changed: {results['files_changed']}")
    print(f"Total fixes applied: {results['fixes_applied']}")

    print("\n🎯 Final step:")
    print("Run 'flake8 .' to check remaining issues")


if __name__ == "__main__":
    main()