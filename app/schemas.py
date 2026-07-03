from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


class Resource(BaseModel):
    """Représente une ressource interne accessible via AccessGuard."""

    id: int
    name: str = Field(..., min_length=3, max_length=100)
    description: str
    sensitivity: str
    is_active: bool


class AccessRequestCreate(BaseModel):
    """Données fournies lors de la création d'une demande d'accès."""

    requester_email: str = Field(..., min_length=5, max_length=150)
    resource_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=10, max_length=500)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> "AccessRequestCreate":
        """Vérifie que la date de fin est cohérente."""
        if self.end_date < self.start_date:
            raise ValueError(
                "La date de fin doit être postérieure ou égale à la date de début."
            )
        return self


class AccessRequest(BaseModel):
    """Représente une demande d'accès créée dans AccessGuard."""

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
    """Décision prise par un manager sur une demande d'accès."""

    manager_email: str = Field(..., min_length=5, max_length=150)
    decision: str = Field(..., pattern="^(APPROVED|REFUSED)$")
    comment: str = Field(..., min_length=5, max_length=500)


class AccessGrantCreate(BaseModel):
    """Données nécessaires à l'attribution d'un accès par un IT Admin."""

    it_admin_email: str = Field(..., min_length=5, max_length=150)
    comment: str = Field(..., min_length=5, max_length=500)


class AccessGrantRevoke(BaseModel):
    """Données nécessaires à la révocation d'un accès."""

    it_admin_email: str = Field(..., min_length=5, max_length=150)
    reason: str = Field(..., min_length=5, max_length=500)


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


class AuditLog(BaseModel):
    """Trace d'une action sensible réalisée dans la plateforme."""

    id: int
    actor_email: str
    action: str
    entity_type: str
    entity_id: int
    outcome: str
    created_at: datetime


class LoginRequest(BaseModel):
    """Identifiants soumis lors de l'authentification."""

    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=1, max_length=200)


class TokenResponse(BaseModel):
    """Jeton JWT retourné après une authentification réussie."""

    access_token: str
    token_type: str = "bearer"
    email: str
    role: str
    expires_in_minutes: int
