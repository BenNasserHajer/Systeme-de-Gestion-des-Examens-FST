"""
- Constantes pour la base de données
Rôle : Stocker toutes les valeurs fixes utilisées par la BD
Quand : Importé par les modèles et les services
"""

class DBConstants:
    """
    Constantes générales pour la base de données
    """
    
    # ========================================================================
    # LIMITES DES CHAMPS (utilisées dans les modèles)
    # ========================================================================
    
    # Strings courts (noms, emails, username, etc.)
    MAX_STRING_LENGTH: int = 255
    
    # Strings moyens (descriptions courtes, titres, etc.)
    MAX_MEDIUM_LENGTH: int = 500
    
    # Strings longs (descriptions longues, contenu, etc.)
    MAX_LONG_LENGTH: int = 1000
    
    # Strings très longs (texte libre, articles, etc.)
    MAX_TEXT_LENGTH: int = 10000
    
    # ========================================================================
    # PAGINATION (pour les requêtes qui retournent des listes)
    # ========================================================================
    
    # Nombre d'éléments par défaut par page
    DEFAULT_PAGE_SIZE: int = 20
    
    # Nombre maximum d'éléments qu'on peut demander
    MAX_PAGE_SIZE: int = 100
    
    # ========================================================================
    # TEMPS ET DÉLAIS
    # ========================================================================
    
    # Timeout des requêtes en secondes
    QUERY_TIMEOUT: int = 30
    
    # Temps entre deux tentatives de reconnexion (secondes)
    RECONNECT_DELAY: int = 5

class TableNames:
    """
    Noms standards pour toutes les tables
    Centraliser ici pour éviter les fautes de frappe
    """
    
    # Exemples (à adapter selon tes besoins)
    USERS: str = "users"
    ITEMS: str = "items"
    CATEGORIES: str = "categories"
    ORDERS: str = "orders"
    
    # Tu ajouteras d'autres tables ici au fur et à mesure

class ErrorMessages:
    """
    Messages d'erreur standards pour la base de données
    """
    
    CONNECTION_FAILED: str = "Impossible de se connecter à la base de données"
    QUERY_FAILED: str = "Erreur lors de l'exécution de la requête"
    NOT_FOUND: str = "Ressource non trouvée dans la base de données"
    DUPLICATE_ENTRY: str = "Cette ressource existe déjà"
    FOREIGN_KEY_ERROR: str = "Référence invalide vers une autre ressource"
    CONSTRAINT_VIOLATION: str = "Violation d'une contrainte de base de données"
    TIMEOUT: str = "La requête a pris trop de temps"