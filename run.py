#!/usr/bin/env python3
"""
run.py - Convenience script to run the main application

This script ensures proper module resolution and runs the main application.
"""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Run the main application
if __name__ == "__main__":
    from main import main
    main()
