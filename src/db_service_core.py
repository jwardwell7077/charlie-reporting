"""
DBService: Business logic and SQLAlchemy operations for the DB Service API.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, text
import os
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

DB_PATH = os.environ.get("DB_SERVICE_DB_PATH", "sqlite:///db_service.sqlite3")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

class DBService:
    def __init__(self):
        self.engine = engine
        self.metadata = metadata
        self.SessionLocal = SessionLocal

    def create_table(self, table_name: str, columns_dict: Dict[str, str]):
        columns: list[Column[Any]] = []
        for col, col_type in columns_dict.items():
            if not col or not col_type:
                raise HTTPException(status_code=400, detail=f"Invalid column definition: {col}")
            ct = str(col_type).strip().upper()
            is_pk = "PRIMARY KEY" in ct
            if "INT" in ct:
                coltype = Integer
            else:
                coltype = String
            columns.append(Column(col, coltype, primary_key=is_pk))
        try:
            table = Table(table_name, self.metadata, *columns, extend_existing=True)
            table.create(bind=self.engine, checkfirst=True)
            self.metadata.reflect(bind=self.engine)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def list_tables(self) -> List[str]:
        try:
            self.metadata.reflect(bind=self.engine)
            return list(self.metadata.tables.keys())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        try:
            self.metadata.reflect(bind=self.engine)
            if table_name not in self.metadata.tables:
                raise HTTPException(status_code=404, detail="Table not found.")
            table = self.metadata.tables[table_name]
            return [{"name": col.name, "type": str(col.type)} for col in table.columns]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def delete_table(self, table_name: str):
        try:
            self.metadata.reflect(bind=self.engine)
            if table_name not in self.metadata.tables:
                raise HTTPException(status_code=404, detail="Table not found.")
            table = self.metadata.tables[table_name]
            table.drop(bind=self.engine, checkfirst=True)
            self.metadata.remove(table)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def insert_row(self, table_name: str, row: Dict[str, Any]) -> Optional[int]:
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                ins = table.insert().values(**row)
                result = session.execute(ins)
                session.commit()
                return int(result.inserted_primary_key[0]) if result.inserted_primary_key and result.inserted_primary_key[0] is not None else None
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def get_rows(self, table_name: str, start_time: Optional[str], end_time: Optional[str], timestamp_column: str, columns: Optional[List[str]]) -> List[Dict[str, Any]]:
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
                # SQLAlchemy 2.x: use mappings() to get dictionaries reliably
                return [dict(m) for m in result.mappings().all()]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def delete_row(self, table_name: str, row_id: int):
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                # Prefer primary key if available
                pk_cols = list(table.primary_key.columns)
                if pk_cols:
                    stmt = table.delete().where(pk_cols[0] == row_id)
                else:
                    stmt = table.delete().where(text("rowid = :rowid")).params(rowid=row_id)
                result = session.execute(stmt)
                session.commit()
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Row not found.")
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def update_row(self, table_name: str, row_id: int, row: Dict[str, Any]):
        self.metadata.reflect(bind=self.engine)
        if table_name not in self.metadata.tables:
            raise HTTPException(status_code=404, detail="Table not found.")
        table = self.metadata.tables[table_name]
        with self.SessionLocal() as session:
            try:
                pk_cols = list(table.primary_key.columns)
                if pk_cols:
                    stmt = table.update().where(pk_cols[0] == row_id).values(**row)
                else:
                    stmt = table.update().where(text("rowid = :rowid")).values(**row).params(rowid=row_id)
                result = session.execute(stmt)
                session.commit()
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Row not found.")
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"DB error: {e}")

    # --- Ingestion log support ---
    def _ensure_ingestion_log(self) -> Table:
        try:
            self.metadata.reflect(bind=self.engine)
            if "ingestion_log" not in self.metadata.tables:
                log = Table(
                    "ingestion_log",
                    self.metadata,
                    Column("filename", String, primary_key=True),
                    Column("dataset", String),
                    Column("ingested_at", String),
                )
                log.create(bind=self.engine, checkfirst=True)
                self.metadata.reflect(bind=self.engine)
            return self.metadata.tables["ingestion_log"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def log_ingestion(self, filename: str, dataset: str, ingested_at: Optional[str] = None) -> None:
        log = self._ensure_ingestion_log()
        if not ingested_at:
            from datetime import datetime, timezone
            ingested_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.SessionLocal() as session:
            try:
                ins = log.insert().values(filename=filename, dataset=dataset, ingested_at=ingested_at)
                session.execute(ins)
                session.commit()
            except Exception as e:
                session.rollback()
                # Ignore duplicates (already logged)
                if "UNIQUE" in str(e):
                    return
                raise HTTPException(status_code=400, detail=f"DB error: {e}")

    def get_ingested_filenames(self, start_time: Optional[str], end_time: Optional[str]) -> List[str]:
        log = self._ensure_ingestion_log()
        with self.SessionLocal() as session:
            try:
                stmt = select(log.c.filename)
                if start_time:
                    stmt = stmt.where(log.c.ingested_at >= start_time)
                if end_time:
                    stmt = stmt.where(log.c.ingested_at <= end_time)
                result = session.execute(stmt)
                return [row[0] for row in result.fetchall()]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"DB error: {e}")
