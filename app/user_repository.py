import sqlite3
from typing import Any

from app.database import get_connection
from app.security import hash_password


ALLOWED_ROLES = {
    "employee",
    "manager",
    "it_admin",
    "security_admin",
}


def _normalize_email(email: str) -> str:
    """
    Normalise une adresse e-mail avant son utilisation en base.
    """
    if not isinstance(email, str):
        raise TypeError(
            "L'adresse e-mail doit être une chaîne de caractères."
        )

    normalized_email = email.strip().lower()

    if not normalized_email:
        raise ValueError(
            "L'adresse e-mail ne peut pas être vide."
        )

    return normalized_email


def _validate_role(role: str) -> str:
    """
    Vérifie que le rôle fait partie des rôles AccessGuard.
    """
    if role not in ALLOWED_ROLES:
        raise ValueError(
            "Rôle invalide. Valeurs autorisées : "
            "employee, manager, it_admin, security_admin."
        )

    return role


def _row_to_public_user(
    row: sqlite3.Row,
) -> dict[str, Any]:
    """
    Convertit une ligne SQLite en utilisateur public.

    password_hash n'est jamais exposé.
    """
    return {
        "id": row["id"],
        "email": row["email"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_private_user(
    row: sqlite3.Row,
) -> dict[str, Any]:
    """
    Convertit une ligne SQLite en utilisateur interne.

    Cette représentation contient password_hash et doit uniquement
    être utilisée par l'authentification.
    """
    return {
        "id": row["id"],
        "email": row["email"],
        "password_hash": row["password_hash"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_user(
    email: str,
    password: str,
    role: str = "employee",
    is_active: bool = True,
) -> dict[str, Any]:
    """
    Crée un utilisateur dans SQLite.

    Le mot de passe est haché avant son insertion.
    """
    normalized_email = _normalize_email(email)
    validated_role = _validate_role(role)
    password_hash = hash_password(password)

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (
                    email,
                    password_hash,
                    role,
                    is_active
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    normalized_email,
                    password_hash,
                    validated_role,
                    int(is_active),
                ),
            )

            user_id = int(cursor.lastrowid)

            row = connection.execute(
                """
                SELECT
                    id,
                    email,
                    role,
                    is_active,
                    created_at,
                    updated_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

            connection.commit()

    except sqlite3.IntegrityError as error:
        error_message = str(error).lower()

        if (
            "unique" in error_message
            or "users.email" in error_message
        ):
            raise ValueError(
                "Un utilisateur possède déjà cette adresse email."
            ) from error

        raise ValueError(
            "Impossible de créer l'utilisateur."
        ) from error

    if row is None:
        raise RuntimeError(
            "Utilisateur créé mais impossible à relire."
        )

    return _row_to_public_user(row)


def get_user_by_email(
    email: str,
) -> dict[str, Any] | None:
    """
    Retourne un utilisateur public à partir de son e-mail.

    password_hash n'est pas retourné.
    """
    normalized_email = _normalize_email(email)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                email,
                role,
                is_active,
                created_at,
                updated_at
            FROM users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_public_user(row)


def get_user_by_email_with_password(
    email: str,
) -> dict[str, Any] | None:
    """
    Retourne un utilisateur avec password_hash.

    Cette fonction est réservée à /auth/login.
    """
    normalized_email = _normalize_email(email)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                email,
                password_hash,
                role,
                is_active,
                created_at,
                updated_at
            FROM users
            WHERE email = ?
            """,
            (normalized_email,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_private_user(row)


def get_user_by_id(
    user_id: int,
) -> dict[str, Any] | None:
    """
    Retourne un utilisateur public à partir de son identifiant.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                email,
                role,
                is_active,
                created_at,
                updated_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_public_user(row)


def list_users() -> list[dict[str, Any]]:
    """
    Retourne tous les utilisateurs sans exposer password_hash.
    """
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                email,
                role,
                is_active,
                created_at,
                updated_at
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        _row_to_public_user(row)
        for row in rows
    ]


def update_user_role(
    user_id: int,
    role: str,
) -> dict[str, Any] | None:
    """
    Modifie le rôle d'un utilisateur.
    """
    validated_role = _validate_role(role)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET
                role = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                validated_role,
                user_id,
            ),
        )

        connection.commit()

    if cursor.rowcount == 0:
        return None

    return get_user_by_id(user_id)


def update_user_status(
    user_id: int,
    is_active: bool,
) -> dict[str, Any] | None:
    """
    Active ou désactive un utilisateur.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                int(is_active),
                user_id,
            ),
        )

        connection.commit()

    if cursor.rowcount == 0:
        return None

    return get_user_by_id(user_id)


def update_user(
    user_id: int,
    email: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> dict[str, Any] | None:
    """
    Modifie plusieurs propriétés d'un utilisateur.
    """
    current_user = get_user_by_id(user_id)

    if current_user is None:
        return None

    new_email = (
        _normalize_email(email)
        if email is not None
        else current_user["email"]
    )

    new_role = (
        _validate_role(role)
        if role is not None
        else current_user["role"]
    )

    new_status = (
        bool(is_active)
        if is_active is not None
        else current_user["is_active"]
    )

    try:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE users
                SET
                    email = ?,
                    role = ?,
                    is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    new_email,
                    new_role,
                    int(new_status),
                    user_id,
                ),
            )

            connection.commit()

    except sqlite3.IntegrityError as error:
        raise ValueError(
            "Un utilisateur possède déjà cette adresse email."
        ) from error

    return get_user_by_id(user_id)


def update_user_password(
    user_id: int,
    new_password: str,
) -> bool:
    """
    Modifie le mot de passe d'un utilisateur.

    Le nouveau mot de passe est haché avant stockage.
    """
    password_hash = hash_password(new_password)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET
                password_hash = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                password_hash,
                user_id,
            ),
        )

        connection.commit()

    return cursor.rowcount > 0


def delete_user(
    user_id: int,
) -> bool:
    """
    Supprime définitivement un utilisateur.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (user_id,),
        )

        connection.commit()

    return cursor.rowcount > 0
