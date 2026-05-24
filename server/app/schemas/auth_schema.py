"""
schemas/auth_schema.py
Schémas Pydantic pour l'authentification (enseignant + admin).
"""
from pydantic import BaseModel, EmailStr
from typing import Literal


# ─────────────────────────────────────────────────────────────────────────────
# Requête de login (même formulaire pour enseignant et admin)
# ─────────────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:       str
    mot_de_passe: str

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Payload stocké dans le JWT
# ─────────────────────────────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    type:          Literal["ENSEIGNANT", "ADMIN"]
    id:            int | None = None   # None pour admin (pas en base)
    email:         str
    enseignant_id: int | None = None   # renseigné uniquement pour ENSEIGNANT


# ─────────────────────────────────────────────────────────────────────────────
# Réponse renvoyée après login
# ─────────────────────────────────────────────────────────────────────────────

class LoginResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user: "UserInfo"

    model_config = {"from_attributes": True}


class UserInfo(BaseModel):
    type:          Literal["ENSEIGNANT", "ADMIN"]
    id:            int | None = None
    email:         str
    enseignant_id: int | None = None
    nom:           str | None = None   # prénom + nom pour enseignant
    prenom:        str | None = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Schéma DB (lecture)
# ─────────────────────────────────────────────────────────────────────────────

class CompteEnseignantRead(BaseModel):
    id:            int
    enseignant_id: int
    email:         str
    type_compte:   str
    actif:         bool

    model_config = {"from_attributes": True}