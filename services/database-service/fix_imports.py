#!/usr/bin/env python3
"""
Advanced flake8 violation fixer - handles missing imports and code issues
"""

import re
from pathlib import Path


def fix_imports_and_issues(file_path):
    """Fix missing imports and other code issues"""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    lines = content.split('\n')
    new_lines = []
    
    # Track what imports we need to add
    needs_uuid = False
    needs_optional = False
    needs_datetime = False
    needs_list = False
    needs_asyncio = False
    needs_pathlib = False
    needs_sqlalchemy_error = False
    
    # Check what's needed in the content
    if 'UUID' in content and 'from uuid import' not in content and 'import uuid' not in content:
        needs_uuid = True
    if 'Optional[' in content and 'Optional' not in [line for line in lines if 'import' in line]:
        needs_optional = True
    if 'datetime' in content and 'datetime' not in [line for line in lines if 'import' in line and 'datetime' in line]:
        needs_datetime = True
    if 'List[' in content and 'List' not in [line for line in lines if 'import' in line]:
        needs_list = True
    if 'asyncio.' in content and 'import asyncio' not in content:
        needs_asyncio = True
    if 'Path(' in content and 'from pathlib import Path' not in content:
        needs_pathlib = True
    if 'SQLAlchemyError' in content and 'SQLAlchemyError' not in [line for line in lines if 'import' in line]:
        needs_sqlalchemy_error = True
    
    import_section_end = 0
    in_imports = False
    
    for i, line in enumerate(lines):
        # Track where imports end
        if line.strip().startswith(('import ', 'from ')) and not in_imports:
            in_imports = True
        elif in_imports and not line.strip().startswith(('import ', 'from ')) and line.strip() != '':
            import_section_end = i
            in_imports = False
        
        # Remove unused imports
        if any(unused in line for unused in [
            'typing.List\' imported but unused',
            'typing.Optional\' imported but unused', 
            'typing.Dict\' imported but unused',
            'typing.Any\' imported but unused',
            'datetime.timedelta\' imported but unused',
            'pathlib.Path\' imported but unused',
            'pydantic.ConfigDict\' imported but unused',
        ]):
            continue
            
        # Remove unused import lines
        skip_line = False
        if 'from typing import' in line:
            parts = line.split('import')[1].strip()
            imports = [imp.strip() for imp in parts.split(',')]
            used_imports = []
            
            for imp in imports:
                imp_clean = imp.strip()
                if imp_clean == 'List' and 'List[' not in content:
                    continue
                if imp_clean == 'Optional' and 'Optional[' not in content:
                    continue
                if imp_clean == 'Dict' and 'Dict[' not in content:
                    continue
                if imp_clean == 'Any' and ': Any' not in content and 'Any]' not in content:
                    continue
                used_imports.append(imp_clean)
            
            if used_imports:
                new_lines.append(f"from typing import {', '.join(used_imports)}")
            skip_line = True
        
        # Remove other unused imports
        elif any(pattern in line for pattern in [
            'from datetime import timedelta',
            'from pathlib import Path',
            'from pydantic import ConfigDict',
            'import asyncio',
        ]) and not any(usage in content for usage in [
            'timedelta', 'Path(', 'ConfigDict', 'asyncio.'
        ]):
            skip_line = True
        
        # Remove local variable assignments that are unused
        elif 'session =' in line and 'F841' in str(content):
            skip_line = True
        elif 'content =' in line and 'local variable \'content\' is assigned to but never used' in str(content):
            skip_line = True
        elif 'except Exception as e:' in line:
            # Replace with just except Exception:
            new_lines.append(line.replace(' as e', ''))
            skip_line = True
        
        if not skip_line:
            new_lines.append(line)
    
    # Add missing imports at the appropriate location
    if import_section_end == 0:
        import_section_end = len([l for l in new_lines if l.strip().startswith(('"""', "'''"))][-1:]) or [0][-1] + 1
    
    imports_to_add = []
    
    if needs_uuid:
        imports_to_add.append('from uuid import UUID')
    if needs_optional:
        imports_to_add.append('from typing import Optional')
    if needs_datetime:
        imports_to_add.append('from datetime import datetime, timezone')
    if needs_list:
        imports_to_add.append('from typing import List')
    if needs_asyncio:
        imports_to_add.append('import asyncio')
    if needs_pathlib:
        imports_to_add.append('from pathlib import Path')
    if needs_sqlalchemy_error:
        imports_to_add.append('from sqlalchemy.exc import SQLAlchemyError')
    
    if imports_to_add:
        # Insert imports after existing imports
        for i, import_line in enumerate(imports_to_add):
            new_lines.insert(import_section_end + i, import_line)
    
    content = '\n'.join(new_lines)
    
    # Fix line length issues by breaking long lines
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 88 and '=' in line and not line.strip().startswith('#'):
            # Try to break assignment lines
            if ' = ' in line:
                parts = line.split(' = ', 1)
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    if len(parts[1]) > 40:
                        fixed_lines.append(parts[0] + ' = (')
                        fixed_lines.append(' ' * (indent + 4) + parts[1])
                        fixed_lines.append(' ' * indent + ')')
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix f-string issues
    content = re.sub(r'f"([^{]*)"', r'"\1"', content)  # Remove f from strings without placeholders
    
    # Fix blank line issues
    content = re.sub(r'\n\n\nclass ', r'\n\n\nclass ', content)
    content = re.sub(r'\n\n\ndef ', r'\n\n\ndef ', content)
    content = re.sub(r'\n\n\nasync def ', r'\n\n\nasync def ', content)
    
    # Add necessary blank lines before class/function definitions
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if i > 0 and line.strip().startswith(('class ', 'def ', 'async def ')):
            prev_line = lines[i-1].strip()
            if prev_line and not prev_line.startswith(('"""', "'''", '#')):
                if i > 1 and lines[i-2].strip():
                    fixed_lines.append('')
                fixed_lines.append('')
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix continuation line indentation
    content = re.sub(r'\n    ([^)]+)\)', r'\n        \1)', content)
    
    # Only write if content changed
    if content.strip() != original_content.strip():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed imports and code issues")
        return True
    else:
        print(f"  ✨ No changes needed")
        return False


def main():
    """Fix all Python files in the database service"""
    src_dir = Path("src")
    
    if not src_dir.exists():
        print("❌ src/ directory not found. Run from database-service directory.")
        return 1
    
    # Find all Python files
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"🔧 Fixing imports and issues in {len(python_files)} files...")
    
    fixed_count = 0
    for file_path in python_files:
        try:
            if fix_imports_and_issues(file_path):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} files!")
    print("Run flake8 again to see remaining issues.")
    
    return 0


if __name__ == "__main__":
    exit(main())
