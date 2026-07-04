from typing import Final

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Identifiants utilisés pour la connexion de démonstration."""

    email: str = Field(
        min_length=5,
        max_length=120,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    """Réponse retournée après une connexion réussie."""

    access_token: str
    token_type: str
    role: str


DEMO_USERS: Final[dict[str, dict[str, str]]] = {
    "alice.employee@asteriatech.local": {
        "role": "employee",
        "password_hash": hash_password("Employee123!"),
    },
    "marc.manager@asteriatech.local": {
        "role": "manager",
        "password_hash": hash_password("Manager123!"),
    },
    "ines.itadmin@asteriatech.local": {
        "role": "it_admin",
        "password_hash": hash_password("Admin123!"),
    },
    "sam.security@asteriatech.local": {
        "role": "security_admin",
        "password_hash": hash_password("Security123!"),
    },
}


def authenticate_user(email: str, password: str) -> dict[str, str] | None:
    """Retourne l'utilisateur si les identifiants sont valides."""

    user = DEMO_USERS.get(email)

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "email": email,
        "role": user["role"],
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion et génération d'un token JWT",
)
def login(payload: LoginRequest) -> TokenResponse:
    """Authentifie un utilisateur et retourne un Bearer token JWT."""

    user = authenticate_user(payload.email, payload.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects.",
        )

    access_token = create_access_token(
        subject=user["email"],
        role=user["role"],
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
    )