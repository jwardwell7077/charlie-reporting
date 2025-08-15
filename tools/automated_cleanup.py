#!/usr/bin/env python3
"""(LEGACY) Automated Code Quality Cleanup Script.

NOTE: This script is being migrated to tools/legacy and excluded from strict
lint/type checks. Content intentionally left unchanged except shebang & header.
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set


class CodeCleanupTool:
    """Automated code cleanup for common Flake8 violations."""

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
        # Only process Python files
        if file_path.suffix != '.py':
            return False

        # Skip excluded directories
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

    def fix_whitespace_issues(self, content: str) -> str:
        """Fix whitespace - related issues."""
        original_content = content

        # W293: Remove blank lines containing whitespace
        content = re.sub(r'^[ \t]+$', '', content, flags=re.MULTILINE)

        # W291: Remove trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

        # W292: Ensure newline at end of file
        if content and not content.endswith('\n'):
            content += '\n'

        if content != original_content:
            self.fixes_applied += 1

        return content

    def fix_blank_line_issues(self, content: str) -> str:
        """Fix blank line spacing issues."""
        lines = content.split('\n')
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # E302: Add blank lines before class / function definitions
            if (re.match(r'^(class|def|async def)\s+', line)
                and i > 0
                new_lines
                and new_lines[-1].strip() != ''
                not re.match(r'^\s*@', new_lines[-1] if new_lines else '')):

                # Check if we need to add blank lines
                blanklines_needed = 2 if line.startswith('class ') else 1
                blanklines_before = 0

                # Count existing blank lines
                j = len(new_lines) - 1
                while j >= 0 and new_lines[j].strip() == '':
                    blank_lines_before += 1
                    j -= 1

                # Add missing blank lines
                while blank_lines_before < blank_lines_needed:
                    new_lines.append('')
                    blank_lines_before += 1
                    self.fixes_applied += 1

            new_lines.append(line)
            i += 1

        return '\n'.join(new_lines)

    def fix_import_issues(self, content: str) -> str:
        """Fix import - related issues."""
        lines = content.split('\n')

        # Find import section
        importstart = -1
        importend = -1

        for i, line in enumerate(lines):
            if re.match(r'^(import|from)\s+', line.strip()):
                if import_start == -1:
                    importstart = i
                importend = i
            elif (import_start != -1
                  and line.strip()
                  not line.startswith('#')
                  and not re.match(r'^(import|from)\s+', line.strip())):
                break

        if import_start != -1:
            # Separate standard library, third - party, and local imports
            stdlibimports = []
            thirdpartyimports = []
            localimports = []

            for i in range(import_start, import_end + 1):
                line = lines[i]
                if re.match(r'^from\s+\.', line) or 'src.' in line:
                    local_imports.append(line)
                elif any(lib in line for lib in ['os', 'sys', 'pathlib', 'datetime', 'logging', 'asyncio', 'typing']):
                    stdlib_imports.append(line)
                else:
                    thirdparty_imports.append(line)

            # Rebuild import section with proper grouping
            newimports = []
            if stdlib_imports:
                new_imports.extend(sorted(stdlib_imports))
                new_imports.append('')
            if thirdparty_imports:
                new_imports.extend(sorted(thirdparty_imports))
                new_imports.append('')
            if local_imports:
                new_imports.extend(sorted(local_imports))

            # Replace import section
            lines[import_start:import_end + 1] = new_imports
            self.fixes_applied += 1

        return '\n'.join(lines)

    def remove_unused_imports(self, content: str) -> str:
        """Remove obviously unused imports."""
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            # Skip lines that import unused typing elements
            if 'from typing import' in line:
                # Check if any typing elements are actually used
                if 'Optional' in line and 'Optional[' not in content:
                    line = line.replace('Optional, ', '').replace(', Optional', '').replace('Optional', '')
                if 'List' in line and 'List[' not in content:
                    line = line.replace('List, ', '').replace(', List', '').replace('List', '')
                if 'Any' in line and ': Any' not in content and 'Any,' not in content:
                    line = line.replace('Any, ', '').replace(', Any', '').replace('Any', '')

                # Clean up empty import
                if line.strip() == 'from typing import':
                    continue

            new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_line_too_long(self, content: str) -> str:
        """Fix basic line length issues."""
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if len(line) > 88:
                # Try to break long lines at logical points
                if ' and ' in line and len(line) > 88:
                    # Break at 'and' operators
                    parts = line.split(' and ')
                    if len(parts) > 1:
                        indent = len(line) - len(line.lstrip())
                        newline = parts[0] + ' and \\'
                        new_lines.append(new_line)
                        for part in parts[1:]:
                            new_lines.append(' ' * (indent + 4) + part.strip())
                        continue

            new_lines.append(line)

        return '\n'.join(new_lines)

    def fix_common_style_issues(self, content: str) -> str:
        """Fix common style issues."""
        # E704: Multiple statements on one line
        content = re.sub(r'def\s+\w+\([^)]*\):\s * pass\s*$',
                        lambda m: m.group(0).replace(': pass', ':\n        pass'),
                        content, flags=re.MULTILINE)

        # E261: At least two spaces before inline comment
        content = re.sub(r'(\S)\s#', r'\1  #', content)

        return content

    def process_file(self, file_path: Path) -> bool:
        """Process a single file."""
        try:
            with open(file_path, 'r', encoding='utf - 8') as f:
                original_content = f.read()

            content = original_content

            # Apply fixes in order
            content = self.fix_whitespace_issues(content)
            content = self.remove_unused_imports(content)
            content = self.fix_blank_line_issues(content)
            content = self.fix_common_style_issues(content)

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
        """Run the cleanup process."""
        print("🧹 Starting automated code cleanup...")

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

    cleanup_tool = CodeCleanupTool(project_root)
    results = cleanup_tool.run_cleanup()

    print("\n📊 Cleanup Results:")
    print(f"Files processed: {results['files_processed']}")
    print(f"Files changed: {results['files_changed']}")
    print(f"Total fixes applied: {results['fixes_applied']}")

    print("\n✨ Automated cleanup complete!")
    print("Run 'flake8 .' to check remaining issues")


if __name__ == "__main__":
    main()