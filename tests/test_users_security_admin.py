"""Tests V5 des routes utilisateurs réservées au security_admin."""

from typing import Any

from fastapi.testclient import TestClient


NEW_USER: dict[str, Any] = {
    "email": "crud.user@asteriatech.local",
    "password": "AccessGuard123!",
    "role": "employee",
    "is_active": True,
}


def create_test_user(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> dict[str, Any]:
    response = client.post(
        "/users",
        headers=security_admin_headers,
        json=NEW_USER,
    )

    assert response.status_code == 201, response.text

    return response.json()


def test_security_admin_can_list_users(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users",
        headers=security_admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_users_without_token_returns_401(
    client: TestClient,
) -> None:
    response = client.get("/users")

    assert response.status_code == 401
    assert "detail" in response.json()


def test_employee_cannot_list_users(
    client: TestClient,
    employee_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users",
        headers=employee_headers,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


def test_it_admin_cannot_list_users(
    client: TestClient,
    it_admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users",
        headers=it_admin_headers,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


def test_security_admin_can_create_user(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/users",
        headers=security_admin_headers,
        json=NEW_USER,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == NEW_USER["email"]
    assert body["role"] == "employee"
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body


def test_duplicate_user_returns_409(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    first_response = client.post(
        "/users",
        headers=security_admin_headers,
        json=NEW_USER,
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/users",
        headers=security_admin_headers,
        json=NEW_USER,
    )

    assert duplicate_response.status_code == 409
    assert "detail" in duplicate_response.json()


def test_security_admin_can_get_user_by_id(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    user = create_test_user(
        client,
        security_admin_headers,
    )

    response = client.get(
        f"/users/{user['id']}",
        headers=security_admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


def test_unknown_user_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.get(
        "/users/999999",
        headers=security_admin_headers,
    )

    assert response.status_code == 404
    assert "detail" in response.json()


def test_security_admin_can_update_role(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    user = create_test_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        f"/users/{user['id']}/role",
        headers=security_admin_headers,
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "manager"


def test_invalid_role_returns_422(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    user = create_test_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        f"/users/{user['id']}/role",
        headers=security_admin_headers,
        json={
            "role": "super_root_admin",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_unknown_user_role_update_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/999999/role",
        headers=security_admin_headers,
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 404
    assert "detail" in response.json()


def test_security_admin_can_update_status(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    user = create_test_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        f"/users/{user['id']}/status",
        headers=security_admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_unknown_user_status_update_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    response = client.patch(
        "/users/999999/status",
        headers=security_admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 404
    assert "detail" in response.json()