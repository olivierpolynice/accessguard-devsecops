from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app  # noqa: E402
from app.database import clear_database  # noqa: E402
from app.security import create_access_token  # noqa: E402


client = TestClient(app)


def reset_data() -> None:
    clear_database()


def auth_headers(email: str, role: str) -> dict[str, str]:
    token = create_access_token(subject=email, role=role)
    return {"Authorization": f"Bearer {token}"}


EMPLOYEE_HEADERS = auth_headers("employee@asteriatech.local", "employee")
MANAGER_HEADERS = auth_headers("manager@asteriatech.local", "manager")
IT_ADMIN_HEADERS = auth_headers("it.admin@asteriatech.local", "it_admin")
SECURITY_ADMIN_HEADERS = auth_headers("security.admin@asteriatech.local", "security_admin")


def create_valid_request(headers: dict[str, str] = EMPLOYEE_HEADERS) -> int:
    response = client.post(
        "/access-requests",
        headers=headers,
        json={
            "resource_id": 1,
            "reason": "Test de la route V4 pour vérification.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def approve_request(request_id: int) -> None:
    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=MANAGER_HEADERS,
        json={"decision": "APPROVED", "comment": "OK pour test V4."},
    )
    assert response.status_code == 200


def grant_access(request_id: int) -> int:
    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=IT_ADMIN_HEADERS,
        json={"comment": "Attribution test V4."},
    )
    assert response.status_code == 201
    return response.json()["id"]


# --- /me -------------------------------------------------------------


def test_get_me_with_valid_token() -> None:
    """Vérifie que /me retourne l'email et le rôle du token JWT."""
    reset_data()

    response = client.get("/me", headers=EMPLOYEE_HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        "email": "employee@asteriatech.local",
        "role": "employee",
    }


def test_get_me_without_token_401() -> None:
    """Vérifie que /me exige un token JWT."""
    reset_data()

    response = client.get("/me")

    assert response.status_code == 401


# --- /dashboard/summary ------------------------------------------------


def test_dashboard_summary_employee() -> None:
    """
    Vérifie qu'un employee ne voit que ses propres compteurs
    (pending_requests, active_grants, revoked_grants), mais le total
    d'audit logs reste global.
    """
    reset_data()

    request_id = create_valid_request(EMPLOYEE_HEADERS)

    other_employee_headers = auth_headers("bob.employee@asteriatech.local", "employee")
    create_valid_request(other_employee_headers)

    response = client.get("/dashboard/summary", headers=EMPLOYEE_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["pending_requests"] == 1
    assert body["active_grants"] == 0
    assert body["revoked_grants"] == 0
    assert body["audit_logs"] == 2

    assert request_id > 0


def test_dashboard_summary_it_admin() -> None:
    """
    Vérifie qu'un it_admin voit des compteurs globaux (toutes les
    demandes/accès, pas seulement les siens).
    """
    reset_data()

    request_id = create_valid_request(EMPLOYEE_HEADERS)
    approve_request(request_id)
    grant_access(request_id)

    other_employee_headers = auth_headers("bob.employee@asteriatech.local", "employee")
    create_valid_request(other_employee_headers)

    response = client.get("/dashboard/summary", headers=IT_ADMIN_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["pending_requests"] == 1
    assert body["active_grants"] == 1
    assert body["revoked_grants"] == 0
    # 4 logs : ACCESS_REQUEST_CREATED (x2), MANAGER_DECISION, ACCESS_GRANTED
    assert body["audit_logs"] == 4


def test_dashboard_summary_requires_jwt() -> None:
    """Vérifie que /dashboard/summary exige un token JWT."""
    reset_data()

    response = client.get("/dashboard/summary")

    assert response.status_code == 401


# --- /access-requests/status/{status} -----------------------------------


def test_list_access_requests_by_status_employee_scoped() -> None:
    """Vérifie qu'un employee ne voit que ses propres demandes filtrées."""
    reset_data()

    create_valid_request(EMPLOYEE_HEADERS)

    other_employee_headers = auth_headers("bob.employee@asteriatech.local", "employee")
    create_valid_request(other_employee_headers)

    response = client.get(
        "/access-requests/status/PENDING_MANAGER",
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["requester_email"] == "employee@asteriatech.local"


def test_list_access_requests_by_status_invalid_status_422() -> None:
    """Vérifie qu'un statut inconnu retourne 422 plutôt qu'une liste vide."""
    reset_data()

    response = client.get(
        "/access-requests/status/NOT_A_REAL_STATUS",
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 422


def test_list_access_requests_by_status_requires_jwt() -> None:
    """Vérifie que la route exige un token JWT."""
    reset_data()

    response = client.get("/access-requests/status/PENDING_MANAGER")

    assert response.status_code == 401


# --- /access-grants/active ------------------------------------------------


def test_list_active_access_grants_it_admin() -> None:
    """Vérifie qu'un it_admin voit tous les accès actifs, pas les révoqués."""
    reset_data()

    request_id = create_valid_request(EMPLOYEE_HEADERS)
    approve_request(request_id)
    grant_id = grant_access(request_id)

    second_request_id = create_valid_request(EMPLOYEE_HEADERS)
    approve_request(second_request_id)
    second_grant_id = grant_access(second_request_id)

    revoke_response = client.post(
        f"/access-grants/{second_grant_id}/revoke",
        headers=IT_ADMIN_HEADERS,
        json={"reason": "Fin de test V4."},
    )
    assert revoke_response.status_code == 200

    response = client.get("/access-grants/active", headers=IT_ADMIN_HEADERS)

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == grant_id
    assert results[0]["status"] == "ACTIVE"


def test_list_active_access_grants_manager_forbidden() -> None:
    """Vérifie qu'un manager reçoit 403, comme sur /access-grants."""
    reset_data()

    response = client.get("/access-grants/active", headers=MANAGER_HEADERS)

    assert response.status_code == 403


def test_list_active_access_grants_requires_jwt() -> None:
    """Vérifie que la route exige un token JWT."""
    reset_data()

    response = client.get("/access-grants/active")

    assert response.status_code == 401
