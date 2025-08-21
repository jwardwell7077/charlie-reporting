"""Integration: Verify DBService time-window filtering by timestamp column."""
from src.db_service_core import DBService


def test_db_time_window_filtering_lexical_iso() -> None:
    svc = DBService()
    table = "events"
    # Ensure a clean slate if the table already exists from prior runs
    if table in svc.list_tables():
        svc.delete_table(table)
    # Create table with a timestamp column and a value
    svc.create_table(table, {"timestamp": "TEXT", "value": "TEXT"})
    # Insert three rows with ISO timestamps
    svc.insert_row(table, {"timestamp": "2025-08-20T10:00:00+00:00", "value": "a"})
    svc.insert_row(table, {"timestamp": "2025-08-20T11:00:00+00:00", "value": "b"})
    svc.insert_row(table, {"timestamp": "2025-08-20T12:00:00+00:00", "value": "c"})

    # Query rows between 10:30 and 11:30 should return only the middle one
    rows = svc.get_rows(
        table_name=table,
        start_time="2025-08-20T10:30:00+00:00",
        end_time="2025-08-20T11:30:00+00:00",
        timestamp_column="timestamp",
        columns=None,
    )
    # Expect exactly one row (the 11:00 row)
    assert len(rows) == 1
    assert rows[0]["value"] == "b"
