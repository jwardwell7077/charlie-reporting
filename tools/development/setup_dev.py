#!/usr / bin / env python3
"""
setup.py - Alternative setup for development

This script ensures the src directory is in the Python path for development.
Run this before running tests or the main application.
"""

import sys
import os

# Add src directory to Python path
srcpath = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print(f"Added {src_path} to Python path")
print("You can now run:")
print("  python src / main.py")
print("  python -m pytest tests/")