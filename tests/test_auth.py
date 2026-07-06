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


def test_login_with_malformed_email_returns_422() -> None:
    """Un email sans arobase ne respecte pas le pattern attendu."""
    response = client.post(
        "/auth/login",
        json={
            "email": "email-invalide-sans-arobase",
            "password": "Employee123!",
        },
    )
    assert response.status_code == 422


def test_login_with_short_password_returns_422() -> None:
    """Un mot de passe de moins de 8 caractères doit être rejeté par Pydantic."""
    response = client.post(
        "/auth/login",
        json={
            "email": "alice.employee@asteriatech.local",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_login_missing_password_field_returns_422() -> None:
    """Une requête sans le champ password doit être rejetée."""
    response = client.post(
        "/auth/login",
        json={"email": "alice.employee@asteriatech.local"},
    )
    assert response.status_code == 422


def test_login_missing_email_field_returns_422() -> None:
    """Une requête sans le champ email doit être rejetée."""
    response = client.post(
        "/auth/login",
        json={"password": "Employee123!"},
    )
    assert response.status_code == 422
