#!/usr/bin/env python3
"""Run the FileConsumer once to ingest CSVs from an input dir and archive them.

Environment variables:
  INGESTION_DIR  - directory to read CSVs from (default: ./data/incoming)
  ARCHIVE_DIR    - directory to move processed CSVs to (default: ./data/outputs)

Usage:
  python scripts/run_consumer_once.py
"""
from __future__ import annotations

import os
import logging
from pathlib import Path

from src.consumer.file_watcher import FileConsumer
from src.db_service import DBClient


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    input_dir = Path(os.environ.get("INGESTION_DIR", "./data/incoming"))
    archive_dir = Path(os.environ.get("ARCHIVE_DIR", "./data/outputs"))
    input_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    consumer = FileConsumer(input_dir=input_dir, archive_dir=archive_dir, db_service=DBClient())
    consumer.consume_new_files()
    print(f"Processed CSVs from {input_dir} to {archive_dir} and ingested into DB.")


if __name__ == "__main__":
    main()
