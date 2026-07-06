import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

SECRET_KEY = os.getenv(
    "ACCESSGUARD_SECRET_KEY",
    "accessguard-local-demo-secret-change-in-production",
)
ALGORITHM = os.getenv("ACCESSGUARD_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESSGUARD_TOKEN_EXPIRE_MINUTES", "60")
)

# auto_error=False permet de retourner 401 au lieu d'un 403 automatique
# lorsque le token Bearer est absent.
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Crée un hash bcrypt pour un mot de passe de démonstration."""
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hash.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe avec son hash bcrypt."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(subject: str, role: str) -> str:
    """Crée un JWT contenant l'identité et le rôle de l'utilisateur."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expires_at,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def normalize_role(role: str) -> str:
    """
    Convertit certains noms de rôles courants vers les rôles V2.

    Cela évite un problème si ta V1 utilise par exemple "admin"
    au lieu de "it_admin".
    """
    normalized = role.strip().lower()

    role_aliases = {
        "employee": "employee",
        "user": "employee",
        "standard_user": "employee",
        "manager": "manager",
        "it_admin": "it_admin",
        "itadmin": "it_admin",
        "admin": "it_admin",
        "administrator": "it_admin",
        "security_admin": "security_admin",
        "securityadmin": "security_admin",
        "security": "security_admin",
    }

    return role_aliases.get(normalized, normalized)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, str]:
    """
    Vérifie le JWT transmis dans Authorization: Bearer <token>
    et retourne l'identité de l'utilisateur connecté.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Un token JWT Bearer est requis.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT a expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT est invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    email = payload.get("sub")
    role = payload.get("role")

    if not isinstance(email, str) or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT ne contient pas d'identité valide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not isinstance(role, str) or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT ne contient pas de rôle valide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "email": email,
        "role": normalize_role(role),
    }


def require_roles(*allowed_roles: str):
    """
    Crée une dépendance FastAPI qui exige un ou plusieurs rôles.

    Exemples :
        Depends(require_roles("manager"))
        Depends(require_roles("it_admin", "security_admin"))
    """

    def role_checker(
        current_user: dict[str, str] = Depends(get_current_user),
    ) -> dict[str, str]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Votre rôle ne vous autorise pas à effectuer cette action."
                ),
            )

        return current_user

    return role_checker