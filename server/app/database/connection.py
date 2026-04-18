"""
database/connection.py - Connexion à PostgreSQL
Rôle : Établir et gérer la connexion avec PostgreSQL
C'est le fichier le PLUS IMPORTANT pour la base de données !

Ce fichier contient:
    - engine: Le moteur qui parle à PostgreSQL
    - SessionLocal: La fabrique qui crée des sessions
    - Base: La classe dont héritent tous les modèles
    - get_db: La fonction pour les routes FastAPI
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Importer la configuration
from app.database.config import db_settings

# ============================================================================
# 1. CRÉATION DU MOTEUR (ENGINE)
# ============================================================================
"""
create_engine() : Établit la connexion avec PostgreSQL
- C'est le "câble" qui relie ton app à la base de données
- Créé UNE SEULE fois au démarrage de l'application
- Reste actif tant que l'app tourne
"""

engine = create_engine(
    # URL de connexion (ex: postgresql://postgres:password@localhost:5432/mydb)
    url=db_settings.DATABASE_URL,
    
    # Taille du pool de connexions (combien de connexions en parallèle)
    pool_size=db_settings.DATABASE_POOL_SIZE,
    
    # Connexions supplémentaires si le pool est plein
    max_overflow=db_settings.DATABASE_MAX_OVERFLOW,
    
    # Vérifier que la connexion est encore valide avant de l'utiliser
    # Évite les erreurs de connexion expirée
    pool_pre_ping=True,
    
    # Afficher les requêtes SQL dans la console (True = mode débogage)
    echo=db_settings.DATABASE_ECHO,
    
    # Timeout des connexions
    pool_recycle=3600,  # Reconnexion après 1 heure
)

# ============================================================================
# 2. CRÉATION DE LA SESSION LOCALE
# ============================================================================
"""
SessionLocal : Fabrique qui crée des sessions de base de données
- Une session = une conversation avec PostgreSQL
- Chaque requête API a sa propre session
- La session est automatiquement fermée après la requête
"""

SessionLocal = sessionmaker(
    autocommit=False,    # Désactiver l'autocommit (nous contrôlons manuellement)
    autoflush=False,     # Désactiver l'autoflush (plus de contrôle)
    bind=engine          # Lier cette session au moteur créé ci-dessus
)

# ============================================================================
# 3. CRÉATION DE LA BASE POUR LES MODÈLES
# ============================================================================
"""
Base : Classe dont héritent TOUS les modèles SQLAlchemy
- Tous les modèles (dans app/models/) doivent hériter de Base
- SQLAlchemy utilise Base pour créer les tables dans PostgreSQL
"""

Base = declarative_base()

# ============================================================================
# 4. FONCTION POUR OBTENIR UNE SESSION (DÉPENDANCE FASTAPI)
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Fonction de dépendance pour FastAPI.
    Crée une session et la ferme automatiquement après utilisation.
    
    COMMENT L'UTILISER DANS UNE ROUTE:
    
    from fastapi import Depends
    from app.database import get_db
    from sqlalchemy.orm import Session
    
    @router.get("/users")
    def get_users(db: Session = Depends(get_db)):
        # db est une session ouverte et prête à l'emploi
        users = db.query(User).all()
        return users
        # La session est automatiquement fermée à la fin
    
    POURQUOI yield au lieu de return ?
    - yield donne la session à la route
    - Après que la route a fini, l'exécution revient ici
    - Le code dans finally s'exécute pour fermer la session
    """
    
    # Créer une nouvelle session
    db = SessionLocal()
    
    try:
        # Donner la session à la route qui a appelé get_db()
        yield db
        
    finally:
        # Quoi qu'il arrive (erreur ou succès), fermer la session
        # C'est IMPORTANT pour libérer les ressources PostgreSQL
        db.close()