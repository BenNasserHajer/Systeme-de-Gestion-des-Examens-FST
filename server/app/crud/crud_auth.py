"""
crud/crud_auth.py
Logique d'authentification :
  - Enseignant  → vérifie email + mot_de_passe dans la table compte_enseignant
  - Admin       → vérifie email + mot_de_passe contre des constantes backend (pas de BDD)
"""
from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session

from app.models.compte_enseignant import CompteEnseignant
from app.models.enseignant import Enseignant
from app.schemas.auth_schema import LoginRequest, LoginResponse, UserInfo
from app.utils.jwt_handler import create_access_token, set_auth_cookie

# ─────────────────────────────────────────────────────────────────────────────
# Credentials admin (hardcodés dans le backend, pas en base)
# ─────────────────────────────────────────────────────────────────────────────

ADMIN_EMAIL    = "admin@fst.utm.tn"
ADMIN_PASSWORD = "Admin@2026"          # ← changer en production


# ─────────────────────────────────────────────────────────────────────────────
# Helper — vérification mot de passe en clair
# ─────────────────────────────────────────────────────────────────────────────

def _verify_password(plain: str, stored: str) -> bool:
    """
    Comparaison simple en clair.
    En production : remplacer par bcrypt.checkpw() ou argon2.
    """
    return plain == stored


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN ADMIN
# ─────────────────────────────────────────────────────────────────────────────

def login_admin(payload: LoginRequest, response: Response) -> LoginResponse:
    """
    Vérifie les credentials admin contre les constantes backend.
    Retourne un LoginResponse avec type='ADMIN' et injecte le cookie.
    """
    if payload.email != ADMIN_EMAIL or payload.mot_de_passe != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    token = create_access_token(
        type="ADMIN",
        email=ADMIN_EMAIL,
        id=None,
        enseignant_id=None,
    )

    # Injecter le token dans le cookie HTTP-only
    set_auth_cookie(response, token)

    user_info = UserInfo(
        type="ADMIN",
        email=ADMIN_EMAIL,
        id=None,
        enseignant_id=None,
        nom=None,
        prenom=None,
    )

    return LoginResponse(access_token=token, user=user_info)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN ENSEIGNANT
# ─────────────────────────────────────────────────────────────────────────────

def login_enseignant(
    payload: LoginRequest,
    response: Response,
    db: Session,
) -> LoginResponse:
    """
    Vérifie email + mot_de_passe dans la table compte_enseignant.
    Retourne un LoginResponse avec type='ENSEIGNANT' et injecte le cookie.
    """
    # 1 — Chercher le compte par email
    compte = (
        db.query(CompteEnseignant)
        .filter(CompteEnseignant.email == payload.email)
        .first()
    )

    if not compte:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    # 2 — Vérifier que le compte est actif
    if not compte.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé — contacter l'administrateur",
        )

    # 3 — Vérifier le mot de passe
    if not _verify_password(payload.mot_de_passe, compte.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    # 4 — Récupérer les infos de l'enseignant
    enseignant = (
        db.query(Enseignant)
        .filter(Enseignant.id == compte.enseignant_id)
        .first()
    )

    # 5 — Créer le token JWT
    token = create_access_token(
        type="ENSEIGNANT",
        email=compte.email,
        id=compte.id,
        enseignant_id=compte.enseignant_id,
        nom=enseignant.nom       if enseignant else None,
        prenom=enseignant.prenom if enseignant else None,
    )

    # 6 — Injecter dans le cookie HTTP-only
    set_auth_cookie(response, token)

    user_info = UserInfo(
        type="ENSEIGNANT",
        email=compte.email,
        id=compte.id,
        enseignant_id=compte.enseignant_id,
        nom=enseignant.nom       if enseignant else None,
        prenom=enseignant.prenom if enseignant else None,
    )

    return LoginResponse(access_token=token, user=user_info)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN UNIFIÉ  (détecte automatiquement admin ou enseignant)
# ─────────────────────────────────────────────────────────────────────────────

def login(
    payload: LoginRequest,
    response: Response,
    db: Session,
) -> LoginResponse:
    """
    Point d'entrée unique :
      - Si l'email correspond à ADMIN_EMAIL → login_admin
      - Sinon → login_enseignant
    """
    if payload.email == ADMIN_EMAIL:
        return login_admin(payload, response)
    return login_enseignant(payload, response, db)


# ─────────────────────────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────────────────────────

def logout(response: Response) -> dict:
    """Supprime le cookie d'authentification."""
    from app.utils.jwt_handler import delete_auth_cookie
    delete_auth_cookie(response)
    return {"message": "Déconnexion réussie"}


# ─────────────────────────────────────────────────────────────────────────────
# GET compte enseignant (utilitaire)
# ─────────────────────────────────────────────────────────────────────────────

def get_compte_by_email(db: Session, email: str) -> CompteEnseignant | None:
    return db.query(CompteEnseignant).filter(CompteEnseignant.email == email).first()


def get_compte_by_enseignant_id(db: Session, enseignant_id: int) -> CompteEnseignant | None:
    return (
        db.query(CompteEnseignant)
        .filter(CompteEnseignant.enseignant_id == enseignant_id)
        .first()
    )