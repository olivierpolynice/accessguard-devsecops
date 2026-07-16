import pytest

from app.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_email_with_password,
    get_user_by_id,
    list_users,
    update_user_role,
    update_user_status,
)


TEST_EMAIL = "repository.user@asteriatech.local"
TEST_PASSWORD = "AccessGuard123!"


def test_create_user_in_sqlite():
    user = create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
        is_active=True,
    )

    assert user["email"] == TEST_EMAIL
    assert user["role"] == "employee"
    assert user["is_active"] is True
    assert "password" not in user
    assert "password_hash" not in user


def test_get_user_by_email():
    created_user = create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    user = get_user_by_email(TEST_EMAIL)

    assert user is not None
    assert user["id"] == created_user["id"]
    assert user["email"] == TEST_EMAIL


def test_get_user_by_id():
    created_user = create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    user = get_user_by_id(created_user["id"])

    assert user is not None
    assert user["email"] == TEST_EMAIL


def test_list_users():
    create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    users = list_users()

    assert any(
        user["email"] == TEST_EMAIL
        for user in users
    )


def test_update_user_role():
    user = create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    updated_user = update_user_role(
        user_id=user["id"],
        role="manager",
    )

    assert updated_user is not None
    assert updated_user["role"] == "manager"


def test_update_user_status():
    user = create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    updated_user = update_user_status(
        user_id=user["id"],
        is_active=False,
    )

    assert updated_user is not None
    assert updated_user["is_active"] is False


def test_password_hash_is_only_available_in_private_lookup():
    create_user(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        role="employee",
    )

    public_user = get_user_by_email(TEST_EMAIL)
    private_user = get_user_by_email_with_password(
        TEST_EMAIL
    )

    assert public_user is not None
    assert private_user is not None

    assert "password_hash" not in public_user
    assert private_user["password_hash"] != TEST_PASSWORD


def test_invalid_role_is_rejected():
    with pytest.raises(ValueError):
        create_user(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            role="root_admin",
        )
