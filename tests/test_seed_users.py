from app.database import (
    get_connection,
    initialize_database,
)
from app.seed import DEMO_USERS, seed_users


def count_demo_users() -> int:
    """
    Compte uniquement les quatre comptes de démonstration.
    """
    demo_emails = tuple(
        str(user["email"])
        for user in DEMO_USERS
    )

    placeholders = ", ".join(
        "?"
        for _ in demo_emails
    )

    with get_connection() as connection:
        row = connection.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM users
            WHERE email IN ({placeholders})
            """,
            demo_emails,
        ).fetchone()

    return int(row["total"])


def test_seed_creates_four_demo_users():
    """
    Le seed doit créer exactement quatre comptes de démonstration.
    """
    initialize_database()

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM users
            WHERE email IN (
                ?,
                ?,
                ?,
                ?
            )
            """,
            tuple(
                str(user["email"])
                for user in DEMO_USERS
            ),
        )
        connection.commit()

    seed_users()

    assert count_demo_users() == 4


def test_seed_users_is_idempotent():
    """
    Relancer le seed plusieurs fois ne doit créer aucun doublon.
    """
    initialize_database()

    seed_users()
    seed_users()
    seed_users()
    seed_users()
    seed_users()

    assert count_demo_users() == 4


def test_each_demo_email_is_unique():
    """
    Chaque compte de démonstration doit exister une seule fois.
    """
    initialize_database()

    seed_users()
    seed_users()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                email,
                COUNT(*) AS total
            FROM users
            WHERE email IN (
                ?,
                ?,
                ?,
                ?
            )
            GROUP BY email
            ORDER BY email
            """,
            tuple(
                str(user["email"])
                for user in DEMO_USERS
            ),
        ).fetchall()

    assert len(rows) == 4

    for row in rows:
        assert row["total"] == 1
