from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIRECTORY))

from main import ACCESS_GRANTS, ACCESS_REQUESTS, AUDIT_LOGS, app  # noqa: E402


client = TestClient(app)


def reset_data() -> None:
    """Réinitialise les données locales entre les tests."""
    ACCESS_REQUESTS.clear()
    ACCESS_GRANTS.clear()
    AUDIT_LOGS.clear()


def create_valid_request() -> int:
    """Crée une demande valide et retourne son identifiant."""
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

    assert response.status_code == 201
    return response.json()["id"]


def approve_request(request_id: int) -> None:
    """Approuve une demande au nom d'un manager."""
    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
    )

    assert response.status_code == 200


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "AccessGuard"
    assert response.json()["version"] == "0.1.0"
    assert "checked_at" in response.json()


def test_list_resources() -> None:
    response = client.get("/resources")

    assert response.status_code == 200
    resources = response.json()

    assert len(resources) == 5
    assert resources[0]["name"] == "VPN Entreprise"
    assert resources[3]["sensitivity"] == "CRITICAL"


def test_create_access_request() -> None:
    reset_data()

    request_id = create_valid_request()

    assert request_id == 1
    assert ACCESS_REQUESTS[0].status == "PENDING_MANAGER"
    assert len(AUDIT_LOGS) == 1
    assert AUDIT_LOGS[0].action == "ACCESS_REQUEST_CREATED"


def test_list_access_requests() -> None:
    reset_data()

    request_id = create_valid_request()
    response = client.get("/access-requests")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == request_id
    assert response.json()[0]["status"] == "PENDING_MANAGER"


def test_get_access_request_detail() -> None:
    reset_data()

    request_id = create_valid_request()
    response = client.get(f"/access-requests/{request_id}")

    assert response.status_code == 200
    assert response.json()["id"] == request_id
    assert response.json()["resource_name"] == "VPN Entreprise"
    assert response.json()["status"] == "PENDING_MANAGER"


def test_reject_invalid_dates() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Test de validation des dates incohérentes.",
            "start_date": "2026-07-31",
            "end_date": "2026-07-01",
        },
    )

    assert response.status_code == 422


def test_complete_access_workflow() -> None:
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Accès attribué après approbation du manager.",
        },
    )

    assert grant_response.status_code == 201
    assert grant_response.json()["status"] == "ACTIVE"

    grant_id = grant_response.json()["id"]

    revoke_response = client.post(
        f"/access-grants/{grant_id}/revoke",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "reason": "Fin de la période de test.",
        },
    )

    assert revoke_response.status_code == 200
    assert revoke_response.json()["status"] == "REVOKED"

    audit_actions = [audit.action for audit in AUDIT_LOGS]

    assert "ACCESS_REQUEST_CREATED" in audit_actions
    assert "MANAGER_DECISION" in audit_actions
    assert "ACCESS_GRANTED" in audit_actions
    assert "ACCESS_REVOKED" in audit_actions


def test_request_not_found_404() -> None:
    reset_data()

    response = client.post(
        "/access-requests/999/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "Test d'une demande inexistante.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La demande d'accès est introuvable."


def test_grant_before_approval_409() -> None:
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Tentative d'attribution avant approbation.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "L'accès ne peut être attribué que pour une demande approuvée."
    )


def test_manager_refusal() -> None:
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "REFUSED",
            "comment": "Accès non justifié pour le périmètre demandé.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REFUSED"
    assert AUDIT_LOGS[-1].action == "MANAGER_DECISION"
    assert AUDIT_LOGS[-1].outcome.startswith("REFUSED:")


def test_resource_not_found_404() -> None:
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 999,
            "reason": "Test de contrôle d'une ressource inexistante.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "La ressource demandée est introuvable ou inactive."
    )


def test_duplicate_active_grant_409() -> None:
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    first_grant = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Première attribution pour vérifier le doublon.",
        },
    )

    assert first_grant.status_code == 201
    assert first_grant.json()["status"] == "ACTIVE"

    second_grant = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Tentative de seconde attribution.",
        },
    )

    assert second_grant.status_code == 409
    assert second_grant.json()["detail"] == (
        "Un accès actif existe déjà pour cette demande."
    )
def test_invalid_manager_status_422() -> None:
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "INVALID",
            "comment": "Test d'un statut manager non autorisé.",
        },
    )

    assert response.status_code == 422

def test_create_access_request_reason_too_short_422() -> None:
    """Un motif de moins de 10 caractères doit être rejeté."""
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 1,
            "reason": "Court",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 422


def test_create_access_request_invalid_resource_id_422() -> None:
    """Un resource_id négatif ou nul doit être rejeté."""
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "requester_email": "test.user@asteriatech.local",
            "resource_id": 0,
            "reason": "Test de validation d'un identifiant de ressource invalide.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 422


def test_manager_decision_comment_too_short_422() -> None:
    """Un commentaire de moins de 5 caractères doit être rejeté."""
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        json={
            "manager_email": "manager@asteriatech.local",
            "decision": "APPROVED",
            "comment": "OK",
        },
    )

    assert response.status_code == 422


def test_grant_comment_too_short_422() -> None:
    """Un commentaire trop court lors de l'attribution doit être rejeté."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "OK",
        },
    )

    assert response.status_code == 422


def test_revoke_reason_too_short_422() -> None:
    """Un motif de révocation trop court doit être rejeté."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    grant_response = client.post(
        f"/access-requests/{request_id}/grant",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "comment": "Attribution valide pour tester la révocation.",
        },
    )
    grant_id = grant_response.json()["id"]

    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        json={
            "it_admin_email": "it.admin@asteriatech.local",
            "reason": "NA",
        },
    )

    assert response.status_code == 422
