from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from fastapi import Response, HTTPException, status, Request

# ─────────────────────────────────────────────────────────────────────────────
# Configuration  (à déplacer dans un fichier .env / settings en production)
# ─────────────────────────────────────────────────────────────────────────────

SECRET_KEY      = "CHANGE_MOI_EN_PRODUCTION_SECRET_TRES_LONG"   # ← changer
ALGORITHM       = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8   # 8 heures
COOKIE_NAME     = "access_token"


# ─────────────────────────────────────────────────────────────────────────────
# Création du token JWT
# ─────────────────────────────────────────────────────────────────────────────

def create_access_token(
    *,
    type:          Literal["ENSEIGNANT", "ADMIN"],
    email:         str,
    id:            int | None = None,
    enseignant_id: int | None = None,
    nom:           str | None = None,
    prenom:        str | None = None,
) -> str:
    """
    Génère un JWT signé contenant :
      - type          : "ENSEIGNANT" ou "ADMIN"
      - email         : adresse mail
      - id            : id du compte_enseignant (None pour admin)
      - enseignant_id : id de l'enseignant      (None pour admin)
      - nom / prenom  : informations display     (None pour admin)
      - exp           : date d'expiration
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "type":          type,
        "email":         email,
        "id":            id,
        "enseignant_id": enseignant_id,
        "nom":           nom,
        "prenom":        prenom,
        "exp":           expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────────────────────────────────────────
# Vérification / décodage du token
# ─────────────────────────────────────────────────────────────────────────────

def decode_access_token(token: str) -> dict:
    """
    Décode et vérifie le JWT.
    Lève HTTPException 401 si le token est invalide ou expiré.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Injection du token dans un cookie HTTP-only
# ─────────────────────────────────────────────────────────────────────────────

def set_auth_cookie(response: Response, token: str) -> None:
    """
    Place le JWT dans un cookie HTTP-only sécurisé.
    Le cookie n'est pas accessible en JavaScript (protection XSS).
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,           # non accessible par JS
        secure=False,            # mettre True en production (HTTPS)
        samesite="lax",          # protection CSRF basique
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def delete_auth_cookie(response: Response) -> None:
    """Supprime le cookie (logout)."""
    response.delete_cookie(key=COOKIE_NAME, path="/")


# ─────────────────────────────────────────────────────────────────────────────
# Extraction du token depuis la requête (cookie OU header Authorization)
# ─────────────────────────────────────────────────────────────────────────────

def get_token_from_request(request: Request) -> str:
    """
    Cherche le token dans :
    1. Le cookie HTTP-only  →  access_token
    2. Le header Authorization  →  Bearer <token>
    Lève 401 si rien n'est trouvé.
    """
    # 1 — Cookie
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return token

    # 2 — Header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non authentifié — token manquant",
        headers={"WWW-Authenticate": "Bearer"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Dépendance FastAPI — récupère l'utilisateur courant depuis le token
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user(request: Request) -> dict:
    """
    Dépendance FastAPI :
        from app.utils.jwt_handler import get_current_user
        @router.get("/me")
        def me(user = Depends(get_current_user)):
            ...
    Retourne le payload décodé du JWT.
    """
    token = get_token_from_request(request)
    return decode_access_token(token)


def require_admin(request: Request) -> dict:
    """Dépendance FastAPI — route réservée aux admins."""
    user = get_current_user(request)
    if user.get("type") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return user


def require_enseignant(request: Request) -> dict:
    """Dépendance FastAPI — route réservée aux enseignants."""
    user = get_current_user(request)
    if user.get("type") != "ENSEIGNANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux enseignants",
        )
    return user