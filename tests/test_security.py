from app.security import create_access_token, hash_password, verify_password


def test_password_hash_and_verify() -> None:
    password = "Employee123!"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("WrongPassword123!", password_hash) is False


def test_create_access_token() -> None:
    token = create_access_token(
        subject="alice.employee@asteriatech.local",
        role="employee",
    )

    assert isinstance(token, str)
    assert len(token.split(".")) == 3
