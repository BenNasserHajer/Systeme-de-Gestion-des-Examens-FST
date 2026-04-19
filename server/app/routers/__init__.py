"""API router composition."""

from fastapi import APIRouter

from app.routers.planifications import router as planifications_router
from app.routers.referentiel import router as referentiel_router
from app.routers.surveillances import router as surveillances_router

api_router = APIRouter()
api_router.include_router(planifications_router, tags=["Planification"])
api_router.include_router(surveillances_router, prefix="/surveillances", tags=["Surveillance"])
api_router.include_router(referentiel_router, prefix="/referentiel", tags=["Referentiel"])
