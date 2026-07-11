from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_success_returns_jwt() -> None:
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


def test_login_with_wrong_password_returns_401() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Adresse e-mail ou mot de passe incorrect."
    )


def test_login_with_unknown_email_returns_401() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown.user@asteriatech.local",
            "password": "AccessGuard123!",
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Adresse e-mail ou mot de passe incorrect."
    )