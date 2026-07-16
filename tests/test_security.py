import pytest

from app.security import hash_password, verify_password


def test_password_is_hashed():
    password = "AccessGuard123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert password_hash.startswith("$2")


def test_correct_password_is_valid():
    password = "AccessGuard123!"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_wrong_password_is_invalid():
    password_hash = hash_password("AccessGuard123!")

    assert verify_password(
        "MauvaisMotDePasse123!",
        password_hash,
    ) is False


def test_password_longer_than_72_bytes_is_rejected():
    long_password = "A" * 73

    with pytest.raises(ValueError):
        hash_password(long_password)