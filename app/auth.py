"""Module d'authentification et de gestion des JSON Web Tokens (JWT).

Ce module pose le socle V1 d'AccessGuard : utilisateurs de démonstration
avec mots de passe hashés, vérification des identifiants et émission d'un
jeton JWT contenant l'email et le rôle de l'utilisateur.

La brique RBAC (protection des routes existantes avec 401/403) n'est PAS
appliquée ici volontairement : ce fichier ne fait que poser les fondations
(login + jeton). La fonction `get_current_user` est fournie prête à
l'emploi pour que la protection des routes puisse être ajoutée dans une
tâche V1 suivante sans toucher à nouveau à ce module.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# --------------------------------------------------------------------------
# Configuration du JWT
# --------------------------------------------------------------------------
# Le secret est lu depuis une variable d'environnement afin de ne jamais
# être versionné en clair dans le dépôt (bonne pratique DevSecOps).
# Une valeur par défaut est fournie uniquement pour l'environnement local
# de développement.
SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY", "dev-secret-change-me-in-env-please-32chars-min"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# URL du "tokenUrl" utilisée par Swagger pour le bouton Authorize.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# --------------------------------------------------------------------------
# Utilisateurs de démonstration (V1 : en mémoire, pas encore de base
# de données persistante -- cohérent avec le reste du P0/V1).
# --------------------------------------------------------------------------
def _hash(password: str) -> str:
    return pwd_context.hash(password)


DEMO_USERS: list[dict] = [
    {
        "email": "employee.demo@asteriatech.local",
        "full_name": "Employé Démo",
        "role": "employee",
        "password_hash": _hash("Employee@2026"),
    },
    {
        "email": "manager.asteriatech@asteriatech.local",
        "full_name": "Manager Démo",
        "role": "manager",
        "password_hash": _hash("Manager@2026"),
    },
    {
        "email": "it.admin@asteriatech.local",
        "full_name": "IT Admin Démo",
        "role": "it_admin",
        "password_hash": _hash("ItAdmin@2026"),
    },
    {
        "email": "security.admin@asteriatech.local",
        "full_name": "Security Admin Démo",
        "role": "security_admin",
        "password_hash": _hash("SecurityAdmin@2026"),
    },
]


def get_user_by_email(email: str) -> dict | None:
    """Retourne l'utilisateur de démonstration correspondant à l'email."""
    return next((user for user in DEMO_USERS if user["email"] == email), None)


def authenticate_user(email: str, password: str) -> dict | None:
    """Vérifie l'email et le mot de passe. Retourne l'utilisateur si valide."""
    user = get_user_by_email(email)
    if user is None:
        return None
    if not pwd_context.verify(password, user["password_hash"]):
        return None
    return user


# --------------------------------------------------------------------------
# Génération et lecture du JWT
# --------------------------------------------------------------------------
def create_access_token(email: str, role: str) -> str:
    """Génère un JWT signé contenant l'email et le rôle de l'utilisateur."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": email,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Décode et valide un JWT. Lève une HTTPException 401 si invalide."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le jeton a expiré, veuillez vous reconnecter.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le jeton fourni est invalide.",
        )
    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dépendance FastAPI prête à l'emploi pour protéger une route.

    Non appliquée aux routes existantes dans cette tâche : réservée à la
    prochaine étape V1 (RBAC / réponses 401-403 sur les routes métier).
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
        )

    payload = decode_access_token(token)
    email = payload.get("sub")
    user = get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur associé au jeton introuvable.",
        )

    return user
