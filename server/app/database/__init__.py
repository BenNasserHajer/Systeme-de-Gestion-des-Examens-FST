"""
database/__init__.py - Point d'entrée du module database
Rôle : Exporter ce qui est nécessaire aux autres modules
Quand : Importé par les modèles et main.py

Utilisation exemple dans main.py:
    from app.database import get_db, Base, engine
"""

# Exporter les composants principaux pour qu'ils soient facilement accessibles
from app.database.connection import (
    engine,          # Le moteur SQLAlchemy
    SessionLocal,    # La fabrique de sessions
    Base,            # La classe de base pour les modèles
    get_db           # La dépendance FastAPI pour les routes
)

from app.database.config import db_settings
from app.database.constants import DBConstants, TableNames
from app.database.utils import check_connection, paginate, handle_error

# Ce qui est disponible quand on fait: from app.database import *
__all__ = [
    # Connection
    "engine",
    "SessionLocal", 
    "Base",
    "get_db",
    
    # Config
    "db_settings",
    
    # Constants
    "DBConstants",
    "TableNames",
    
    # Utils
    "check_connection",
    "paginate",
    "handle_error"
]