"""DB Service API backed by SQLite via SQLAlchemy.

Endpoints mirror the in-memory version used in tests but persist to SQLite.
"""

from __future__ import annotations

import threading
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from db_service_core import DBService

app = FastAPI(title="DB Service API")
_db_lock = threading.Lock()
db_service = DBService()


class InsertRowRequest(BaseModel):
    """Request model for inserting a single row into a table."""

    row: dict[str, Any]


class CreateTableRequest(BaseModel):
    """Request to create a table with schema or columns mapping."""

    table_name: str
    schema: dict[str, str] | None = None
    columns: dict[str, str] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}


@app.post("/tables", status_code=201)
def create_table(payload: CreateTableRequest) -> dict[str, str]:
    """Create a table with the provided schema/columns payload."""
    name = payload.table_name
    if not isinstance(name, str) or not name:
        raise HTTPException(status_code=422, detail="Invalid table name")

    schema = payload.schema
    columns = payload.columns
    effective: dict[str, str] | None = None
    if isinstance(schema, dict) and schema:
        effective = {str(k): str(v) for k, v in schema.items()}
    elif isinstance(columns, dict) and columns:
        effective = {str(k): str(v) for k, v in columns.items()}
    if effective is None:
        raise HTTPException(status_code=422, detail="Invalid schema/columns")

    with _db_lock:
        db_service.create_table(name, effective)
    return {"message": f"table '{name}' created"}


@app.get("/tables")
def list_tables() -> dict[str, list[str]]:
    """List available tables."""
    with _db_lock:
        tables = db_service.list_tables()
    return {"tables": tables}


@app.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str) -> dict[str, Any]:
    """Get the schema for a table."""
    with _db_lock:
        schema = db_service.get_table_schema(table_name)
    return {"schema": schema}


@app.delete("/tables/{table_name}")
def delete_table(table_name: str) -> dict[str, str]:
    """Delete a table and its contents."""
    with _db_lock:
        db_service.delete_table(table_name)
    return {"message": f"table '{table_name}' deleted"}


@app.post("/tables/{table_name}/rows", status_code=201)
def insert_row(table_name: str, payload: InsertRowRequest) -> dict[str, Any]:
    """Insert a single row into the specified table."""
    if not payload.row:
        raise HTTPException(status_code=422, detail="Invalid row data")
    with _db_lock:
        row_id = db_service.insert_row(table_name, payload.row)
    return {"message": "row inserted", "row_id": row_id}


@app.get("/tables/{table_name}/rows")
def get_rows(
    table_name: str,
    start_time: str | None = Query(default=None),
    end_time: str | None = Query(default=None),
    columns: str | None = Query(default=None),
    timestamp_column: str = Query(default="timestamp"),
) -> list[dict[str, Any]]:
    """Query rows with optional time filtering and projected columns."""
    col_list = [c for c in columns.split(",") if c] if columns else None
    with _db_lock:
        rows = db_service.get_rows(table_name, start_time, end_time, timestamp_column, col_list)
    return rows


@app.delete("/tables/{table_name}/rows/{row_id}")
def delete_row(table_name: str, row_id: int) -> dict[str, str]:
    """Delete a single row by ID."""
    with _db_lock:
        db_service.delete_row(table_name, row_id)
    return {"message": f"row {row_id} deleted"}


@app.put("/tables/{table_name}/rows/{row_id}")
def update_row(table_name: str, row_id: int, row: dict[str, Any]) -> dict[str, str]:
    """Update a single row by ID."""
    if not row:
        raise HTTPException(status_code=422, detail="No row data provided")
    with _db_lock:
        db_service.update_row(table_name, row_id, row)
    return {"message": f"row {row_id} updated"}
