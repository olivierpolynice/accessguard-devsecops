from typing import Final

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.security import create_access_token, hash_password, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: str


DEMO_PASSWORD: Final[str] = "AccessGuard123!"

DEMO_USERS: Final[dict[str, dict[str, str]]] = {
    "alice.employee@asteriatech.local": {
        "email": "alice.employee@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "employee",
    },
    "marc.manager@asteriatech.local": {
        "email": "marc.manager@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "manager",
    },
    "ines.itadmin@asteriatech.local": {
        "email": "ines.itadmin@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "it_admin",
    },
    "paul.security@asteriatech.local": {
        "email": "paul.security@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "security_admin",
    },
}


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(payload: LoginRequest) -> TokenResponse:
    normalized_email = payload.email.strip().lower()
    user = DEMO_USERS.get(normalized_email)

    if user is None or not verify_password(
        payload.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Adresse e-mail ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user["email"],
        role=user["role"],
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        email=user["email"],
    )
