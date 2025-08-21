"""DBService: Business logic and SQLAlchemy operations for the DB Service API."""
from typing import Any

from fastapi import HTTPException
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select, text
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///db_service.sqlite3"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

class DBService:
    """Service that manages simple table CRUD using SQLAlchemy/SQLite."""

    def __init__(self) -> None:
        """Initialize the DB service with shared engine/metadata/session factory."""
        self.engine = engine
        self.metadata = metadata
        self.SessionLocal = SessionLocal

    def create_table(self, table_name: str, columns_dict: dict[str, str]) -> None:
        """Create or replace a table with the provided column declarations."""
        # Recreate table fresh each time to ensure deterministic tests
        try:
            self.metadata.reflect(bind=self.engine)
            if table_name in self.metadata.tables:
                existing = self.metadata.tables[table_name]
                existing.drop(bind=self.engine, checkfirst=True)
                self.metadata.remove(existing)

            cols: list[Column[Any]] = []
            for col, decl in columns_dict.items():
                if not col or not decl:
                    raise HTTPException(status_code=400, detail=f"Invalid column definition: {col}")
                up = str(decl).upper()
                coltype = Integer if "INTEGER" in up else String
                is_pk = "PRIMARY KEY" in up
                cols.append(Column(col, coltype, primary_key=is_pk))

            table = Table(table_name, self.metadata, *cols)
            table.create(bind=self.engine, checkfirst=False)
            self.metadata.reflect(bind=self.engine)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def list_tables(self) -> list[str]:
        """Return list of user table names."""
        try:
            self.metadata.reflect(bind=self.engine)
            return list(self.metadata.tables.keys())
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def get_table_schema(self, table_name: str) -> list[dict[str, str]]:
        """Return table schema as a list of name/type dicts."""
        try:
            self.metadata.reflect(bind=self.engine)
            if table_name not in self.metadata.tables:
                raise HTTPException(status_code=404, detail="Table not found.")
            table = self.metadata.tables[table_name]
            return [{"name": col.name, "type": str(col.type)} for col in table.columns]
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def delete_table(self, table_name: str) -> None:
        """Delete a table if it exists, else 404."""
        try:
            self.metadata.reflect(bind=self.engine)
            if table_name not in self.metadata.tables:
                raise HTTPException(status_code=404, detail="Table not found.")
            table = self.metadata.tables[table_name]
            table.drop(bind=self.engine, checkfirst=True)
            self.metadata.remove(table)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def insert_row(self, table_name: str, row: dict[str, Any]) -> int | None:
        """Insert a row and return the inserted primary key if present."""
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                ins = table.insert().values(**row)
                result = session.execute(ins)
                session.commit()
                if result.inserted_primary_key and result.inserted_primary_key[0] is not None:
                    return int(result.inserted_primary_key[0])
                return None
            except Exception as e:  # noqa: BLE001
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def get_rows(
        self,
        table_name: str,
        start_time: str | None,
        end_time: str | None,
        timestamp_column: str,
        columns: list[str] | None,
    ) -> list[dict[str, Any]]:
        """Return rows with optional timestamp filtering and column projection."""
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                sel_cols = [table.c[col] for col in columns] if columns else [table]
                stmt = select(*sel_cols)
                if start_time:
                    stmt = stmt.where(table.c[timestamp_column] >= start_time)
                if end_time:
                    stmt = stmt.where(table.c[timestamp_column] <= end_time)
                result = session.execute(stmt)
                return [dict(m) for m in result.mappings().all()]
            except Exception as e:  # noqa: BLE001
                raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def delete_row(self, table_name: str, row_id: int) -> None:
        """Delete a row by primary key or SQLite rowid fallback."""
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                pk_cols = list(table.primary_key.columns)
                key_col = pk_cols[0] if pk_cols else (table.c.get("id") if "id" in table.c else None)
                if key_col is None:
                    stmt = table.delete().where(text("rowid = :rowid")).params(rowid=row_id)
                else:
                    stmt = table.delete().where(key_col == row_id)
                result = session.execute(stmt)
                session.commit()
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Row not found.")
            except Exception as e:  # noqa: BLE001
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}") from e

    def update_row(self, table_name: str, row_id: int, row: dict[str, Any]) -> None:
        """Update a row by primary key or SQLite rowid fallback."""
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                pk_cols = list(table.primary_key.columns)
                key_col = pk_cols[0] if pk_cols else (table.c.get("id") if "id" in table.c else None)
                if key_col is None:
                    stmt = table.update().where(text("rowid = :rowid")).values(**row).params(rowid=row_id)
                else:
                    stmt = table.update().where(key_col == row_id).values(**row)
                result = session.execute(stmt)
                session.commit()
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Row not found.")
            except Exception as e:  # noqa: BLE001
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}") from e
