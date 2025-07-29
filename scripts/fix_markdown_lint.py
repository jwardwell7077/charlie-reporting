#!/usr/bin/env python3
"""
Quick markdown lint fixes for documentation files
"""

import os
import re
from pathlib import Path

def fix_markdown_file(file_path):
    """Fix common markdown lint issues in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix: Remove italics from quoted text (MD036)
        content = re.sub(r'\*"([^"]+)"\*', r'"\1"', content)
        
        # Fix: Add language to fenced code blocks where missing
        content = re.sub(r'```\n(?!```)', '```text\n', content)
        
        # Fix: Remove trailing spaces from lines ending with :
        content = re.sub(r':[ ]+\n', ':\n', content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix markdown issues in all documentation files"""
    print("🔧 Fixing markdown lint issues in documentation files...")
    
    # Find all markdown files in docs directory
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ docs directory not found")
        return
    
    markdown_files = list(docs_dir.rglob("*.md"))
    
    fixed_count = 0
    for md_file in markdown_files:
        if fix_markdown_file(md_file):
            fixed_count += 1
    
    print(f"\n🎉 Fixed {fixed_count} files out of {len(markdown_files)} markdown files")

if __name__ == "__main__":
    main()
