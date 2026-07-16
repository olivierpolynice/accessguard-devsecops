from typing import Final

from app.schemas import Resource
from app.security import verify_password
from app.user_repository import (
    create_user,
    get_user_by_email_with_password,
    update_user_password,
    update_user_role,
    update_user_status,
)


# ============================================================
# Comptes de démonstration
# ============================================================

DEMO_PASSWORD: Final[str] = "AccessGuard123!"

DEMO_USERS: Final[tuple[dict[str, object], ...]] = (
    {
        "email": "alice.employee@asteriatech.local",
        "password": DEMO_PASSWORD,
        "role": "employee",
        "is_active": True,
    },
    {
        "email": "marc.manager@asteriatech.local",
        "password": DEMO_PASSWORD,
        "role": "manager",
        "is_active": True,
    },
    {
        "email": "ines.itadmin@asteriatech.local",
        "password": DEMO_PASSWORD,
        "role": "it_admin",
        "is_active": True,
    },
    {
        "email": "paul.security@asteriatech.local",
        "password": DEMO_PASSWORD,
        "role": "security_admin",
        "is_active": True,
    },
)


# ============================================================
# Ressources de démonstration
# ============================================================

def get_seed_resources() -> list[Resource]:
    """Retourne les ressources initiales d'AsteriaTech."""

    return [
        Resource(
            id=1,
            name="VPN Entreprise",
            description=(
                "Accès distant sécurisé aux ressources internes "
                "d'AsteriaTech."
            ),
            sensitivity="MEDIUM",
            is_active=True,
        ),
        Resource(
            id=2,
            name="Serveur de fichiers Finance",
            description=(
                "Partage de fichiers réservé aux documents budgétaires "
                "et financiers."
            ),
            sensitivity="HIGH",
            is_active=True,
        ),
        Resource(
            id=3,
            name="Environnement de développement",
            description=(
                "Environnement partagé de test et de développement "
                "des applications internes."
            ),
            sensitivity="HIGH",
            is_active=True,
        ),
        Resource(
            id=4,
            name="Portail d'administration",
            description=(
                "Portail réservé aux actions d'administration "
                "des systèmes internes."
            ),
            sensitivity="CRITICAL",
            is_active=True,
        ),
        Resource(
            id=5,
            name="Plateforme Grafana",
            description=(
                "Tableaux de bord de supervision et métriques "
                "techniques."
            ),
            sensitivity="LOW",
            is_active=True,
        ),
    ]


# ============================================================
# Seed utilisateurs
# ============================================================

def seed_users() -> None:
    """
    Crée ou restaure les quatre comptes de démonstration.

    La fonction est idempotente :
    plusieurs exécutions ne créent aucun doublon.

    Lorsqu'un compte existe déjà, le seed restaure :
    - son rôle attendu ;
    - son état actif ;
    - son mot de passe de démonstration.
    """

    for demo_user in DEMO_USERS:
        email = str(demo_user["email"])
        password = str(demo_user["password"])
        role = str(demo_user["role"])
        is_active = bool(demo_user["is_active"])

        existing_user = get_user_by_email_with_password(
            email
        )

        if existing_user is None:
            create_user(
                email=email,
                password=password,
                role=role,
                is_active=is_active,
            )
            continue

        user_id = int(existing_user["id"])

        if existing_user["role"] != role:
            update_user_role(
                user_id=user_id,
                role=role,
            )

        if bool(existing_user["is_active"]) != is_active:
            update_user_status(
                user_id=user_id,
                is_active=is_active,
            )

        if not verify_password(
            password,
            existing_user["password_hash"],
        ):
            update_user_password(
                user_id=user_id,
                new_password=password,
            )
