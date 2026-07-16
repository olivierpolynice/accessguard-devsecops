"""Tests V5 relatifs à la gestion des utilisateurs."""

from typing import Any

import pytest
from fastapi.testclient import TestClient


USER_ROUTES = {
    "collection": "/users",
    "detail": "/users/{user_id}",
    "role": "/users/{user_id}/role",
    "status": "/users/{user_id}/status",
}


NEW_USER_PAYLOAD: dict[str, Any] = {
    "email": "irina.v5@asteriatech.local",
    "password": "AccessGuardV5!2026",
    "role": "employee",
    "is_active": True,
}


def route_exists(
    client: TestClient,
    method: str,
    path: str,
) -> bool:
    """
    Vérifie si une route est déclarée dans FastAPI.

    Pour les routes contenant un paramètre, le schéma OpenAPI
    est utilisé afin de distinguer une route absente d'un simple 404.
    """
    openapi_response = client.get("/openapi.json")

    assert openapi_response.status_code == 200

    openapi_paths = openapi_response.json().get(
        "paths",
        {},
    )

    normalized_path = path

    for route_path in openapi_paths:
        route_without_parameters = route_path

        for part in route_path.split("/"):
            if part.startswith("{") and part.endswith("}"):
                route_without_parameters = (
                    route_without_parameters.replace(
                        part,
                        "1",
                    )
                )

        if route_without_parameters == normalized_path:
            return (
                method.lower()
                in openapi_paths[route_path]
            )

    return False


def require_users_api(
    client: TestClient,
    method: str,
    path: str,
) -> None:
    """
    Ignore le test si les routes utilisateurs ne sont pas présentes.
    """
    if not route_exists(
        client,
        method,
        path,
    ):
        pytest.skip(
            "Les routes CRUD utilisateurs V5 "
            "ne sont pas encore implémentées."
        )


def create_user(
    client: TestClient,
    security_admin_headers: dict[str, str],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Crée un utilisateur avec le compte security_admin.
    """
    actual_payload = (
        payload
        if payload is not None
        else NEW_USER_PAYLOAD
    )

    response = client.post(
        USER_ROUTES["collection"],
        headers=security_admin_headers,
        json=actual_payload,
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert "id" in body
    assert body["email"] == actual_payload["email"]
    assert body["role"] == actual_payload["role"]
    assert "password" not in body
    assert "password_hash" not in body

    return body


@pytest.mark.users
def test_users_route_requires_authentication(
    client: TestClient,
) -> None:
    require_users_api(
        client,
        "get",
        USER_ROUTES["collection"],
    )

    response = client.get(
        USER_ROUTES["collection"]
    )

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_employee_cannot_list_users(
    client: TestClient,
    employee_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "get",
        USER_ROUTES["collection"],
    )

    response = client.get(
        USER_ROUTES["collection"],
        headers=employee_headers,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_it_admin_cannot_list_users(
    client: TestClient,
    it_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "get",
        USER_ROUTES["collection"],
    )

    response = client.get(
        USER_ROUTES["collection"],
        headers=it_admin_headers,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.users
def test_security_admin_can_list_users(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "get",
        USER_ROUTES["collection"],
    )

    response = client.get(
        USER_ROUTES["collection"],
        headers=security_admin_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.users
def test_security_admin_can_create_user(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    assert user["email"] == NEW_USER_PAYLOAD["email"]
    assert user["role"] == "employee"
    assert user["is_active"] is True
    assert "password" not in user
    assert "password_hash" not in user


@pytest.mark.users
def test_duplicate_user_is_rejected(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )

    create_user(
        client,
        security_admin_headers,
    )

    duplicate_response = client.post(
        USER_ROUTES["collection"],
        headers=security_admin_headers,
        json=NEW_USER_PAYLOAD,
    )

    assert duplicate_response.status_code == 409
    assert "detail" in duplicate_response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_employee_cannot_create_user(
    client: TestClient,
    employee_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )

    response = client.post(
        USER_ROUTES["collection"],
        headers=employee_headers,
        json=NEW_USER_PAYLOAD,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_it_admin_cannot_create_user(
    client: TestClient,
    it_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )

    response = client.post(
        USER_ROUTES["collection"],
        headers=it_admin_headers,
        json=NEW_USER_PAYLOAD,
    )

    assert response.status_code == 403
    assert "detail" in response.json()


@pytest.mark.users
def test_security_admin_can_get_user_by_id(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "get",
        "/users/1",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    response = client.get(
        USER_ROUTES["detail"].format(
            user_id=user["id"]
        ),
        headers=security_admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]


@pytest.mark.users
def test_unknown_user_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "get",
        "/users/1",
    )

    response = client.get(
        USER_ROUTES["detail"].format(
            user_id=999999
        ),
        headers=security_admin_headers,
    )

    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_security_admin_can_update_user_role(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )
    require_users_api(
        client,
        "patch",
        "/users/1/role",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        USER_ROUTES["role"].format(
            user_id=user["id"]
        ),
        headers=security_admin_headers,
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "manager"


@pytest.mark.users
def test_invalid_role_is_rejected(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )
    require_users_api(
        client,
        "patch",
        "/users/1/role",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        USER_ROUTES["role"].format(
            user_id=user["id"]
        ),
        headers=security_admin_headers,
        json={
            "role": "super_root_admin",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.users
def test_unknown_user_role_update_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "patch",
        "/users/1/role",
    )

    response = client.patch(
        USER_ROUTES["role"].format(
            user_id=999999
        ),
        headers=security_admin_headers,
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.rbac
def test_employee_cannot_update_user_role(
    client: TestClient,
    security_admin_headers: dict[str, str],
    employee_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )
    require_users_api(
        client,
        "patch",
        "/users/1/role",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        USER_ROUTES["role"].format(
            user_id=user["id"]
        ),
        headers=employee_headers,
        json={
            "role": "manager",
        },
    )

    assert response.status_code == 403


@pytest.mark.users
def test_security_admin_can_deactivate_user(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )
    require_users_api(
        client,
        "patch",
        "/users/1/status",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    response = client.patch(
        USER_ROUTES["status"].format(
            user_id=user["id"]
        ),
        headers=security_admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.users
def test_unknown_user_status_update_returns_404(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "patch",
        "/users/1/status",
    )

    response = client.patch(
        USER_ROUTES["status"].format(
            user_id=999999
        ),
        headers=security_admin_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.users
@pytest.mark.auth
def test_deactivated_user_cannot_login(
    client: TestClient,
    security_admin_headers: dict[str, str],
) -> None:
    require_users_api(
        client,
        "post",
        USER_ROUTES["collection"],
    )
    require_users_api(
        client,
        "patch",
        "/users/1/status",
    )

    user = create_user(
        client,
        security_admin_headers,
    )

    deactivate_response = client.patch(
        USER_ROUTES["status"].format(
            user_id=user["id"]
        ),
        headers=security_admin_headers,
        json={
            "is_active": False,
        },
    )

    assert deactivate_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": NEW_USER_PAYLOAD["email"],
            "password": NEW_USER_PAYLOAD["password"],
        },
    )

    assert login_response.status_code == 403
    assert "detail" in login_response.json()