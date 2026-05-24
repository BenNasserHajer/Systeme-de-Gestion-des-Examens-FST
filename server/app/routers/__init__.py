"""API router composition."""

from fastapi import APIRouter

from app.routers.planification_workflow import router as planification_workflow_router
from app.routers.planifications import router as planifications_router
from app.routers.referentiel import router as referentiel_router
from app.routers.salles import router as salles_router
from app.routers.surveillances import router as surveillances_router
from app.routers.helpers import router as session_router  

api_router = APIRouter()
api_router.include_router(planifications_router, tags=["Planification"])
api_router.include_router(planification_workflow_router, tags=["Planification Workflow"])
api_router.include_router(surveillances_router, tags=["Surveillance"])
api_router.include_router(salles_router, tags=["Salles"])
api_router.include_router(referentiel_router, prefix="/referentiel", tags=["Referentiel"])
api_router.include_router(session_router, tags=["Sessions"])  