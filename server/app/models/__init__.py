"""
- Exporte tous les modèles
Rôle : Centraliser les modèles pour Alembic
"""

from app.database import Base

# IMPORTANT: Chaque développeur ajoutera ses modèles ici
# Exemple:
# from app.models.user import User
# from app.models.product import Product
__all__ = ["Base"]