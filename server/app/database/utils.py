"""
database/utils.py - Fonctions utilitaires pour la base de données
Rôle : Fournir des fonctions réutilisables pour les opérations BD
Quand : Utilisé par les services et les controllers
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
from app.database.constants import DBConstants
from app.database.config import db_settings

# ============================================================================
# VÉRIFICATION DE CONNEXION
# ============================================================================

def check_connection(db: Session) -> bool:
    """
    Vérifie si la connexion à PostgreSQL fonctionne
    
    Args:
        db: Session SQLAlchemy
        
    Returns:
        True si connecté, False sinon
    
    Utilisation:
        Dans le middleware ou au démarrage pour vérifier que tout va bien
    
    Exemple:
        if not check_connection(db):
            raise HTTPException(status_code=500, detail="BD inaccessible")
    """
    try:
        # Exécuter une requête simple pour tester la connexion
        # SELECT 1 est la requête la plus simple possible
        result = db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Erreur de connexion BD: {e}")
        return False

# ============================================================================
# PAGINATION
# ============================================================================

def paginate(page: int = 1, per_page: int = None) -> Dict[str, int]:
    """
    Calcule les paramètres de pagination pour les requêtes SQL
    
    Args:
        page: Numéro de la page (commence à 1)
        per_page: Nombre d'éléments par page
        
    Returns:
        Dictionnaire avec offset (départ) et limit (limite)
    
    Exemple:
        page=1, per_page=20 -> offset=0, limit=20 (premiers 20 éléments)
        page=2, per_page=20 -> offset=20, limit=20 (éléments 21 à 40)
        page=3, per_page=20 -> offset=40, limit=20 (éléments 41 à 60)
    """
    
    # Utiliser la valeur par défaut si non spécifiée
    if per_page is None:
        per_page = DBConstants.DEFAULT_PAGE_SIZE
    
    # S'assurer que page est au moins 1 (pas de page 0 ou négative)
    page = max(1, page)
    
    # Limiter per_page à la valeur maximale (protection contre les abus)
    per_page = min(per_page, DBConstants.MAX_PAGE_SIZE)
    
    # Calculer l'offset (combien d'éléments sauter)
    # Page 1: offset 0 (on saute 0 éléments)
    # Page 2: offset 20 (on saute les 20 premiers)
    offset = (page - 1) * per_page
    
    return {
        "offset": offset,
        "limit": per_page,
        "page": page,
        "per_page": per_page
    }

# ============================================================================
# GESTION DES ERREURS
# ============================================================================

def handle_error(error: Exception) -> Dict[str, Any]:
    """
    Transforme une erreur SQLAlchemy en réponse utilisateur lisible
    
    Args:
        error: L'erreur SQLAlchemy capturée
        
    Returns:
        Dictionnaire avec message d'erreur adapté
    
    Utilisation:
        try:
            db.commit()
        except Exception as e:
            return handle_error(e)
    """
    error_message = str(error).lower()
    
    # ========================================================================
    # ERREUR DE CONNEXION
    # ========================================================================
    if any(keyword in error_message for keyword in ["could not connect", "connection refused"]):
        return {
            "success": False,
            "error": "La base de données est inaccessible",
            "detail": "Vérifie que PostgreSQL est lancé"
        }
    
    # ========================================================================
    # ERREUR DE DUPLICATION (unique constraint)
    # ========================================================================
    if any(keyword in error_message for keyword in ["duplicate key", "unique constraint"]):
        return {
            "success": False,
            "error": "Cette ressource existe déjà",
            "detail": "Un enregistrement avec ces identifiants existe déjà"
        }
    
    # ========================================================================
    # ERREUR DE CLÉ ÉTRANGÈRE
    # ========================================================================
    if any(keyword in error_message for keyword in ["foreign key", "violates foreign key"]):
        return {
            "success": False,
            "error": "Référence invalide",
            "detail": "La ressource référencée n'existe pas"
        }
    
    # ========================================================================
    # ERREUR DE CONTRAINTE NOT NULL
    # ========================================================================
    if "null value" in error_message and "not-null" in error_message:
        return {
            "success": False,
            "error": "Champ obligatoire manquant",
            "detail": "Un champ requis n'a pas été fourni"
        }
    
    # ========================================================================
    # TIMEOUT
    # ========================================================================
    if "timeout" in error_message:
        return {
            "success": False,
            "error": "Requête trop longue",
            "detail": "La requête a dépassé le temps limite"
        }
    
    # ========================================================================
    # ERREUR GÉNÉRIQUE
    # ========================================================================
    return {
        "success": False,
        "error": "Erreur base de données",
        "detail": str(error)
    }

# ============================================================================
# EXÉCUTION DE REQUÊTE SÉCURISÉE
# ============================================================================

def execute_safe(db: Session, query: str, params: dict = None) -> Dict[str, Any]:
    """
    Exécute une requête SQL de manière sécurisée avec gestion d'erreur
    
    Args:
        db: Session SQLAlchemy
        query: Requête SQL (avec placeholders :param)
        params: Paramètres pour la requête
        
    Returns:
        Dictionnaire avec résultat ou erreur
    """
    try:
        # Exécuter la requête avec les paramètres
        result = db.execute(text(query), params or {})
        
        # Commit si c'est une modification (INSERT, UPDATE, DELETE)
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            db.commit()
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        db.rollback()  # Annuler les changements en cas d'erreur
        return handle_error(e)