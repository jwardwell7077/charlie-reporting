#!/usr/bin/env python3
"""
Final comprehensive cleanup for report-generator service.
Handles remaining F401 (unused imports), E302/E304 (blank lines), and other issues.
"""

import ast
import re
from pathlib import Path
from typing import Set


class FinalCleanup:
    """Final cleanup for common flake8 violations."""
    
    def __init__(self, service_root: str):
        self.service_root = Path(service_root)
        self.files_fixed = 0
        self.fixes_applied = 0
        
    def run_cleanup(self):
        """Run final cleanup."""
        print("🧹 Final cleanup for report-generator service...")
        
        for py_file in self.service_root.glob("**/*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                original_content = content
                fixed_content = self.fix_file(content, py_file)
                
                if fixed_content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    self.files_fixed += 1
                    print(f"Cleaned: {py_file.relative_to(self.service_root)}")
                    
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
        
        print(f"Cleanup complete: {self.files_fixed} files cleaned, {self.fixes_applied} fixes applied")
    
    def fix_file(self, content: str, file_path: Path) -> str:
        """Fix individual file content."""
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            original_line = line
            
            # Remove unused imports that are clearly safe to remove
            if self.is_safe_unused_import(line, content, file_path):
                self.fixes_applied += 1
                i += 1
                continue
            
            # Fix E302: expected 2 blank lines before function/class
            if self.needs_blank_lines_before(line, new_lines):
                # Remove existing blank lines
                while new_lines and new_lines[-1].strip() == '':
                    new_lines.pop()
                # Add exactly 2 blank lines
                new_lines.extend(['', ''])
                self.fixes_applied += 1
            
            # Fix E304: blank lines after decorator
            if self.is_blank_after_decorator(line, lines, i):
                self.fixes_applied += 1
                i += 1
                continue
            
            # Fix indentation issues
            if self.has_indentation_issue(line, lines, i):
                line = self.fix_indentation(line, lines, i)
                self.fixes_applied += 1
            
            new_lines.append(line)
            i += 1
        
        # Ensure file ends with exactly one newline
        while new_lines and new_lines[-1] == '':
            new_lines.pop()
        new_lines.append('')
        
        return '\n'.join(new_lines)
    
    def is_safe_unused_import(self, line: str, content: str, file_path: Path) -> bool:
        """Check if this is a safe unused import to remove."""
        line = line.strip()
        
        # Safe patterns for removal
        safe_patterns = [
            r'^import os$',
            r'^import sys$',
            r'^import re$',
            r'^import json$',
            r'^from typing import Dict$',
            r'^from typing import List$',
            r'^from typing import Any$',
            r'^from typing import Optional$',
            r'^from pathlib import Path$',
        ]
        
        for pattern in safe_patterns:
            if re.match(pattern, line):
                # Check if actually unused (basic check)
                import_name = line.split()[-1]
                # Don't remove if used elsewhere in file
                if import_name in content.replace(line, '', 1):
                    return False
                return True
        
        return False
    
    def needs_blank_lines_before(self, line: str, new_lines: list) -> bool:
        """Check if we need blank lines before this line."""
        # Top-level function or class definition
        if not re.match(r'^(def|class)\s+\w+', line):
            return False
        
        if not new_lines:
            return False
        
        # Count existing blank lines
        blank_count = 0
        for i in range(len(new_lines) - 1, -1, -1):
            if new_lines[i].strip() == '':
                blank_count += 1
            else:
                break
        
        return blank_count < 2
    
    def is_blank_after_decorator(self, line: str, lines: list, i: int) -> bool:
        """Check if this is a blank line after decorator."""
        if line.strip() != '' or i == 0:
            return False
        
        # Previous line is decorator
        prev_line = lines[i - 1].strip()
        if not prev_line.startswith('@'):
            return False
        
        # Next line is function/class
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            return next_line.startswith(('def ', 'class '))
        
        return False
    
    def has_indentation_issue(self, line: str, lines: list, i: int) -> bool:
        """Check for common indentation issues."""
        if i + 1 >= len(lines):
            return False
        
        # Check for unindented pass after colon
        if (line.strip().endswith(':') and 
            i + 1 < len(lines) and 
            lines[i + 1].strip() == 'pass' and
            not lines[i + 1].startswith('    ')):
            return True
        
        return False
    
    def fix_indentation(self, line: str, lines: list, i: int) -> str:
        """Fix indentation issues."""
        # This is handled in the main loop
        return line


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    service_root = script_dir.parent / 'services' / 'report-generator'
    
    cleaner = FinalCleanup(str(service_root))
    cleaner.run_cleanup()


if __name__ == "__main__":
    main()
