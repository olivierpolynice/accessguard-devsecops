"""Fixtures partagées pour les tests AccessGuard V5."""

from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(APP_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(APP_DIRECTORY))


from app.database import clear_database  # noqa: E402
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


def build_auth_headers(email: str, role: str) -> dict[str, str]:
    """Construit un en-tête Authorization valide."""

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
    """Construit volontairement un JWT expiré."""

    payload: dict[str, Any] = {
        "sub": email,
        "role": role,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def reset_test_data() -> None:
    """Nettoie la base SQLite et les caches mémoire."""

    ACCESS_REQUESTS.clear()
    ACCESS_GRANTS.clear()
    AUDIT_LOGS.clear()
    clear_database()


@pytest.fixture(autouse=True)
def clean_database_between_tests() -> Generator[None, None, None]:
    """Garantit l’indépendance de chaque test."""

    reset_test_data()

    yield

    reset_test_data()


@pytest.fixture
def client() -> TestClient:
    """Retourne le client FastAPI de test."""

    return TestClient(app)


@pytest.fixture
def employee_headers() -> dict[str, str]:
    account = DEMO_ACCOUNTS["employee"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def manager_headers() -> dict[str, str]:
    account = DEMO_ACCOUNTS["manager"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def it_admin_headers() -> dict[str, str]:
    account = DEMO_ACCOUNTS["it_admin"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def security_admin_headers() -> dict[str, str]:
    account = DEMO_ACCOUNTS["security_admin"]

    return build_auth_headers(
        account["email"],
        account["role"],
    )


@pytest.fixture
def expired_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {build_expired_token()}",
    }


@pytest.fixture
def invalid_headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer token-invalide-v5",
    }
