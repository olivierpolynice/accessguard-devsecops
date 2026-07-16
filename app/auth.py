from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.schemas import validate_internal_email
from app.security import create_access_token, verify_password
from app.user_repository import get_user_by_email_with_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    """Identifiants transmis pour ouvrir une session."""

    email: str = Field(
        min_length=5,
        max_length=255,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_internal_email(value)


class TokenResponse(BaseModel):
    """Réponse retournée après une authentification réussie."""

    access_token: str
    token_type: str = "bearer"
    role: str
    email: str


def raise_invalid_credentials() -> None:
    """
    Retourne une erreur générique afin de ne pas révéler
    si l'adresse e-mail existe dans la base.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Adresse e-mail ou mot de passe incorrect.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    payload: LoginRequest,
) -> TokenResponse:
    """
    Authentifie un utilisateur depuis la table users SQLite.

    Étapes :
    1. recherche de l'utilisateur par e-mail ;
    2. vérification de l'état du compte ;
    3. vérification du hash du mot de passe ;
    4. génération du JWT.
    """
    normalized_email = payload.email.strip().lower()

    user = get_user_by_email_with_password(
        normalized_email
    )

    if user is None:
        raise_invalid_credentials()

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte utilisateur est désactivé.",
        )

    if not verify_password(
        payload.password,
        user["password_hash"],
    ):
        raise_invalid_credentials()

    access_token = create_access_token(
        subject=user["email"],
        role=user["role"],
        user_id=user["id"],
        is_active=user["is_active"],
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        email=user["email"],
    )