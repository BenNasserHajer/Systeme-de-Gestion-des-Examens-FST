"""
database/config.py - Configuration de la base de données
Rôle : Lire les variables d'environnement pour la BD
Quand : Importé par connection.py au démarrage
"""

import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
# load_dotenv() cherche .env à la racine du projet (dossier server/)
load_dotenv()

class DatabaseSettings:
    """
    Configuration spécifique à la base de données
    Toutes les variables commençant par DATABASE_ sont ici
    """
    
    # URL de connexion PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/mydb"
    )
    
    # Taille du pool de connexions (combien de connexions en parallèle)
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    
    # Connexions supplémentaires max (quand le pool est plein)
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    # Afficher les requêtes SQL dans la console ? (True = débogage)
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # Timeout des requêtes en secondes
    DATABASE_TIMEOUT: int = int(os.getenv("DATABASE_TIMEOUT", "30"))

# Créer une instance unique des settings
db_settings = DatabaseSettings()