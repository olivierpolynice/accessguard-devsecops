"""Tests de sécurité, d’authentification et de RBAC pour AccessGuard V5."""

from datetime import date

import pytest
from fastapi.testclient import TestClient


VALID_REQUEST_PAYLOAD = {
    "resource_id": 1,
    "reason": "Validation des contrôles de sécurité AccessGuard V5.",
    "start_date": str(date(2026, 8, 1)),
    "end_date": str(date(2026, 8, 31)),
}


SENSITIVE_GET_ROUTES = [
    "/me",
    "/dashboard/summary",
    "/access-requests",
    "/access-grants",
    "/access-grants/active",
    "/audit-logs",
]


@pytest.mark.auth
def test_login_success(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "AccessGuard123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["role"] == "employee"
    assert body["email"] == "alice.employee@asteriatech.local"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


@pytest.mark.auth
def test_login_with_wrong_password(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "MauvaisMotDePasse123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Adresse e-mail ou mot de passe incorrect."
    )


@pytest.mark.auth
def test_login_with_unknown_user(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "inconnu@asteriatech.local",
            "password": "AccessGuard123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Adresse e-mail ou mot de passe incorrect."
    )


@pytest.mark.auth
@pytest.mark.security
def test_expired_token_is_rejected(
    client: TestClient,
    expired_headers: dict[str, str],
) -> None:
    response = client.get(
        "/me",
        headers=expired_headers,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Le token JWT a expiré."


@pytest.mark.auth
@pytest.mark.security
def test_invalid_token_is_rejected(
    client: TestClient,
    invalid_headers: dict[str, str],
) -> None:
    response = client.get(
        "/me",
        headers=invalid_headers,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Le token JWT est invalide."


@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.parametrize("route", SENSITIVE_GET_ROUTES)
def test_sensitive_get_routes_require_jwt(
    client: TestClient,
    route: str,
) -> None:
    response = client.get(route)

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.security
@pytest.mark.rbac
def test_create_access_request_requires_jwt(
    client: TestClient,
) -> None:
    response = client.post(
        "/access-requests",
        json=VALID_REQUEST_PAYLOAD,
    )

    assert response.status_code == 401


@pytest.mark.security
@pytest.mark.rbac
def test_manager_decision_requires_jwt(
    client: TestClient,
) -> None:
    response = client.post(
        "/access-requests/999/manager-decision",
        json={
            "decision": "APPROVED",
            "comment": "Tentative sans JWT.",
        },
    )

    assert response.status_code == 401


@pytest.mark.security
@pytest.mark.rbac
def test_grant_requires_jwt(
    client: TestClient,
) -> None:
    response = client.post(
        "/access-requests/999/grant",
        json={
            "comment": "Tentative sans JWT.",
        },
    )

    assert response.status_code == 401


@pytest.mark.security
@pytest.mark.rbac
def test_revoke_requires_jwt(
    client: TestClient,
) -> None:
    response = client.post(
        "/access-grants/999/revoke",
        json={
            "reason": "Tentative sans JWT.",
        },
    )

    assert response.status_code == 401


@pytest.mark.rbac
def test_employee_cannot_make_manager_decision(
    client: TestClient,
    employee_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/access-requests",
        headers=employee_headers,
        json=VALID_REQUEST_PAYLOAD,
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    decision_response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=employee_headers,
        json={
            "decision": "APPROVED",
            "comment": "Tentative non autorisée.",
        },
    )

    assert decision_response.status_code == 403


@pytest.mark.rbac
def test_manager_cannot_grant_access(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/access-requests",
        headers=employee_headers,
        json=VALID_REQUEST_PAYLOAD,
    )

    assert create_response.status_code == 201

    request_id = create_response.json()["id"]

    approval_response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=manager_headers,
        json={
            "decision": "APPROVED",
            "comment": "Demande validée.",
        },
    )

    assert approval_response.status_code == 200

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=manager_headers,
        json={
            "comment": "Tentative de grant par le manager.",
        },
    )

    assert grant_response.status_code == 403


@pytest.mark.rbac
def test_manager_cannot_list_access_grants(
    client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = client.get(
        "/access-grants",
        headers=manager_headers,
    )

    assert response.status_code == 403


@pytest.mark.rbac
def test_employee_cannot_read_audit_logs(
    client: TestClient,
    employee_headers: dict[str, str],
) -> None:
    response = client.get(
        "/audit-logs",
        headers=employee_headers,
    )

    assert response.status_code == 403


@pytest.mark.rbac
def test_manager_cannot_read_audit_logs(
    client: TestClient,
    manager_headers: dict[str, str],
) -> None:
    response = client.get(
        "/audit-logs",
        headers=manager_headers,
    )

    assert response.status_code == 403


@pytest.mark.rbac
def test_it_admin_can_read_audit_logs(
    client: TestClient,
    it_admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/audit-logs",
        headers=it_admin_headers,
    )

    assert response.status_code == 200


@pytest.mark.rbac
def test_security_admin_can_read_audit_logs(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/audit-logs",
        headers=security_admin_headers,
    )

    assert response.status_code == 200


@pytest.mark.monitoring
def test_metrics_endpoint_is_available(
    client: TestClient,
) -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests" in response.text.lower()
