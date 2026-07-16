import os
import sqlite3
from pathlib import Path

from app.schemas import AccessGrant, AccessRequest, AuditLog


# ============================================================
# Configuration SQLite
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = Path(
    os.getenv(
        "ACCESSGUARD_DATABASE_PATH",
        str(PROJECT_ROOT / "accessguard.db"),
    )
)


def get_connection() -> sqlite3.Connection:
    """
    Ouvre une connexion SQLite.

    Les colonnes peuvent être lues par leur nom :
    row["email"], row["role"], etc.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# Alias conservé pour une éventuelle ancienne utilisation.
def get_db_connection() -> sqlite3.Connection:
    return get_connection()


# ============================================================
# Initialisation de la base
# ============================================================

def initialize_database() -> None:
    """
    Crée toutes les tables AccessGuard.
    """
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,

                role TEXT NOT NULL CHECK (
                    role IN (
                        'employee',
                        'manager',
                        'it_admin',
                        'security_admin'
                    )
                ),

                is_active INTEGER NOT NULL DEFAULT 1 CHECK (
                    is_active IN (0, 1)
                ),

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email);


            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_email TEXT NOT NULL,
                resource_id INTEGER NOT NULL,
                resource_name TEXT NOT NULL,
                reason TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );


            CREATE TABLE IF NOT EXISTS access_grants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                requester_email TEXT NOT NULL,
                resource_id INTEGER NOT NULL,
                resource_name TEXT NOT NULL,
                status TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,

                FOREIGN KEY (request_id)
                    REFERENCES access_requests(id)
            );


            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_email TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                outcome TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        connection.commit()


# Alias conservé pour les anciennes commandes.
def init_database() -> None:
    initialize_database()


# ============================================================
# Conversion des lignes SQLite
# ============================================================

def _to_access_request(
    row: sqlite3.Row,
) -> AccessRequest:
    return AccessRequest(
        id=row["id"],
        requester_email=row["requester_email"],
        resource_id=row["resource_id"],
        resource_name=row["resource_name"],
        reason=row["reason"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        status=row["status"],
        created_at=row["created_at"],
    )


def _to_access_grant(
    row: sqlite3.Row,
) -> AccessGrant:
    return AccessGrant(
        id=row["id"],
        request_id=row["request_id"],
        requester_email=row["requester_email"],
        resource_id=row["resource_id"],
        resource_name=row["resource_name"],
        status=row["status"],
        granted_at=row["granted_at"],
        expires_at=row["expires_at"],
        revoked_at=row["revoked_at"],
    )


def _to_audit_log(
    row: sqlite3.Row,
) -> AuditLog:
    return AuditLog(
        id=row["id"],
        actor_email=row["actor_email"],
        action=row["action"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"],
        outcome=row["outcome"],
        created_at=row["created_at"],
    )


# ============================================================
# Demandes d'accès
# ============================================================

def save_access_request(
    access_request: AccessRequest,
) -> AccessRequest:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO access_requests (
                requester_email,
                resource_id,
                resource_name,
                reason,
                start_date,
                end_date,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                access_request.requester_email,
                access_request.resource_id,
                access_request.resource_name,
                access_request.reason,
                access_request.start_date.isoformat(),
                access_request.end_date.isoformat(),
                access_request.status,
                access_request.created_at.isoformat(),
            ),
        )

        request_id = int(cursor.lastrowid)
        connection.commit()

    return access_request.model_copy(
        update={
            "id": request_id,
        }
    )


def get_access_request_from_database(
    request_id: int,
) -> AccessRequest | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM access_requests
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()

    if row is None:
        return None

    return _to_access_request(row)


def get_access_requests_from_database(
    requester_email: str | None = None,
) -> list[AccessRequest]:
    query = "SELECT * FROM access_requests"
    parameters: tuple[str, ...] = ()

    if requester_email is not None:
        query += " WHERE requester_email = ?"
        parameters = (requester_email,)

    query += " ORDER BY id ASC"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        _to_access_request(row)
        for row in rows
    ]


def update_access_request_status(
    request_id: int,
    new_status: str,
) -> AccessRequest | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE access_requests
            SET status = ?
            WHERE id = ?
            """,
            (
                new_status,
                request_id,
            ),
        )

        connection.commit()

    if cursor.rowcount == 0:
        return None

    return get_access_request_from_database(
        request_id
    )


# ============================================================
# Accès attribués
# ============================================================

def save_access_grant(
    access_grant: AccessGrant,
) -> AccessGrant:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO access_grants (
                request_id,
                requester_email,
                resource_id,
                resource_name,
                status,
                granted_at,
                expires_at,
                revoked_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                access_grant.request_id,
                access_grant.requester_email,
                access_grant.resource_id,
                access_grant.resource_name,
                access_grant.status,
                access_grant.granted_at.isoformat(),
                access_grant.expires_at.isoformat(),
                (
                    access_grant.revoked_at.isoformat()
                    if access_grant.revoked_at is not None
                    else None
                ),
            ),
        )

        grant_id = int(cursor.lastrowid)
        connection.commit()

    return access_grant.model_copy(
        update={
            "id": grant_id,
        }
    )


def get_access_grant_from_database(
    grant_id: int,
) -> AccessGrant | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM access_grants
            WHERE id = ?
            """,
            (grant_id,),
        ).fetchone()

    if row is None:
        return None

    return _to_access_grant(row)


def get_access_grants_from_database(
    requester_email: str | None = None,
) -> list[AccessGrant]:
    query = "SELECT * FROM access_grants"
    parameters: tuple[str, ...] = ()

    if requester_email is not None:
        query += " WHERE requester_email = ?"
        parameters = (requester_email,)

    query += " ORDER BY id ASC"

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        _to_access_grant(row)
        for row in rows
    ]


def get_active_grant_for_request(
    request_id: int,
) -> AccessGrant | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM access_grants
            WHERE request_id = ?
              AND status = 'ACTIVE'
            """,
            (request_id,),
        ).fetchone()

    if row is None:
        return None

    return _to_access_grant(row)


def revoke_access_grant(
    grant_id: int,
    revoked_at: str,
) -> AccessGrant | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE access_grants
            SET
                status = 'REVOKED',
                revoked_at = ?
            WHERE id = ?
              AND status = 'ACTIVE'
            """,
            (
                revoked_at,
                grant_id,
            ),
        )

        connection.commit()

    if cursor.rowcount == 0:
        return None

    return get_access_grant_from_database(
        grant_id
    )


# ============================================================
# Logs d'audit
# ============================================================

def save_audit_log(
    audit_log: AuditLog,
) -> AuditLog:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO audit_logs (
                actor_email,
                action,
                entity_type,
                entity_id,
                outcome,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                audit_log.actor_email,
                audit_log.action,
                audit_log.entity_type,
                audit_log.entity_id,
                audit_log.outcome,
                audit_log.created_at.isoformat(),
            ),
        )

        audit_id = int(cursor.lastrowid)
        connection.commit()

    return audit_log.model_copy(
        update={
            "id": audit_id,
        }
    )


def get_audit_logs_from_database() -> list[AuditLog]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM audit_logs
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        _to_audit_log(row)
        for row in rows
    ]


# ============================================================
# Nettoyage des tests
# ============================================================

def clear_database() -> None:
    """
    Supprime les données créées par les tests.

    Les quatre comptes de démonstration sont conservés.
    """
    demo_emails = (
        "alice.employee@asteriatech.local",
        "marc.manager@asteriatech.local",
        "ines.itadmin@asteriatech.local",
        "paul.security@asteriatech.local",
    )

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM audit_logs"
        )

        connection.execute(
            "DELETE FROM access_grants"
        )

        connection.execute(
            "DELETE FROM access_requests"
        )

        connection.execute(
            """
            DELETE FROM users
            WHERE email NOT IN (?, ?, ?, ?)
            """,
            demo_emails,
        )

        connection.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN (
                'audit_logs',
                'access_grants',
                'access_requests'
            )
            """
        )

        connection.commit()


# ============================================================
# Exécution directe
# ============================================================

if __name__ == "__main__":
    initialize_database()
    print(
        f"Base SQLite initialisée : {DATABASE_PATH}"
    )
