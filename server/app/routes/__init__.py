"""
- Route principale de l'API
Rôle : Centraliser TOUTES les routes de l'application

CE FICHIER EST LE "CHEF D'ORCHESTRE" DES ROUTES
Les coéquipiers ajouteront leurs routes ici au fur et à mesure
"""

from fastapi import APIRouter

# ============================================================================
# CRÉATION DU ROUTEUR PRINCIPAL
# ============================================================================

main_router = APIRouter()

# ============================================================================
# IMPORT DES ROUTES
# ============================================================================

# Exemple:
# from app.routes import user_routes

# ============================================================================
# ENREGISTREMENT DES ROUTES 
# ============================================================================

# Chaque groupe de routes aura son propre préfixe
# main_router.include_router(user_routes.router, prefix="/users", tags=["Users"])
# main_router.include_router(product_routes.router, prefix="/products", tags=["Products"])
# main_router.include_router(order_routes.router, prefix="/orders", tags=["Orders"])

# ============================================================================
# ROUTES PUBLIQUES (accessibles sans authentification)
# ============================================================================

# Tu peux ajouter ici des routes qui ne nécessitent pas de token
# Exemple:
# @main_router.get("/public/health")
# async def public_health():
#     return {"status": "ok"}