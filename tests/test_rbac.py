"""
Tests dédiés au contrôle d'accès basé sur les rôles (RBAC).

Couvre, pour chacune des routes protégées :
- absence de token -> 401
- token invalide / malformé -> 401
- token expiré -> 401
- token valide mais rôle non autorisé -> 403
- token valide avec le bon rôle -> succès (non-régression)
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import jwt
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIRECTORY))

from main import ACCESS_GRANTS, ACCESS_REQUESTS, AUDIT_LOGS, app  # noqa: E402
from security import ALGORITHM, SECRET_KEY  # noqa: E402


client = TestClient(app)


def reset_data() -> None:
    """Réinitialise les données locales entre les tests."""
    ACCESS_REQUESTS.clear()
    ACCESS_GRANTS.clear()
    AUDIT_LOGS.clear()


def get_token(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def headers_for(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


EMPLOYEE_TOKEN = get_token("alice.employee@asteriatech.local", "Employee123!")
MANAGER_TOKEN = get_token("marc.manager@asteriatech.local", "Manager123!")
IT_ADMIN_TOKEN = get_token("ines.itadmin@asteriatech.local", "Admin123!")
SECURITY_ADMIN_TOKEN = get_token("sam.security@asteriatech.local", "Security123!")

EMPLOYEE_HEADERS = headers_for(EMPLOYEE_TOKEN)
MANAGER_HEADERS = headers_for(MANAGER_TOKEN)
IT_ADMIN_HEADERS = headers_for(IT_ADMIN_TOKEN)
SECURITY_ADMIN_HEADERS = headers_for(SECURITY_ADMIN_TOKEN)

INVALID_TOKEN_HEADERS = {"Authorization": "Bearer ceci-nest-pas-un-jwt-valide"}


def expired_token_headers(role: str = "employee", email: str = "expired.user@asteriatech.local") -> dict:
    """Construit un JWT valide en signature mais expiré depuis 5 minutes."""
    expired_payload = {
        "sub": email,
        "role": role,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    return headers_for(token)


def create_valid_request() -> int:
    """Crée une demande valide (avec un token employee) et retourne son identifiant."""
    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
        headers=EMPLOYEE_HEADERS,
    )
    assert response.status_code == 201
    return response.json()["id"]


def approve_request(request_id: int) -> None:
    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
        headers=MANAGER_HEADERS,
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /access-requests -> rôle "employee"
# ---------------------------------------------------------------------------

def test_create_access_request_no_token_401() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Un token Bearer est requis pour accéder à cette ressource."


def test_create_access_request_invalid_token_401() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
        headers=INVALID_TOKEN_HEADERS,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Le token est invalide."


def test_create_access_request_expired_token_401() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
        headers=expired_token_headers(role="employee"),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Le token a expiré."


def test_create_access_request_wrong_role_403() -> None:
    """Un manager n'a pas le droit de créer une demande d'accès (réservé à employee)."""
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
        headers=MANAGER_HEADERS,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Votre rôle ne permet pas d'accéder à cette ressource."


def test_create_access_request_correct_role_201() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Accès VPN requis pour réaliser des tests automatisés.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 201


# ---------------------------------------------------------------------------
# POST /access-requests/{id}/manager-decision -> rôle "manager"
# ---------------------------------------------------------------------------

def test_manager_decision_no_token_401() -> None:
    reset_data()
    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
    )

    assert response.status_code == 401


def test_manager_decision_invalid_token_401() -> None:
    reset_data()
    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
        headers=INVALID_TOKEN_HEADERS,
    )

    assert response.status_code == 401


def test_manager_decision_wrong_role_403() -> None:
    """Un employee ne peut pas valider une demande (réservé à manager)."""
    reset_data()
    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 403


def test_manager_decision_correct_role_200() -> None:
    reset_data()
    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
        headers=MANAGER_HEADERS,
    )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /access-requests/{id}/grant -> rôle "it_admin"
# ---------------------------------------------------------------------------

def test_grant_access_no_token_401() -> None:
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
    )

    assert response.status_code == 401


def test_grant_access_wrong_role_403() -> None:
    """Un manager ne peut pas attribuer un accès (réservé à it_admin)."""
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
        headers=MANAGER_HEADERS,
    )

    assert response.status_code == 403


def test_grant_access_correct_role_201() -> None:
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
        headers=IT_ADMIN_HEADERS,
    )

    assert response.status_code == 201


# ---------------------------------------------------------------------------
# POST /access-grants/{id}/revoke -> rôle "it_admin"
# ---------------------------------------------------------------------------

def test_revoke_access_no_token_401() -> None:
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
        headers=IT_ADMIN_HEADERS,
    )
    grant_id = grant_response.json()["id"]

    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "reason": "Fin de la période de test.",
        },
    )

    assert response.status_code == 401


def test_revoke_access_wrong_role_403() -> None:
    """Un employee ne peut pas révoquer un accès (réservé à it_admin)."""
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
        headers=IT_ADMIN_HEADERS,
    )
    grant_id = grant_response.json()["id"]

    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "reason": "Fin de la période de test.",
        },
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 403


def test_revoke_access_correct_role_200() -> None:
    reset_data()
    request_id = create_valid_request()
    approve_request(request_id)

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
        headers=IT_ADMIN_HEADERS,
    )
    grant_id = grant_response.json()["id"]

    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "reason": "Fin de la période de test.",
        },
        headers=IT_ADMIN_HEADERS,
    )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /audit-logs -> rôle "security_admin"
# ---------------------------------------------------------------------------

def test_audit_logs_no_token_401() -> None:
    response = client.get("/audit-logs")

    assert response.status_code == 401


def test_audit_logs_invalid_token_401() -> None:
    response = client.get("/audit-logs", headers=INVALID_TOKEN_HEADERS)

    assert response.status_code == 401


def test_audit_logs_wrong_role_403() -> None:
    """Un it_admin ne peut pas consulter le journal d'audit (réservé à security_admin)."""
    response = client.get("/audit-logs", headers=IT_ADMIN_HEADERS)

    assert response.status_code == 403


def test_audit_logs_correct_role_200() -> None:
    response = client.get("/audit-logs", headers=SECURITY_ADMIN_HEADERS)

    assert response.status_code == 200
