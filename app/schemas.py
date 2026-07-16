from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


# ============================================================
# Ressources
# ============================================================

class Resource(BaseModel):
    """Représente une ressource interne accessible via AccessGuard."""

    id: int
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )
    description: str
    sensitivity: str
    is_active: bool


# ============================================================
# Demandes d'accès
# ============================================================

class AccessRequestCreate(BaseModel):
    """Données nécessaires pour créer une demande d'accès."""

    resource_id: int = Field(
        ...,
        gt=0,
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
    )
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "AccessRequestCreate":
        if self.end_date < self.start_date:
            raise ValueError(
                "La date de fin doit être postérieure ou égale "
                "à la date de début."
            )

        return self


class AccessRequest(BaseModel):
    """Représente une demande d'accès."""

    id: int
    requester_email: str
    resource_id: int
    resource_name: str
    reason: str
    start_date: date
    end_date: date
    status: str
    created_at: datetime


class ManagerDecisionCreate(BaseModel):
    """Décision prise par un manager."""

    decision: str = Field(
        ...,
        pattern="^(APPROVED|REFUSED)$",
    )
    comment: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )


# ============================================================
# Accès attribués
# ============================================================

class AccessGrantCreate(BaseModel):
    """Données nécessaires pour attribuer un accès."""

    comment: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )


class AccessGrantRevoke(BaseModel):
    """Données nécessaires pour révoquer un accès."""

    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )


class AccessGrant(BaseModel):
    """Représente un accès attribué à un utilisateur."""

    id: int
    request_id: int
    requester_email: str
    resource_id: int
    resource_name: str
    status: str
    granted_at: datetime
    expires_at: date
    revoked_at: datetime | None = None


# ============================================================
# Audit
# ============================================================

class AuditLog(BaseModel):
    """Trace d'une action sensible réalisée dans la plateforme."""

    id: int
    actor_email: str
    action: str
    entity_type: str
    entity_id: int
    outcome: str
    created_at: datetime


# ============================================================
# Validation des adresses internes
# ============================================================

def validate_internal_email(
    email: str,
) -> str:
    """
    Valide une adresse interne AsteriaTech.

    Exemple accepté :
    alice.employee@asteriatech.local
    """
    if not isinstance(email, str):
        raise ValueError(
            "L'adresse e-mail doit être une chaîne de caractères."
        )

    normalized_email = email.strip().lower()

    if not normalized_email:
        raise ValueError(
            "L'adresse e-mail ne peut pas être vide."
        )

    if len(normalized_email) > 255:
        raise ValueError(
            "L'adresse e-mail est trop longue."
        )

    if normalized_email.count("@") != 1:
        raise ValueError(
            "L'adresse e-mail doit contenir un seul caractère @."
        )

    local_part, domain = normalized_email.split(
        "@",
        1,
    )

    if not local_part:
        raise ValueError(
            "La partie locale de l'adresse e-mail est obligatoire."
        )

    if domain != "asteriatech.local":
        raise ValueError(
            "L'adresse e-mail doit appartenir au domaine "
            "asteriatech.local."
        )

    return normalized_email


# ============================================================
# Utilisateurs V5
# ============================================================

class UserRole(str, Enum):
    """Rôles autorisés dans AccessGuard."""

    EMPLOYEE = "employee"
    MANAGER = "manager"
    IT_ADMIN = "it_admin"
    SECURITY_ADMIN = "security_admin"


class UserCreate(BaseModel):
    """
    Données reçues pour créer un utilisateur.

    Le mot de passe est accepté uniquement en entrée.
    Il n'est jamais présent dans UserResponse.
    """

    email: str = Field(
        min_length=5,
        max_length=255,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role: UserRole = UserRole.EMPLOYEE

    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str,
    ) -> str:
        return validate_internal_email(value)


class UserResponse(BaseModel):
    """
    Représentation publique d'un utilisateur.

    Ce schéma ne contient jamais :
    - password ;
    - password_hash.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str,
    ) -> str:
        return validate_internal_email(value)


class UserRoleUpdate(BaseModel):
    """Données reçues pour modifier le rôle d'un utilisateur."""

    role: UserRole


class UserStatusUpdate(BaseModel):
    """Données reçues pour activer ou désactiver un compte."""

    is_active: bool


# ============================================================
# Compatibilité avec les routes CRUD déjà développées
# ============================================================

class UserUpdate(BaseModel):
    """
    Données générales modifiables sur un utilisateur.

    Ce schéma est conservé pour les routes PATCH existantes.
    """

    email: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
    )

    role: UserRole | None = None

    is_active: bool | None = None

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        return validate_internal_email(value)


class UserPasswordUpdate(BaseModel):
    """
    Nouveau mot de passe d'un utilisateur.

    Ce mot de passe sera haché avant stockage.
    """

    password: str = Field(
        min_length=8,
        max_length=72,
    )


# Alias conservé pour ne pas casser les routes existantes
# utilisant response_model=User.
User = UserResponse