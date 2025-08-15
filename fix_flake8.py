#!/usr/bin/env python3
"""
Fix common flake8 violations in Python files
"""
import os
import re

def clean_imports(lines):
    """Remove duplicate and unused imports"""
    import_lines = []
    seen_imports = set()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Track import lines
        if (stripped.startswith('import ') or 
            stripped.startswith('from ') and ' import ' in stripped):
            
            # Skip duplicate imports
            if stripped not in seen_imports:
                seen_imports.add(stripped)
                import_lines.append(line)
        else:
            # Once we hit non-imports, add all unique imports then continue
            if import_lines:
                cleaned_lines.extend(import_lines)
                import_lines = []
            cleaned_lines.append(line)
    
    return cleaned_lines

def fix_spacing(lines):
    """Fix spacing issues"""
    fixed_lines = []
    prev_line_empty = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Add blank lines before class/function definitions
        if (stripped.startswith('class ') or 
            stripped.startswith('def ') or 
            stripped.startswith('async def ')):
            
            # Need 2 blank lines before top-level class/function
            if (i > 0 and 
                not prev_line_empty and 
                not lines[i-1].strip().startswith('@')):
                fixed_lines.append('\n')
                if not lines[i-1].strip():
                    pass  # Already have one blank line
                else:
                    fixed_lines.append('\n')
        
        # Remove blank lines after decorators
        if (stripped.startswith('@') and 
            i + 1 < len(lines) and 
            not lines[i + 1].strip()):
            fixed_lines.append(line)
            # Skip the blank line after decorator
            continue
            
        fixed_lines.append(line)
        prev_line_empty = not stripped
    
    return fixed_lines

def fix_file(file_path):
    """Fix common flake8 issues in a file"""
    print(f"Fixing {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Fix imports
        lines = clean_imports(lines)
        
        # Fix spacing
        lines = fix_spacing(lines)
        
        # Remove trailing whitespace
        lines = [line.rstrip() + '\n' if line.strip() else '\n' for line in lines]
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

def main():
    """Fix common issues in database service"""
    base_dir = "/home/jon/repos/charlie-left/services/database-service/src"
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                fix_file(file_path)

if __name__ == "__main__":
    main()
