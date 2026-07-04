from app.schemas import Resource


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