from pathlib import Path
import sys

import jwt
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIRECTORY))

from auth import SECRET_KEY, ALGORITHM  # noqa: E402
from main import AUDIT_LOGS, app  # noqa: E402


client = TestClient(app)


def reset_data() -> None:
    """Réinitialise le journal d'audit entre les tests."""
    AUDIT_LOGS.clear()


def test_login_success_returns_jwt_with_correct_role() -> None:
    """Un login valide retourne 200, un token, et le bon rôle."""
    reset_data()

    response = client.post(
        "/auth/login",
        json={
            "email": "manager.asteriatech@asteriatech.local",
            "password": "Manager@2026",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "manager"
    assert body["email"] == "manager.asteriatech@asteriatech.local"
    assert body["token_type"] == "bearer"

    decoded = jwt.decode(
        body["access_token"], SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert decoded["sub"] == "manager.asteriatech@asteriatech.local"
    assert decoded["role"] == "manager"


def test_login_wrong_password_returns_401() -> None:
    """Un mauvais mot de passe doit retourner 401, sans révéler la cause."""
    reset_data()

    response = client.post(
        "/auth/login",
        json={
            "email": "manager.asteriatech@asteriatech.local",
            "password": "MauvaisMotDePasse",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401() -> None:
    """Un email inconnu doit retourner 401, comme un mauvais mot de passe."""
    reset_data()

    response = client.post(
        "/auth/login",
        json={
            "email": "inconnu@asteriatech.local",
            "password": "Peu importe",
        },
    )

    assert response.status_code == 401


def test_login_creates_audit_log_entry() -> None:
    """Une connexion réussie doit être tracée dans le journal d'audit."""
    reset_data()

    client.post(
        "/auth/login",
        json={
            "email": "it.admin@asteriatech.local",
            "password": "ItAdmin@2026",
        },
    )

    logs = client.get("/audit-logs").json()
    assert any(log["action"] == "LOGIN_SUCCESS" for log in logs)
