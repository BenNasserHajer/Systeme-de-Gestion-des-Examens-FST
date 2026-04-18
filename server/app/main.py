"""
main.py - Point d'entrée principal de l'API FastAPI
Rôle : Initialiser l'application et enregistrer les routes

C'est le fichier qu'on exécute avec: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any

# ============================================================================
# IMPORTS DEPUIS NOTRE BASE DE DONNÉES
# ============================================================================

from app.database import (
    get_db,                    # Pour avoir une session BD
    check_connection,          # Pour tester PostgreSQL
    db_settings,               # Pour les paramètres
    engine,                    # Pour fermer les connexions
    Base                       # Pour créer les tables (optionnel)
)

# ============================================================================
# IMPORTS DES ROUTES 
# ============================================================================
from app.routes import main_router 

# ============================================================================
# CRÉATION DE L'APPLICATION FASTAPI
# ============================================================================

app = FastAPI(
    title="PFA Project",
    description="API avec architecture routes/controllers/services",
    version="1.0.0",
    docs_url="/docs",           # Documentation Swagger
    redoc_url="/redoc",         # Documentation alternative
)

# ============================================================================
# CONFIGURATION CORS (Pour Next.js)
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Tous les headers
)

# ============================================================================
# ENREGISTREMENT DU ROUTEUR PRINCIPAL
# ============================================================================
app.include_router(main_router, prefix="/api")

# ============================================================================
# ÉVÉNEMENT AU DÉMARRAGE 
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Vérifie que PostgreSQL est accessible au démarrage
    """
    print("\n" + "=" * 60)
    print("🚀 DÉMARRAGE DE L'API")
    print("=" * 60)
    
    # Afficher la configuration
    print("\n📋 CONFIGURATION:")
    print(f"   - Projet: {app.title}")
    print(f"   - Version: {app.version}")
    print(f"   - Base de données: {db_settings.DATABASE_URL.split('/')[-1]}")
    print(f"   - Pool de connexions: {db_settings.DATABASE_POOL_SIZE}")
    
    # Tester la connexion à PostgreSQL
    print("\n🔌 VÉRIFICATION BASE DE DONNÉES:")
    from app.database.connection import SessionLocal
    db = SessionLocal()
    
    if check_connection(db):
        print("   ✅ PostgreSQL : CONNECTÉ")
    else:
        print("   ❌ PostgreSQL : NON CONNECTÉ")
    
    db.close()
    
    # Afficher les endpoints disponibles
    print("\n📡 ENDPOINTS DISPONIBLES:")
    print(f"   - Documentation: http://localhost:8000/docs")
    print(f"   - Health check: http://localhost:8000/health")
    print(f"   - API v1: http://localhost:8000/api/v1 (quand les routes seront ajoutées)")
    
    print("\n" + "=" * 60)
    print("✅ API PRÊTE")
    print("=" * 60 + "\n")

# ============================================================================
# ÉVÉNEMENT À L'ARRÊT
# ============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """
    Ferme proprement les connexions à PostgreSQL
    """
    print("\n" + "=" * 60)
    print("🛑 ARRÊT DE L'API")
    print("=" * 60)
    
    # Fermer le pool de connexions
    engine.dispose()
    print("✅ Connexions PostgreSQL fermées")
    
    print("=" * 60 + "\n")

# ============================================================================
# ROUTES DE BASE (toujours disponibles)
# ============================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Route racine - Point d'entrée principal
    URL: GET /
    """
    return {
        "message": f"Bienvenue sur {app.title}",
        "version": app.version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    from datetime import datetime
    
    is_db_connected = check_connection(db)
    
    return {
        "status": "ok" if is_db_connected else "degraded",
        "api": "running",
        "database": "connected" if is_db_connected else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/info")
async def get_info() -> Dict[str, Any]:
    """
    Informations détaillées sur l'API
    URL: GET /info
    """
    return {
        "name": app.title,
        "version": app.version,
        "description": app.description,
        "database": {
            "type": "postgresql",
            "name": db_settings.DATABASE_URL.split('/')[-1],
            "pool_size": db_settings.DATABASE_POOL_SIZE,
            "max_overflow": db_settings.DATABASE_MAX_OVERFLOW
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "info": "/info"
        }
    }

# ============================================================================
# ROUTE DE TEST POUR LA BASE DE DONNÉES 
# ============================================================================

@app.get("/db-test")
async def test_database(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test_value, now() as current_time"))
        row = result.first()
        
        return {
            "success": True,
            "message": "Base de données accessible",
            "test_value": row.test_value,
            "current_time": str(row.current_time)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Erreur base de données",
            "detail": str(e)
        }