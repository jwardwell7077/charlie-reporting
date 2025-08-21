"""Standalone FastAPI app for SharePoint simulator service.

Run with:
    uvicorn sharepoint_sim.server:app --reload --port 8001
"""
from fastapi import FastAPI

from sharepoint_sim.api import router as sim_router

app = FastAPI(title="SharePoint CSV Simulator API", docs_url="/docs", redoc_url="/redoc")
app.include_router(sim_router)
