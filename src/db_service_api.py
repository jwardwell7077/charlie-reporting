"""FastAPI in-memory DB Service API for tests.

Implements simple table and row operations used by tests:
- Health check
- Create/List/Delete tables
- Insert/Get/Update/Delete rows with optional time and column filters

This is intentionally minimal and in-memory.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel


app = FastAPI(title="DB Service API (In-Memory)")


# In-memory storage structure: {table: {"columns": Dict[str,str], "rows": List[Dict[str,Any]]}}
_TABLES: Dict[str, Dict[str, Any]] = {}


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

    existing = _TABLES.get(name)
    existing_rows: List[Dict[str, Any]] = list(existing["rows"]) if isinstance(existing, dict) else []
    _TABLES[name] = {"columns": effective, "rows": existing_rows}
    return {"message": f"table '{name}' created"}


@app.get("/tables")
def list_tables() -> Dict[str, List[str]]:
    return {"tables": list(_TABLES.keys())}


@app.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str) -> Dict[str, Any]:
    table = _TABLES.get(table_name)
    if not isinstance(table, dict):
        raise HTTPException(status_code=404, detail="table not found")
    schema_dict: Dict[str, str] = table.get("columns", {})
    schema_list = [{"name": k, "type": v} for k, v in schema_dict.items()]
    return {"schema": schema_list}


@app.post("/tables/{table_name}/rows", status_code=201)
def insert_row(table_name: str, payload: InsertRowRequest) -> Dict[str, Any]:
    table = _TABLES.get(table_name)
    if not isinstance(table, dict):
        raise HTTPException(status_code=404, detail="table not found")
    table.setdefault("rows", []).append(payload.row)
    return {"message": "row inserted"}


@app.get("/tables/{table_name}/rows")
def get_rows(
    table_name: str,
    start_time: Optional[str] = Query(default=None),
    end_time: Optional[str] = Query(default=None),
    columns: Optional[str] = Query(default=None),
) -> List[Dict[str, Any]]:
    table = _TABLES.get(table_name)
    if not isinstance(table, dict):
        raise HTTPException(status_code=404, detail="table not found")
    rows: List[Dict[str, Any]] = table.get("rows", [])

    # Apply time filtering (string compare on ISO8601 works for tests)
    def within_time(row: Dict[str, Any]) -> bool:
        ts = row.get("timestamp")
        if ts is None:
            return True
        if start_time is not None and ts < start_time:
            return False
        if end_time is not None and ts > end_time:
            return False
        return True

    filtered = [r for r in rows if within_time(r)]

    # Column selection
    if columns:
        desired = [c for c in columns.split(",") if c]
        projected: List[Dict[str, Any]] = []
        for r in filtered:
            # Preserve order of requested columns
            projected.append({c: r[c] for c in desired if c in r})
        return projected

    return filtered


@app.delete("/tables/{table_name}")
def delete_table(table_name: str) -> Dict[str, str]:
    _TABLES.pop(table_name, None)
    return {"message": f"table '{table_name}' deleted"}


@app.delete("/tables/{table_name}/rows/{row_id}")
def delete_row(table_name: str, row_id: int) -> Dict[str, str]:
    table = _TABLES.get(table_name)
    if not isinstance(table, dict):
        raise HTTPException(status_code=404, detail="table not found")
    # Remove first matching row with id
    rows: List[Dict[str, Any]] = table.get("rows", [])
    for idx, r in enumerate(rows):
        if r.get("id") == row_id:
            rows.pop(idx)
            break
    return {"message": f"row {row_id} deleted"}


@app.put("/tables/{table_name}/rows/{row_id}")
def update_row(table_name: str, row_id: int, row: Dict[str, Any]) -> Dict[str, str]:
    table = _TABLES.get(table_name)
    if not isinstance(table, dict):
        raise HTTPException(status_code=404, detail="table not found")
    if not row:
        # Let FastAPI/Pydantic return 422 when body is missing/invalid by requiring the body param
        raise HTTPException(status_code=422, detail="No row data provided")
    rows: List[Dict[str, Any]] = table.get("rows", [])
    for r in rows:
        if r.get("id") == row_id:
            r.update(row)
            break
    return {"message": f"row {row_id} updated"}
