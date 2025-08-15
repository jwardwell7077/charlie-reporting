#!/usr/bin/env python3
"""Fix indentation issues in Python files
"""
import os


def fix_indentation(file_path):
    """Fix common indentation issues in a Python file"""
    print(f"Fixing {file_path}")
    
    with open(file_path) as f:
        lines = f.readlines()
    
    fixed_lines = []
    inside_class = False
    inside_function = False
    
    for i, line in enumerate(lines):
        # Remove trailing whitespace
        line = line.rstrip() + '\n' if line.strip() else '\n'
        
        # Fix common patterns
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            fixed_lines.append(line)
            continue
            
        # Detect class definition
        if stripped.startswith('class '):
            inside_class = True
            inside_function = False
            fixed_lines.append(line)
            continue
            
        # Detect function/method definition
        if stripped.startswith('def ') or stripped.startswith('async def '):
            inside_function = True
            # Ensure proper indentation for methods in class
            if inside_class and not line.startswith('    '):
                line = '    ' + stripped + '\n'
            fixed_lines.append(line)
            continue
            
        # Fix obvious indentation errors
        if inside_class and inside_function:
            # Method body should be double indented
            if stripped and not line.startswith('        ') and not stripped.startswith('@'):
                if not stripped.startswith('def ') and not stripped.startswith('class '):
                    line = '        ' + stripped + '\n'
        elif inside_class and not inside_function:
            # Class body should be single indented
            if stripped and not line.startswith('    ') and not stripped.startswith('@'):
                if not stripped.startswith('def ') and not stripped.startswith('class '):
                    line = '    ' + stripped + '\n'
        
        # Reset function flag on dedent
        if stripped and not line.startswith('    ') and inside_function:
            inside_function = False
            
        # Reset class flag on dedent  
        if stripped and not line.startswith(' ') and inside_class:
            inside_class = False
            
        fixed_lines.append(line)
    
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)

def main():
    """Fix indentation in database service files"""
    base_dir = "/home/jon/repos/charlie-left/services/database-service/src"
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                try:
                    fix_indentation(file_path)
                except Exception as e:
                    print(f"Error fixing {file_path}: {e}")

if __name__ == "__main__":
    main()
