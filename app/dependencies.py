"""
Dépendances FastAPI centralisées pour AccessGuard.

La logique de sécurité est définie dans app.security.
Ce module réexporte les dépendances pour conserver
la compatibilité avec les anciennes routes.
"""

from app.security import (
    get_current_user,
    require_roles,
)


__all__ = [
    "get_current_user",
    "require_roles",
]