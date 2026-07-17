from prometheus_client import REGISTRY

# Cet import garantit l’enregistrement des métriques métier.
import app.metrics  # noqa: F401


def get_counter_value(counter_name: str) -> float:
    """Retourne la valeur actuelle d’un compteur Prometheus."""
    value = REGISTRY.get_sample_value(counter_name)

    if value is None:
        return 0.0

    return float(value)


def login_user(
    client,
    email: str,
    password: str = "AccessGuard123!",
) -> str:
    """Connecte un utilisateur et retourne son token JWT."""
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    assert token

    return token


def authorization_headers(token: str) -> dict[str, str]:
    """Construit l’en-tête Authorization Bearer."""
    return {
        "Authorization": f"Bearer {token}",
    }


def test_business_metrics_are_registered() -> None:
    expected_metrics = [
        "accessguard_login_success_total",
        "accessguard_login_failure_total",
        "accessguard_access_requests_total",
        "accessguard_manager_approvals_total",
        "accessguard_manager_refusals_total",
        "accessguard_access_grants_total",
        "accessguard_access_revocations_total",
        "accessguard_forbidden_actions_total",
    ]

    for metric_name in expected_metrics:
        assert get_counter_value(metric_name) >= 0


def test_login_success_metric_increases(client) -> None:
    before = get_counter_value(
        "accessguard_login_success_total"
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "AccessGuard123!",
        },
    )

    after = get_counter_value(
        "accessguard_login_success_total"
    )

    assert response.status_code == 200
    assert after == before + 1


def test_login_failure_metric_increases(client) -> None:
    before = get_counter_value(
        "accessguard_login_failure_total"
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@asteriatech.local",
            "password": "wrong-password",
        },
    )

    after = get_counter_value(
        "accessguard_login_failure_total"
    )

    assert response.status_code == 401
    assert after == before + 1


def test_access_request_metric_increases(client) -> None:
    token = login_user(
        client,
        "alice.employee@asteriatech.local",
    )

    before = get_counter_value(
        "accessguard_access_requests_total"
    )

    response = client.post(
        "/access-requests",
        headers=authorization_headers(token),
        json={
            "resource_id": 1,
            "reason": (
                "Demande créée pour tester "
                "la métrique Prometheus."
            ),
            "start_date": "2026-07-17",
            "end_date": "2026-07-20",
        },
    )

    after = get_counter_value(
        "accessguard_access_requests_total"
    )

    assert response.status_code == 201
    assert after == before + 1


def test_forbidden_action_metric_increases(client) -> None:
    token = login_user(
        client,
        "alice.employee@asteriatech.local",
    )

    before = get_counter_value(
        "accessguard_forbidden_actions_total"
    )

    # Un employee n’est pas autorisé à consulter les audits.
    response = client.get(
        "/audit-logs",
        headers=authorization_headers(token),
    )

    after = get_counter_value(
        "accessguard_forbidden_actions_total"
    )

    assert response.status_code == 403
    assert after == before + 1
