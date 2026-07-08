from typing import Final

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.security import ALGORITHM, SECRET_KEY

# Rôles connus de l'application (doit rester aligné avec docs/v1_roles_permissions.md)
VALID_ROLES: Final[set[str]] = {
    "employee",
    "manager",
    "it_admin",
    "security_admin",
}

# auto_error=False pour pouvoir distinguer "pas de header" d'un header invalide,
# et renvoyer nous-mêmes un 401 avec un detail cohérent dans les deux cas.
bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """Représente l'utilisateur authentifié à partir du JWT décodé."""

    email: str
    role: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """
    Extrait et valide le Bearer token JWT.

    - Pas de token -> 401
    - Token mal formé / signature invalide / expiré -> 401
    - Token valide -> retourne l'utilisateur courant (email + rôle)
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Un token Bearer est requis pour accéder à cette ressource.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token a expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token est invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    role = payload.get("role")

    if email is None or role is None or role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token ne contient pas les informations attendues.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(email=email, role=role)


def require_role(*allowed_roles: str):
    """
    Fabrique une dépendance FastAPI qui vérifie que l'utilisateur courant
    possède l'un des rôles autorisés.

    Usage:
        @app.post("/access-requests/{id}/manager-decision")
        def manager_decision(
            ...,
            current_user: CurrentUser = Depends(require_role("manager")),
        ):
            ...
    """

    def _check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Votre rôle ne permet pas d'accéder à cette ressource.",
            )
        return current_user

    return _check_role
