"""Main FastAPI application entry point."""

from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, SessionLocal, check_connection, engine, get_db
from app.models import planification as _planification_model  # noqa: F401
from app.models import surveillance as _surveillance_model  # noqa: F401
from app.routers import api_router

app = FastAPI(
    title=settings.app_name,
    description="API architecture with thin routers and service-based business logic.",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize tables and validate DB connectivity at startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        connected = check_connection(db)
        status = "connected" if connected else "disconnected"
        print(f"[startup] database: {status}")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Release DB resources on app shutdown."""
    engine.dispose()


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": f"Welcome to {app.title}",
        "version": app.version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    is_db_connected = check_connection(db)
    return {
        "status": "ok" if is_db_connected else "degraded",
        "database": "connected" if is_db_connected else "disconnected",
        "timestamp": datetime.now().isoformat(),
    }