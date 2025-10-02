"""
Main FastAPI application for the decision tree API - LongBow Core + VM Builder Only
"""

from fastapi import FastAPI
from api.db.migrate import apply_migrations
from api.settings import get_db_path
from api.routers.health import router as health_router
from api.routers.import_router import router as import_router
from api.routers.tree_export_router import router as export_router
from api.routers.tree_basic import router as tree_basic_router
from api.routers.conflicts import router as conflicts_router

app = FastAPI(
    title="Lorien - VM Builder",
    description="Minimal decision tree API for VM Builder with LongBow import/export",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
def on_startup():
    apply_migrations(get_db_path())

app.include_router(health_router, prefix="/api/v1")
app.include_router(import_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(conflicts_router, prefix="/api/v1")
app.include_router(tree_basic_router)