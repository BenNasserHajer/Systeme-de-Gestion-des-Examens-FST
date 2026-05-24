"""Main FastAPI application entry point."""

import uvicorn
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
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

# CORS configuration dynamique
_cors_origins = [
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    messages = [
        f"{'.'.join(str(part) for part in err.get('loc', []))}: {err.get('msg', 'invalid')}"
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": " | ".join(messages)},
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(
    _request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "Contrainte base de donnees: verifiez section_matiere_id, session et salles. "
                f"{exc.orig}"
            )
        },
    )

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize tables and validate DB connectivity at startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        connected = check_connection(db)
        status = "connected" if connected else "disconnected"
        print(f"[startup] database: {status}")
        print(f"[startup] server: http://{settings.backend_host}:{settings.backend_port}")
        print(f"[startup] CORS allowed: {_cors_origins}")
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
        "server": {
            "host": settings.backend_host,
            "port": settings.backend_port,
        },
    }

# Lancement direct
if __name__ == "__main__":
    print(f" Starting {settings.app_name} v{settings.app_version}")
    print(f" Server: http://{settings.backend_host}:{settings.backend_port}")
    print(f" API Docs: http://{settings.backend_host}:{settings.backend_port}/docs")
    
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )