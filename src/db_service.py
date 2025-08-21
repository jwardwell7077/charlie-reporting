"""Local DB service client for FileConsumer and integrations.

Parses CSV text, creates a corresponding table if needed, and inserts rows
using the DBService core (no HTTP involved for tests/in-process runs).
"""
from __future__ import annotations

from typing import Any, Dict, List
import csv
import io

from .db_service_core import DBService


class DBClient:
	"""Thin wrapper to send CSV data to the DBService core."""

	def __init__(self, service: DBService | None = None) -> None:
		self.service = service or DBService()

	def send_to_db(self, data: str, table_name: str | None = None) -> Dict[str, Any]:
		"""Ingest CSV text into a table.

		Args:
			data: Raw CSV text (first row is header).
			table_name: Optional explicit table name; if omitted, uses 'ingest'.

		Returns:
			Dict with keys: table, row_count.
		"""
		if not data:
			return {"table": table_name or "ingest", "row_count": 0}
		reader = csv.DictReader(io.StringIO(data))
		rows: List[Dict[str, Any]] = list(reader)
		if not rows:
			return {"table": table_name or "ingest", "row_count": 0}
		# Infer schema as TEXT columns
		columns = {str(k): "TEXT" for k in rows[0].keys()}
		tbl = table_name or "ingest"
		self.service.create_table(tbl, columns)
		inserted = 0
		for r in rows:
			self.service.insert_row(tbl, r)
			inserted += 1
		return {"table": tbl, "row_count": inserted}


__all__ = ["DBClient"]

