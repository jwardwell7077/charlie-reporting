"""DB Service API backed by SQLite via SQLAlchemy.

Endpoints mirror the in-memory version used in tests but persist to SQLite.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel
import threading

from db_service_core import DBService


app = FastAPI(title="DB Service API")
_db_lock = threading.Lock()
db_service = DBService()


class InsertRowRequest(BaseModel):
    row: Dict[str, Any]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/tables", status_code=201)
def create_table(payload: Dict[str, Any] = Body(...)) -> Dict[str, str]:
    name = payload.get("table_name")
    if not isinstance(name, str) or not name:
        raise HTTPException(status_code=422, detail="Invalid table name")

    schema = payload.get("schema")
    columns = payload.get("columns")
    effective: Optional[Dict[str, str]] = None
    if isinstance(schema, dict) and schema:
        tmp: Dict[str, str] = {}
        for k, v in schema.items():
            tmp[str(k)] = str(v)
        effective = tmp
    elif isinstance(columns, dict) and columns:
        tmp2: Dict[str, str] = {}
        for k, v in columns.items():
            tmp2[str(k)] = str(v)
        effective = tmp2
    if effective is None:
        raise HTTPException(status_code=422, detail="Invalid schema/columns")

    with _db_lock:
        db_service.create_table(name, effective)
    return {"message": f"table '{name}' created"}


@app.get("/tables")
def list_tables() -> Dict[str, List[str]]:
    with _db_lock:
        tables = db_service.list_tables()
    return {"tables": tables}


@app.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str) -> Dict[str, Any]:
    with _db_lock:
        schema = db_service.get_table_schema(table_name)
    return {"schema": schema}


@app.delete("/tables/{table_name}")
def delete_table(table_name: str) -> Dict[str, str]:
    with _db_lock:
        db_service.delete_table(table_name)
    return {"message": f"table '{table_name}' deleted"}


@app.post("/tables/{table_name}/rows", status_code=201)
def insert_row(table_name: str, payload: InsertRowRequest) -> Dict[str, Any]:
    if not payload.row:
        raise HTTPException(status_code=422, detail="Invalid row data")
    with _db_lock:
        row_id = db_service.insert_row(table_name, payload.row)
    return {"message": "row inserted", "row_id": row_id}


@app.get("/tables/{table_name}/rows")
def get_rows(
    table_name: str,
    start_time: Optional[str] = Query(default=None),
    end_time: Optional[str] = Query(default=None),
    columns: Optional[str] = Query(default=None),
    timestamp_column: str = Query(default="timestamp"),
) -> List[Dict[str, Any]]:
    col_list = [c for c in columns.split(",") if c] if columns else None
    with _db_lock:
        rows = db_service.get_rows(table_name, start_time, end_time, timestamp_column, col_list)
    return rows


@app.delete("/tables/{table_name}/rows/{row_id}")
def delete_row(table_name: str, row_id: int) -> Dict[str, str]:
    with _db_lock:
        db_service.delete_row(table_name, row_id)
    return {"message": f"row {row_id} deleted"}


@app.put("/tables/{table_name}/rows/{row_id}")
def update_row(table_name: str, row_id: int, row: Dict[str, Any]) -> Dict[str, str]:
    if not row:
        raise HTTPException(status_code=422, detail="No row data provided")
    with _db_lock:
        db_service.update_row(table_name, row_id, row)
    return {"message": f"row {row_id} updated"}
