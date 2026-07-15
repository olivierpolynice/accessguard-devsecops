"""Tests du workflow métier complet AccessGuard V5."""

from datetime import date

import pytest
from fastapi.testclient import TestClient


REQUEST_PAYLOAD = {
    "resource_id": 1,
    "reason": (
        "Accès requis pour valider le workflow complet de la version V5."
    ),
    "start_date": str(date(2026, 9, 1)),
    "end_date": str(date(2026, 9, 30)),
}


def create_access_request(
    client: TestClient,
    employee_headers: dict[str, str],
) -> dict:
    response = client.post(
        "/access-requests",
        headers=employee_headers,
        json=REQUEST_PAYLOAD,
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert body["status"] == "PENDING_MANAGER"
    assert body["resource_id"] == 1
    assert body["resource_name"] == "VPN Entreprise"

    return body


def approve_access_request(
    client: TestClient,
    manager_headers: dict[str, str],
    request_id: int,
) -> dict:
    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=manager_headers,
        json={
            "decision": "APPROVED",
            "comment": "Besoin métier validé dans le cadre de la V5.",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["status"] == "APPROVED"

    return body


def grant_access(
    client: TestClient,
    it_admin_headers: dict[str, str],
    request_id: int,
) -> dict:
    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=it_admin_headers,
        json={
            "comment": "Accès attribué après approbation du manager.",
        },
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert body["request_id"] == request_id
    assert body["status"] == "ACTIVE"

    return body


def revoke_access(
    client: TestClient,
    security_admin_headers: dict[str, str],
    grant_id: int,
) -> dict:
    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        headers=security_admin_headers,
        json={
            "reason": "Fin du besoin temporaire V5.",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["status"] == "REVOKED"

    return body


@pytest.mark.workflow
def test_complete_request_approval_grant_revoke_audit_workflow(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
    it_admin_headers: dict[str, str],
    security_admin_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    request_id = created_request["id"]

    approved_request = approve_access_request(
        client,
        manager_headers,
        request_id,
    )

    assert approved_request["id"] == request_id

    created_grant = grant_access(
        client,
        it_admin_headers,
        request_id,
    )

    grant_id = created_grant["id"]

    revoked_grant = revoke_access(
        client,
        security_admin_headers,
        grant_id,
    )

    assert revoked_grant["id"] == grant_id

    request_detail_response = client.get(
        f"/access-requests/{request_id}",
        headers=employee_headers,
    )

    assert request_detail_response.status_code == 200
    assert request_detail_response.json()["status"] == "GRANTED"

    grants_response = client.get(
        "/access-grants",
        headers=security_admin_headers,
    )

    assert grants_response.status_code == 200

    matching_grants = [
        grant
        for grant in grants_response.json()
        if grant["id"] == grant_id
    ]

    assert len(matching_grants) == 1
    assert matching_grants[0]["status"] == "REVOKED"

    audit_response = client.get(
        "/audit-logs",
        headers=security_admin_headers,
    )

    assert audit_response.status_code == 200

    actions = [
        log["action"]
        for log in audit_response.json()
    ]

    assert "ACCESS_REQUEST_CREATED" in actions
    assert "MANAGER_DECISION" in actions
    assert "ACCESS_GRANTED" in actions
    assert "ACCESS_REVOKED" in actions


@pytest.mark.workflow
def test_request_cannot_be_granted_before_approval(
    client: TestClient,
    employee_headers: dict[str, str],
    it_admin_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    response = client.post(
        f"/access-requests/{created_request['id']}/grant",
        headers=it_admin_headers,
        json={
            "comment": "Tentative avant approbation.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "L'accès ne peut être attribué que pour une demande approuvée."
    )


@pytest.mark.workflow
def test_request_cannot_be_processed_twice_by_manager(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    request_id = created_request["id"]

    first_response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=manager_headers,
        json={
            "decision": "APPROVED",
            "comment": "Première décision.",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=manager_headers,
        json={
            "decision": "REFUSED",
            "comment": "Seconde décision interdite.",
        },
    )

    assert second_response.status_code == 409


@pytest.mark.workflow
def test_active_grant_cannot_be_created_twice(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
    it_admin_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    request_id = created_request["id"]

    approve_access_request(
        client,
        manager_headers,
        request_id,
    )

    grant_access(
        client,
        it_admin_headers,
        request_id,
    )

    duplicate_response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=it_admin_headers,
        json={
            "comment": "Tentative d’attribution en doublon.",
        },
    )

    assert duplicate_response.status_code == 409


@pytest.mark.workflow
def test_revoked_grant_cannot_be_revoked_twice(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
    it_admin_headers: dict[str, str],
    security_admin_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    request_id = created_request["id"]

    approve_access_request(
        client,
        manager_headers,
        request_id,
    )

    grant = grant_access(
        client,
        it_admin_headers,
        request_id,
    )

    revoke_access(
        client,
        security_admin_headers,
        grant["id"],
    )

    second_revoke_response = client.post(
        f"/access-grants/{grant['id']}/revoke",
        headers=security_admin_headers,
        json={
            "reason": "Tentative de seconde révocation.",
        },
    )

    assert second_revoke_response.status_code == 409


@pytest.mark.audit
def test_workflow_audit_contains_actor_and_outcome(
    client: TestClient,
    employee_headers: dict[str, str],
    manager_headers: dict[str, str],
    security_admin_headers: dict[str, str],
) -> None:
    created_request = create_access_request(
        client,
        employee_headers,
    )

    approve_access_request(
        client,
        manager_headers,
        created_request["id"],
    )

    audit_response = client.get(
        "/audit-logs",
        headers=security_admin_headers,
    )

    assert audit_response.status_code == 200

    logs = audit_response.json()

    assert len(logs) >= 2

    creation_log = next(
        log
        for log in logs
        if log["action"] == "ACCESS_REQUEST_CREATED"
    )

    manager_log = next(
        log
        for log in logs
        if log["action"] == "MANAGER_DECISION"
    )

    assert creation_log["actor_email"] == (
        "alice.employee@asteriatech.local"
    )
    assert creation_log["outcome"] == "PENDING_MANAGER"

    assert manager_log["actor_email"] == (
        "marc.manager@asteriatech.local"
    )
    assert manager_log["outcome"].startswith("APPROVED:")
