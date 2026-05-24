"""
routers/auth_router.py
Routes d'authentification exposées par l'API.
"""
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.crud_auth import login, logout
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.utils.jwt_handler import get_current_user, decode_access_token, get_token_from_request

router = APIRouter(prefix="/auth", tags=["Authentification"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def route_login(
    payload:  LoginRequest,
    response: Response,
    db:       Session = Depends(get_db),
):
    """
    Login unifié pour admin et enseignant.
    - Retourne un JSON avec access_token + infos user
    - Injecte aussi le token dans un cookie HTTP-only (access_token)
    """
    return login(payload, response, db)


# ─────────────────────────────────────────────────────────────────────────────
# POST /auth/logout
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/logout")
def route_logout(response: Response):
    """Supprime le cookie d'authentification."""
    return logout(response)


# ─────────────────────────────────────────────────────────────────────────────
# GET /auth/me  — infos de l'utilisateur connecté
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/me")
def route_me(request: Request):
    """
    Retourne les infos du token (utilisateur courant).
    Fonctionne avec cookie OU header Authorization: Bearer <token>.
    """
    token = get_token_from_request(request)
    payload = decode_access_token(token)
    return {
        "type":          payload.get("type"),
        "id":            payload.get("id"),
        "email":         payload.get("email"),
        "enseignant_id": payload.get("enseignant_id"),
        "nom":           payload.get("nom"),
        "prenom":        payload.get("prenom"),
    }