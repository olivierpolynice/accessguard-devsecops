import os
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.metrics import forbidden_actions_total


# ============================================================
# Configuration JWT
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    os.getenv(
        "JWT_SECRET_KEY",
        "accessguard-development-secret-key-change-me",
    ),
)

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30",
    )
)


# ============================================================
# Configuration des mots de passe
# ============================================================

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# auto_error=False permet de personnaliser
# le message quand aucun token n'est fourni.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


# ============================================================
# Rôles AccessGuard autorisés
# ============================================================

ALLOWED_ROLES = {
    "employee",
    "manager",
    "it_admin",
    "security_admin",
}


# ============================================================
# Gestion des mots de passe
# ============================================================

def hash_password(password: str) -> str:
    """
    Hache un mot de passe avant son stockage dans SQLite.

    bcrypt accepte au maximum 72 octets.
    """
    if not isinstance(password, str):
        raise TypeError(
            "Le mot de passe doit être une chaîne de caractères."
        )

    if not password:
        raise ValueError(
            "Le mot de passe ne peut pas être vide."
        )

    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Le mot de passe ne doit pas dépasser 72 octets."
        )

    return password_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond
    au hash enregistré dans SQLite.
    """
    if not isinstance(plain_password, str):
        return False

    if not isinstance(password_hash, str):
        return False

    if not plain_password or not password_hash:
        return False

    if len(plain_password.encode("utf-8")) > 72:
        return False

    try:
        return password_context.verify(
            plain_password,
            password_hash,
        )
    except (ValueError, TypeError):
        return False


# ============================================================
# Création des JWT
# ============================================================

def create_access_token(
    subject: str | None = None,
    role: str | None = None,
    expires_minutes: int | None = None,
    *,
    data: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
    **extra_claims: Any,
) -> str:
    """
    Crée un JWT AccessGuard.

    Compatible avec les anciennes et nouvelles syntaxes.
    """
    payload: dict[str, Any] = {}

    if data is not None:
        if not isinstance(data, dict):
            raise TypeError(
                "Le paramètre data doit être un dictionnaire."
            )

        payload.update(data)

    if subject is not None:
        payload["sub"] = subject

    if role is not None:
        payload["role"] = role

    payload.update(extra_claims)

    token_role = payload.get("role")

    if token_role is not None and token_role not in ALLOWED_ROLES:
        raise ValueError(
            f"Rôle invalide : {token_role}"
        )

    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expiration = now + expires_delta

    elif expires_minutes is not None:
        expiration = now + timedelta(
            minutes=expires_minutes
        )

    else:
        expiration = now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload["iat"] = now
    payload["exp"] = expiration

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# Décodage des JWT
# ============================================================

def decode_access_token(
    token: str,
) -> dict[str, Any] | None:
    """
    Décode et vérifie un JWT.

    Retourne None si le token est invalide ou expiré.
    """
    if not token:
        return None

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError:
        return None


def decode_token(
    token: str,
) -> dict[str, Any] | None:
    """
    Alias conservé pour les anciens fichiers du projet.
    """
    return decode_access_token(token)


# ============================================================
# Utilisateur actuellement connecté
# ============================================================

def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """
    Vérifie le JWT et retourne l'utilisateur connecté.

    Distingue :
    - l'absence de token ;
    - un token expiré ;
    - un token invalide ;
    - un compte désactivé.
    """

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Un token JWT Bearer est requis.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except ExpiredSignatureError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT a expiré.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    except JWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT est invalide.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    subject = payload.get("sub")
    role = payload.get("role")

    if not subject or role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token JWT est invalide.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    is_active = payload.get(
        "is_active",
        True,
    )

    if not is_active:
        forbidden_actions_total.inc()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est désactivé.",
        )

    return {
        "id": payload.get("user_id"),
        "user_id": payload.get("user_id"),
        "email": subject,
        "sub": subject,
        "role": role,
        "is_active": bool(is_active),
    }


# ============================================================
# Vérification RBAC
# ============================================================

def require_roles(
    *roles: str | list[str] | tuple[str, ...] | set[str],
) -> Callable[..., dict[str, Any]]:
    """
    Crée une dépendance FastAPI autorisant uniquement
    certains rôles.

    Exemples :

        Depends(require_roles("manager"))

        Depends(
            require_roles(
                "manager",
                "security_admin",
            )
        )

        Depends(
            require_roles(
                ["manager", "security_admin"]
            )
        )
    """
    allowed_roles: set[str] = set()

    for role_item in roles:
        if isinstance(
            role_item,
            (list, tuple, set),
        ):
            allowed_roles.update(role_item)
        else:
            allowed_roles.add(role_item)

    invalid_roles = allowed_roles - ALLOWED_ROLES

    if invalid_roles:
        invalid_roles_text = ", ".join(
            sorted(invalid_roles)
        )

        raise ValueError(
            "Rôle(s) non autorisé(s) dans require_roles : "
            f"{invalid_roles_text}"
        )

    def role_checker(
        current_user: dict[str, Any] = Depends(
            get_current_user
        ),
    ) -> dict[str, Any]:
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            forbidden_actions_total.inc()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Vous n'avez pas les permissions "
                    "nécessaires pour cette action."
                ),
            )

        return current_user

    return role_checker