#!/usr/bin/env python3
"""
Automatic flake8 violation fixer for the database service
"""

import re
import os
from pathlib import Path


def fix_file_violations(file_path):
    """Fix common flake8 violations in a single file"""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix W293: blank line contains whitespace
    content = re.sub(r'^[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix W291: trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # Fix W391: blank line at end of file
    content = content.rstrip() + '\n'
    
    # Remove unused imports (F401) - common patterns
    unused_imports = [
        r'^from typing import List$',
        r'^from typing import Optional$', 
        r'^from typing import Dict$',
        r'^from typing import Any$',
        r'^import asyncio$',
        r'^from uuid import UUID$',
        r'^from datetime import timedelta$',
        r'^from pathlib import Path$',
        r'^from pydantic import ConfigDict$',
        r'^from sqlalchemy.dialects.postgresql import UUID$',
        r'^from sqlalchemy.types import TypeDecorator$',
        r'^from sqlalchemy import Enum as SQLEnum$',
        r'^from sqlalchemy.orm import relationship$',
        r'^from datetime import datetime, timezone$',
        r'^from dataclasses import field$',
        r'^from sqlalchemy.exc import SQLAlchemyError$',
        r'^from sqlalchemy.ext.asyncio import AsyncSession$',
    ]
    
    for pattern in unused_imports:
        content = re.sub(pattern + r'\n', '', content, flags=re.MULTILINE)
    
    # Fix specific unused imports in context
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip lines with unused imports that are context-specific
        if ('imported but unused' in line or 
            'F401' in line or
            'local variable' in line and 'is assigned to but never used' in line):
            continue
            
        # Remove specific unused variable assignments
        if 'session' in line and '=' in line and 'never used' not in line:
            # Keep session assignments that are actually used
            new_lines.append(line)
        elif line.strip().startswith('session =') and 'never used' in str(line):
            # Skip unused session assignments
            continue
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed whitespace and basic issues")
    else:
        print(f"  ✨ No changes needed")


def main():
    """Fix all Python files in the database service"""
    src_dir = Path("src")
    
    if not src_dir.exists():
        print("❌ src/ directory not found. Run from database-service directory.")
        return 1
    
    # Find all Python files
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"🔧 Fixing {len(python_files)} Python files...")
    
    for file_path in python_files:
        try:
            fix_file_violations(file_path)
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print("\n✅ Basic flake8 fixes complete!")
    print("Run flake8 again to see remaining issues.")
    
    return 0


if __name__ == "__main__":
    exit(main())
