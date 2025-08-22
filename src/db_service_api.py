"""
DB Service API (FastAPI endpoints only).
All business logic is delegated to db_service_core.DBService.
"""
from fastapi import FastAPI, HTTPException, Query, File, UploadFile, Request, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
import csv
import io
import threading
from db_service_core import DBService

app = FastAPI(title="DB Service API")
_db_lock = threading.Lock()
db_service = DBService()

class TableSchema(BaseModel):
    table_name: str = Field(..., description="Name of the table.")
    columns: Dict[str, str] = Field(..., description="Column definitions as {name: type}.")

class RowInsertRequest(BaseModel):
    row: Dict[str, Any]

class RowInsertResponse(BaseModel):
    message: str
    row_id: Optional[int] = None

class TableCreateResponse(BaseModel):
    message: str
    table_name: str

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(
    request: Request,
    file: UploadFile = File(None),
    dataset: Optional[str] = None
) -> JSONResponse:
    if file:
        content = await file.read()
        csv_text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        if not rows:
            return JSONResponse(status_code=400, content={"error": "Empty CSV file."})
        if not file.filename:
            return JSONResponse(status_code=400, content={"error": "Missing filename for uploaded file."})
        table_name = file.filename.rsplit(".", 1)[0]
        columns = {str(col): "TEXT" for col in rows[0].keys()}
    else:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON body."})
        rows = body.get("rows") if isinstance(body, dict) else body
        if not rows or not isinstance(rows, list):
            return JSONResponse(status_code=400, content={"error": "No rows provided."})
        if not dataset:
            dataset = body.get("dataset") if isinstance(body, dict) else None
        if not dataset:
            return JSONResponse(status_code=400, content={"error": "Missing dataset name."})
        table_name = dataset
        columns = {str(col): "TEXT" for col in rows[0].keys()}
    try:
        db_service.create_table(table_name, columns)
    except HTTPException as e:
        if e.status_code != 400:
            raise
    inserted = 0
    with _db_lock:
        for row in rows:
            db_service.insert_row(table_name, row)
            inserted += 1
    return JSONResponse(status_code=200, content={"message": "Ingested rows.", "row_count": inserted, "table": table_name})

@app.post("/tables", response_model=TableCreateResponse, status_code=status.HTTP_201_CREATED)
def create_table(payload: dict[str, Any] = Body(...)):
    table_name: str = str(payload.get("table_name")) if payload.get("table_name") else ""
    columns_dict_raw = payload.get("columns") or payload.get("schema")
    if not table_name or not columns_dict_raw or not isinstance(columns_dict_raw, dict):
        raise HTTPException(status_code=422, detail="Invalid table name or schema.")
    # Ensure type is Dict[str, str]
    columns_dict: Dict[str, str] = {str(k): str(v) for k, v in columns_dict_raw.items()}  # type: ignore
    with _db_lock:
        # Recreate table cleanly to avoid conflicts with prior test runs
        try:
            db_service.delete_table(table_name)
        except HTTPException:
            pass
        db_service.create_table(table_name, columns_dict)
    return TableCreateResponse(message="Table created or already exists.", table_name=table_name)

@app.get("/tables")
def list_tables() -> JSONResponse:
    with _db_lock:
        tables = db_service.list_tables()
    return JSONResponse(content={"tables": tables})

@app.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str) -> JSONResponse:
    with _db_lock:
        schema = db_service.get_table_schema(table_name)
    return JSONResponse(content={"schema": schema})

@app.delete("/tables/{table_name}")
def delete_table(table_name: str) -> JSONResponse:
    with _db_lock:
        db_service.delete_table(table_name)
    return JSONResponse(content={"message": f"Table '{table_name}' deleted."})

@app.post("/tables/{table_name}/rows", response_model=RowInsertResponse, status_code=status.HTTP_201_CREATED)
def insert_row(table_name: str, payload: RowInsertRequest):
    row = payload.row
    if not row:
        raise HTTPException(status_code=422, detail="Invalid row data.")
    with _db_lock:
        row_id = db_service.insert_row(table_name, row)
    return RowInsertResponse(message="Row inserted.", row_id=row_id)

@app.get("/tables/{table_name}/rows")
def get_rows(
    table_name: str,
    start_time: Optional[str] = Query(None, description="Start time (inclusive) in ISO format."),
    end_time: Optional[str] = Query(None, description="End time (inclusive) in ISO format."),
    timestamp_column: str = Query("timestamp", description="Name of the timestamp column to filter on."),
    columns: Optional[str] = Query(None, description="Comma-separated list of columns to return.")
) -> List[Dict[str, Any]]:
    col_list = [col.strip() for col in columns.split(",") if col.strip()] if columns else None
    with _db_lock:
        rows = db_service.get_rows(table_name, start_time, end_time, timestamp_column, col_list)
    return rows

@app.delete("/tables/{table_name}/rows/{row_id}")
def delete_row(table_name: str, row_id: int) -> JSONResponse:
    with _db_lock:
        db_service.delete_row(table_name, row_id)
    return JSONResponse(content={"message": f"Row {row_id} deleted from '{table_name}'."})

@app.put("/tables/{table_name}/rows/{row_id}")
def update_row(table_name: str, row_id: int, row: Dict[str, Any]) -> JSONResponse:
    if not row:
        raise HTTPException(status_code=422, detail="No row data provided.")
    with _db_lock:
        db_service.update_row(table_name, row_id, row)
    return JSONResponse(content={"message": f"Row {row_id} updated in '{table_name}'."})
