"""
Test suite for the DB Service API.

Covers all endpoints and behaviors as specified in
docs/design-specs/db_service_api_spec.md.

All tests use Google-style docstrings and strict code standards.
"""

import pytest
from fastapi.testclient import TestClient



# Import the FastAPI app
from src.db_service_api import app

# Create the TestClient for the FastAPI app
client = TestClient(app)


@pytest.fixture(scope="module")
def test_client():
    """Fixture for FastAPI test client."""
    return client


def test_health_check(test_client: TestClient):
    """
    Test the /health endpoint returns 200 and expected payload.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_table(test_client: TestClient):
    """
    Test POST /tables creates a new table with valid schema.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    response = test_client.post("/tables", json={"table_name": "test_table", "schema": {"id": "int"}})
    assert response.status_code == 201

def test_create_table_invalid_schema(test_client: TestClient):
    """
    Test POST /tables with invalid schema returns 422 (Unprocessable Entity).

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    response = test_client.post("/tables", json={"table_name": "bad_table", "schema": None})
    assert response.status_code == 422

def test_list_tables(test_client: TestClient):
    """
    Test GET /tables returns a list of tables.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create a table to ensure at least one exists
    test_client.post("/tables", json={"table_name": "list_table", "schema": {"id": "INTEGER"}})
    response = test_client.get("/tables")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert "list_table" in data["tables"]

def test_insert_row(test_client: TestClient):
    """
    Test POST /tables/{table_name}/rows inserts a row.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Use a unique table name to avoid conflicts
    table_name = "insert_row_table"
    test_client.post("/tables", json={
        "table_name": table_name,
        "columns": {"id": "INTEGER PRIMARY KEY", "value": "INTEGER"}
    })
    response = test_client.post(f"/tables/{table_name}/rows", json={"row": {"id": 1, "value": 42}})
    assert response.status_code == 201

def test_insert_row_invalid(test_client: TestClient):
    """
    Test POST /tables/{table_name}/rows with invalid data returns 422 (Unprocessable Entity).

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    response = test_client.post("/tables/test_table/rows", json={"row": None})
    assert response.status_code == 422

def test_get_rows(test_client: TestClient):
    """
    Test GET /tables/{table_name}/rows returns rows with optional filters, time intervals, and column selection.

    Args:
        test_client (TestClient): FastAPI test client fixture.

    Returns:
        None
    """
    # Setup: create table and insert rows with timestamps
    test_client.post("/tables", json={
        "table_name": "time_table",
        "schema": {"id": "INTEGER PRIMARY KEY", "timestamp": "TEXT", "value": "INTEGER"}
    })
    rows = [
        {"id": 1, "timestamp": "2025-08-19T10:00:00", "value": 100},
        {"id": 2, "timestamp": "2025-08-19T11:00:00", "value": 200},
        {"id": 3, "timestamp": "2025-08-19T12:00:00", "value": 300},
    ]
    for row in rows:
        test_client.post("/tables/time_table/rows", json={"row": row})

    # No filter: should return all rows
    response = test_client.get("/tables/time_table/rows")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Filter: start_time only
    response = test_client.get("/tables/time_table/rows?start_time=2025-08-19T11:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(row["timestamp"] >= "2025-08-19T11:00:00" for row in data)

    # Filter: end_time only
    response = test_client.get("/tables/time_table/rows?end_time=2025-08-19T11:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(row["timestamp"] <= "2025-08-19T11:00:00" for row in data)

    # Filter: start_time and end_time
    response = test_client.get("/tables/time_table/rows?start_time=2025-08-19T10:30:00&end_time=2025-08-19T11:30:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 2
    
    # Filter: columns only (single column)
    response = test_client.get("/tables/time_table/rows?columns=id")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(list(row.keys()) == ["id"] for row in data)

    # Filter: columns only (multiple columns)
    response = test_client.get("/tables/time_table/rows?columns=id,value")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(set(row.keys()) == {"id", "value"} for row in data)

    # Filter: columns with time interval
    response = test_client.get("/tables/time_table/rows?columns=id,value&start_time=2025-08-19T11:00:00&end_time=2025-08-19T12:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(set(row.keys()) == {"id", "value"} for row in data)

def test_get_table_schema(test_client: TestClient):
    """
    Test GET /tables/{table_name}/schema returns the table schema.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create table
    test_client.post("/tables", json={"table_name": "schema_table", "schema": {"id": "INTEGER", "val": "TEXT"}})
    response = test_client.get("/tables/schema_table/schema")
    assert response.status_code == 200
    data = response.json()
    assert "schema" in data
    col_names = {col["name"] for col in data["schema"]}
    assert {"id", "val"}.issubset(col_names)

def test_delete_table(test_client: TestClient):
    """
    Test DELETE /tables/{table_name} deletes the table.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create table
    test_client.post("/tables", json={"table_name": "delete_table", "schema": {"id": "INTEGER"}})
    response = test_client.delete("/tables/delete_table")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data and "deleted" in data["message"]

def test_delete_row(test_client: TestClient):
    """
    Test DELETE /tables/{table_name}/rows/{row_id} deletes a row.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create table and insert row
    test_client.post("/tables", json={"table_name": "delrow_table", "schema": {"id": "INTEGER PRIMARY KEY", "val": "TEXT"}})
    test_client.post("/tables/delrow_table/rows", json={"row": {"id": 1, "val": "foo"}})
    response = test_client.delete("/tables/delrow_table/rows/1")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data and "deleted" in data["message"]

def test_update_row(test_client: TestClient):
    """
    Test PUT /tables/{table_name}/rows/{row_id} updates a row.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create table and insert row
    test_client.post("/tables", json={"table_name": "uprow_table", "schema": {"id": "INTEGER PRIMARY KEY", "val": "TEXT"}})
    test_client.post("/tables/uprow_table/rows", json={"row": {"id": 1, "val": "foo"}})
    response = test_client.put("/tables/uprow_table/rows/1", json={"id": 1, "val": "bar"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data and "updated" in data["message"]

def test_update_row_invalid(test_client: TestClient):
    """
    Test PUT /tables/{table_name}/rows/{row_id} with invalid data returns 400.

    Args:
        test_client (TestClient): FastAPI test client fixture.
    """
    # Create table and insert row
    test_client.post("/tables", json={"table_name": "upinv_table", "schema": {"id": "INTEGER PRIMARY KEY", "val": "TEXT"}})
    test_client.post("/tables/upinv_table/rows", json={"row": {"id": 1, "val": "foo"}})
    response = test_client.put("/tables/upinv_table/rows/1", json=None)
    assert response.status_code == 422
