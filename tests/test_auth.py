from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_login_success_returns_jwt() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "Employee123!",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["token_type"] == "bearer"
    assert payload["role"] == "employee"
    assert isinstance(payload["access_token"], str)
    assert len(payload["access_token"].split(".")) == 3


def test_login_with_wrong_password_returns_401() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Identifiants incorrects."


def test_login_with_unknown_email_returns_401() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown.user@asteriatech.local",
            "password": "Employee123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Identifiants incorrects."