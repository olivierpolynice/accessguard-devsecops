"""Fixtures partagées pour les tests AccessGuard V5."""

from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient


# ============================================================
# Configuration des chemins Python
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(APP_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(APP_DIRECTORY))


# Les imports de l'application doivent rester après
# la configuration de sys.path.
from app.database import (  # noqa: E402
    clear_database,
    initialize_database,
)
from app.seed import seed_users  # noqa: E402
from app.main import (  # noqa: E402
    ACCESS_GRANTS,
    ACCESS_REQUESTS,
    AUDIT_LOGS,
    app,
)
from app.security import (  # noqa: E402
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


# ============================================================
# Comptes de démonstration
# ============================================================

DEMO_PASSWORD = "AccessGuard123!"

DEMO_ACCOUNTS: dict[str, dict[str, str]] = {
    "employee": {
        "email": "alice.employee@asteriatech.local",
        "role": "employee",
        "password": DEMO_PASSWORD,
    },
    "manager": {
        "email": "marc.manager@asteriatech.local",
        "role": "manager",
        "password": DEMO_PASSWORD,
    },
    "it_admin": {
        "email": "ines.itadmin@asteriatech.local",
        "role": "it_admin",
        "password": DEMO_PASSWORD,
    },
    "security_admin": {
        "email": "paul.security@asteriatech.local",
        "role": "security_admin",
        "password": DEMO_PASSWORD,
    },
}


# ============================================================
# Fonctions utilitaires JWT
# ============================================================

def build_auth_headers(
    email: str,
    role: str,
) -> dict[str, str]:
    """
    Construit un en-tête Authorization contenant un JWT valide.
    """
    token = create_access_token(
        subject=email,
        role=role,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def build_expired_token(
    email: str = "expired.user@asteriatech.local",
    role: str = "employee",
) -> str:
    """
    Construit volontairement un JWT expiré.
    """
    payload: dict[str, Any] = {
        "sub": email,
        "role": role,
        "exp": (
            datetime.now(timezone.utc)
            - timedelta(minutes=5)
        ),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# Nettoyage des données de test
# ============================================================

def reset_test_data() -> None:
    """
    Réinitialise SQLite et les caches mémoire utilisés
    par les anciennes versions des tests.
    """
    initialize_database()

    ACCESS_REQUESTS.clear()
    ACCESS_GRANTS.clear()
    AUDIT_LOGS.clear()

    clear_database()
    seed_users()


@pytest.fixture(autouse=True)
def clean_database_between_tests() -> Generator[None, None, None]:
    """
    Garantit l'indépendance de chaque test.

    Avant chaque test :
    - initialise les tables ;
    - supprime les données créées par les tests ;
    - restaure les quatre comptes de démonstration ;
    - vide les caches mémoire.

    Après chaque test, la même opération est répétée.
    """
    reset_test_data()

    yield

    reset_test_data()


# ============================================================
# Client FastAPI
# ============================================================

@pytest.fixture
def client() -> TestClient:
    """
    Retourne le client FastAPI utilisé par les tests.
    """
    return TestClient(app)


# ============================================================
# En-têtes JWT par rôle
# ============================================================

@pytest.fixture
def employee_headers() -> dict[str, str]:
    """
    Retourne un JWT valide pour le rôle employee.
    """
    account = DEMO_ACCOUNTS["employee"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def manager_headers() -> dict[str, str]:
    """
    Retourne un JWT valide pour le rôle manager.
    """
    account = DEMO_ACCOUNTS["manager"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def it_admin_headers() -> dict[str, str]:
    """
    Retourne un JWT valide pour le rôle it_admin.
    """
    account = DEMO_ACCOUNTS["it_admin"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def security_admin_headers() -> dict[str, str]:
    """
    Retourne un JWT valide pour le rôle security_admin.
    """
    account = DEMO_ACCOUNTS["security_admin"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


# ============================================================
# Jetons invalides
# ============================================================

@pytest.fixture
def expired_headers() -> dict[str, str]:
    """
    Retourne un en-tête contenant un JWT expiré.
    """
    return {
        "Authorization": (
            f"Bearer {build_expired_token()}"
        ),
    }


@pytest.fixture
def invalid_headers() -> dict[str, str]:
    """
    Retourne un en-tête contenant un JWT invalide.
    """
    return {
        "Authorization": "Bearer token-invalide-v5",
    }
