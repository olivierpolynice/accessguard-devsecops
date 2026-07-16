"""Tests V5 du login basé sur SQLite."""

from fastapi.testclient import TestClient

from app.user_repository import (
    get_user_by_email,
    update_user_status,
)


DEMO_EMAIL = "alice.employee@asteriatech.local"
DEMO_PASSWORD = "AccessGuard123!"


def test_active_user_can_login(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["email"] == DEMO_EMAIL
    assert body["role"] == "employee"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_wrong_password_is_rejected(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": DEMO_EMAIL,
            "password": "MauvaisMotDePasse123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Adresse e-mail ou mot de passe incorrect."
    )


def test_unknown_user_is_rejected(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown.user@asteriatech.local",
            "password": DEMO_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Adresse e-mail ou mot de passe incorrect."
    )


def test_inactive_user_is_rejected(
    client: TestClient,
) -> None:
    user = get_user_by_email(DEMO_EMAIL)

    assert user is not None

    updated_user = update_user_status(
        user_id=user["id"],
        is_active=False,
    )

    assert updated_user is not None
    assert updated_user["is_active"] is False

    response = client.post(
        "/auth/login",
        json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Ce compte utilisateur est désactivé."
    )
