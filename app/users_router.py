from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import (
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.security import require_roles
from app.user_repository import (
    create_user,
    get_user_by_id,
    list_users,
    update_user_role,
    update_user_status,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# Toutes les routes utilisateurs sont réservées
# au rôle security_admin.
security_admin_required = require_roles(
    "security_admin"
)


def get_user_or_404(
    user_id: int,
) -> dict:
    """
    Retourne un utilisateur ou déclenche une erreur 404.
    """
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    return user


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_users(
    current_user: dict = Depends(
        security_admin_required
    ),
) -> list[dict]:
    """
    Retourne tous les utilisateurs.

    Accès réservé au security_admin.
    """
    del current_user

    return list_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: int,
    current_user: dict = Depends(
        security_admin_required
    ),
) -> dict:
    """
    Retourne un utilisateur par son identifiant.

    Accès réservé au security_admin.
    """
    del current_user

    return get_user_or_404(user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_user(
    payload: UserCreate,
    current_user: dict = Depends(
        security_admin_required
    ),
) -> dict:
    """
    Crée un utilisateur dans SQLite.

    Le mot de passe est haché avant stockage.
    """
    del current_user

    try:
        return create_user(
            email=payload.email,
            password=payload.password,
            role=payload.role.value,
            is_active=payload.is_active,
        )

    except ValueError as error:
        error_message = str(error)

        if "déjà" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            ) from error

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=error_message,
        ) from error


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def patch_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: dict = Depends(
        security_admin_required
    ),
) -> dict:
    """
    Modifie le rôle d'un utilisateur.

    Les rôles invalides sont rejetés par Pydantic avec 422.
    """
    del current_user

    get_user_or_404(user_id)

    updated_user = update_user_role(
        user_id=user_id,
        role=payload.role.value,
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    return updated_user


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def patch_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user: dict = Depends(
        security_admin_required
    ),
) -> dict:
    """
    Active ou désactive un utilisateur.
    """
    del current_user

    get_user_or_404(user_id)

    updated_user = update_user_status(
        user_id=user_id,
        is_active=payload.is_active,
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    return updated_user
