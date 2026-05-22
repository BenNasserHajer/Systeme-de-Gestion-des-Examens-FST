from fastapi import APIRouter
from app.routers.planifications import router as planifications_router

# ✅ Routeur principal
api_router = APIRouter()

# ✅ Inclure le routeur des planifications
api_router.include_router(planifications_router)

# Si vous avez d'autres routeurs, ajoutez-les ici
# from app.routers.surveillances import router as surveillances_router
# api_router.include_router(surveillances_router)