from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIRECTORY = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIRECTORY))

from main import ACCESS_GRANTS, ACCESS_REQUESTS, AUDIT_LOGS, app  # noqa: E402
from app.database import clear_database  # noqa: E402
from app.security import create_access_token  # noqa: E402


client = TestClient(app)


def reset_data() -> None:
    """Réinitialise les données mémoire et SQLite entre les tests."""
    ACCESS_REQUESTS.clear()
    ACCESS_GRANTS.clear()
    AUDIT_LOGS.clear()
    clear_database()


def auth_headers(email: str, role: str) -> dict[str, str]:
    """Crée un en-tête Authorization Bearer pour les tests."""
    token = create_access_token(subject=email, role=role)

    return {
        "Authorization": f"Bearer {token}",
    }


EMPLOYEE_HEADERS = auth_headers(
    "employee@asteriatech.local",
    "employee",
)

MANAGER_HEADERS = auth_headers(
    "manager@asteriatech.local",
    "manager",
)

IT_ADMIN_HEADERS = auth_headers(
    "it.admin@asteriatech.local",
    "it_admin",
)

SECURITY_ADMIN_HEADERS = auth_headers(
    "security.admin@asteriatech.local",
    "security_admin",
)


def create_valid_request() -> int:
    """Crée une demande valide au nom d'un employé."""
    response = client.post(
        "/access-requests",
        headers=EMPLOYEE_HEADERS,
        json={
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
        headers=MANAGER_HEADERS,
        json={
            "decision": "APPROVED",
            "comment": "Validation du besoin métier pour les tests.",
        },
    )

    assert response.status_code == 200


def grant_access(request_id: int) -> int:
    """Attribue un accès au nom d'un IT admin."""
    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=IT_ADMIN_HEADERS,
        json={
            "comment": "Accès attribué après approbation du manager.",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_health_check() -> None:
    """Vérifie que l'API est disponible."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "AccessGuard"
    assert response.json()["version"] == "0.2.0"
    assert "checked_at" in response.json()


def test_list_resources() -> None:
    """Vérifie que les ressources sont accessibles."""
    response = client.get("/resources")

    assert response.status_code == 200
    resources = response.json()

    assert len(resources) == 5
    assert resources[0]["name"] == "VPN Entreprise"
    assert resources[3]["sensitivity"] == "CRITICAL"


def test_access_request_requires_jwt() -> None:
    """Vérifie qu'une demande d'accès sans JWT est refusée."""
    reset_data()

    response = client.post(
        "/access-requests",
        json={
            "resource_id": 1,
            "reason": "Tentative de création sans authentification JWT.",
            "start_date": "2026-07-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Un token JWT Bearer est requis."


def test_create_access_request() -> None:
    """Vérifie la création d'une demande avec un JWT employee."""
    reset_data()

    request_id = create_valid_request()

    assert request_id == 1
    assert ACCESS_REQUESTS[0].requester_email == "employee@asteriatech.local"
    assert ACCESS_REQUESTS[0].status == "PENDING_MANAGER"
    assert len(AUDIT_LOGS) == 1
    assert AUDIT_LOGS[0].action == "ACCESS_REQUEST_CREATED"
    assert AUDIT_LOGS[0].actor_email == "employee@asteriatech.local"


def test_list_access_requests_requires_jwt() -> None:
    """Vérifie que la liste des demandes exige un JWT."""
    reset_data()

    response = client.get("/access-requests")

    assert response.status_code == 401


def test_employee_only_sees_own_access_requests() -> None:
    """Vérifie qu'un employee ne voit que ses propres demandes."""
    reset_data()

    request_id = create_valid_request()

    response = client.get(
        "/access-requests",
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == request_id
    assert response.json()[0]["requester_email"] == "employee@asteriatech.local"


def test_get_access_request_detail_requires_jwt() -> None:
    """Vérifie que le détail d'une demande exige un JWT."""
    reset_data()

    request_id = create_valid_request()
    response = client.get(f"/access-requests/{request_id}")

    assert response.status_code == 401


def test_get_access_request_detail_with_employee_token() -> None:
    """Vérifie qu'un employee peut consulter sa propre demande."""
    reset_data()

    request_id = create_valid_request()

    response = client.get(
        f"/access-requests/{request_id}",
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["id"] == request_id
    assert response.json()["resource_name"] == "VPN Entreprise"
    assert response.json()["status"] == "PENDING_MANAGER"


def test_reject_invalid_dates() -> None:
    """Vérifie que des dates incohérentes sont refusées."""
    reset_data()

    response = client.post(
        "/access-requests",
        headers=EMPLOYEE_HEADERS,
        json={
            "resource_id": 1,
            "reason": "Test de validation des dates incohérentes.",
            "start_date": "2026-07-31",
            "end_date": "2026-07-01",
        },
    )

    assert response.status_code == 422


def test_resource_not_found_404_with_valid_jwt() -> None:
    """Vérifie le 404 pour une ressource inconnue après authentification."""
    reset_data()

    response = client.post(
        "/access-requests",
        headers=EMPLOYEE_HEADERS,
        json={
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


def test_manager_decision_requires_jwt_before_404() -> None:
    """
    Vérifie que l'API retourne 401 sans JWT avant de révéler
    qu'une demande existe ou non.
    """
    reset_data()

    response = client.post(
        "/access-requests/999/manager-decision",
        json={
            "decision": "APPROVED",
            "comment": "Tentative non authentifiée.",
        },
    )

    assert response.status_code == 401


def test_employee_cannot_make_manager_decision() -> None:
    """Vérifie qu'un employee reçoit 403 sur une décision manager."""
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=EMPLOYEE_HEADERS,
        json={
            "decision": "APPROVED",
            "comment": "Tentative par un employé standard.",
        },
    )

    assert response.status_code == 403


def test_manager_can_refuse_request() -> None:
    """Vérifie qu'un manager peut refuser une demande."""
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=MANAGER_HEADERS,
        json={
            "decision": "REFUSED",
            "comment": "Accès non justifié pour le périmètre demandé.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REFUSED"
    assert AUDIT_LOGS[-1].action == "MANAGER_DECISION"
    assert AUDIT_LOGS[-1].actor_email == "manager@asteriatech.local"
    assert AUDIT_LOGS[-1].outcome.startswith("REFUSED:")


def test_request_not_found_404_with_manager_jwt() -> None:
    """Vérifie le 404 d'une demande inconnue après authentification manager."""
    reset_data()

    response = client.post(
        "/access-requests/999/manager-decision",
        headers=MANAGER_HEADERS,
        json={
            "decision": "APPROVED",
            "comment": "Test d'une demande inexistante.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "La demande d'accès est introuvable."


def test_grant_requires_jwt_before_404() -> None:
    """
    Vérifie que la route grant retourne 401 sans JWT avant
    d'indiquer si une demande existe.
    """
    reset_data()

    response = client.post(
        "/access-requests/999/grant",
        json={
            "comment": "Tentative non authentifiée.",
        },
    )

    assert response.status_code == 401


def test_employee_cannot_grant_access() -> None:
    """Vérifie qu'un employee reçoit 403 sur l'attribution d'accès."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=EMPLOYEE_HEADERS,
        json={
            "comment": "Tentative d'attribution non autorisée.",
        },
    )

    assert response.status_code == 403


def test_grant_before_approval_409() -> None:
    """Vérifie qu'un IT admin ne peut pas attribuer avant approbation."""
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=IT_ADMIN_HEADERS,
        json={
            "comment": "Tentative d'attribution avant approbation.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "L'accès ne peut être attribué que pour une demande approuvée."
    )


def test_duplicate_active_grant_409() -> None:
    """Vérifie qu'un accès actif ne peut pas être attribué deux fois."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)

    grant_id = grant_access(request_id)

    assert grant_id == 1
    assert ACCESS_GRANTS[0].status == "ACTIVE"

    response = client.post(
        f"/access-requests/{request_id}/grant",
        headers=IT_ADMIN_HEADERS,
        json={
            "comment": "Tentative de seconde attribution.",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Un accès actif existe déjà pour cette demande."
    )


def test_revoke_requires_jwt_before_404() -> None:
    """
    Vérifie que la route revoke retourne 401 sans JWT avant
    d'indiquer si l'accès existe.
    """
    reset_data()

    response = client.post(
        "/access-grants/999/revoke",
        json={
            "reason": "Tentative non authentifiée.",
        },
    )

    assert response.status_code == 401


def test_employee_cannot_revoke_access() -> None:
    """Vérifie qu'un employee reçoit 403 lors d'une révocation."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)
    grant_id = grant_access(request_id)

    response = client.post(
        f"/access-grants/{grant_id}/revoke",
        headers=EMPLOYEE_HEADERS,
        json={
            "reason": "Tentative de révocation non autorisée.",
        },
    )

    assert response.status_code == 403


def test_complete_access_workflow() -> None:
    """Vérifie le workflow complet : demande, approbation, grant, revoke."""
    reset_data()

    request_id = create_valid_request()
    approve_request(request_id)
    grant_id = grant_access(request_id)

    revoke_response = client.post(
        f"/access-grants/{grant_id}/revoke",
        headers=IT_ADMIN_HEADERS,
        json={
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


def test_audit_logs_require_jwt() -> None:
    """Vérifie que les audits ne sont plus accessibles publiquement."""
    reset_data()

    response = client.get("/audit-logs")

    assert response.status_code == 401


def test_employee_cannot_read_audit_logs() -> None:
    """Vérifie qu'un employee reçoit 403 sur les logs d'audit."""
    reset_data()

    response = client.get(
        "/audit-logs",
        headers=EMPLOYEE_HEADERS,
    )

    assert response.status_code == 403


def test_it_admin_can_read_audit_logs() -> None:
    """Vérifie qu'un IT admin peut consulter les audits."""
    reset_data()

    create_valid_request()

    response = client.get(
        "/audit-logs",
        headers=IT_ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["action"] == "ACCESS_REQUEST_CREATED"


def test_security_admin_can_read_audit_logs() -> None:
    """Vérifie qu'un security admin peut consulter les audits."""
    reset_data()

    create_valid_request()

    response = client.get(
        "/audit-logs",
        headers=SECURITY_ADMIN_HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_invalid_manager_status_422() -> None:
    """Vérifie que le manager ne peut pas envoyer un statut invalide."""
    reset_data()

    request_id = create_valid_request()

    response = client.post(
        f"/access-requests/{request_id}/manager-decision",
        headers=MANAGER_HEADERS,
        json={
            "decision": "INVALID",
            "comment": "Test d'un statut manager non autorisé.",
        },
    )

    assert response.status_code == 422