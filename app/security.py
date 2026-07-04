import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv(
    "ACCESSGUARD_SECRET_KEY",
    "accessguard-local-demo-secret-change-in-production",
)
ALGORITHM = os.getenv("ACCESSGUARD_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESSGUARD_TOKEN_EXPIRE_MINUTES", "60")
)


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