from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from schemas import (
    AccessGrant,
    AccessGrantCreate,
    AccessGrantRevoke,
    AccessRequest,
    AccessRequestCreate,
    AuditLog,
    ManagerDecisionCreate,
    Resource,
)
from seed import get_seed_resources

app = FastAPI(
    title="AccessGuard API",
    description=(
        "API pédagogique de gestion et de gouvernance des accès "
        "internes pour l'entreprise fictive AsteriaTech."
    ),
    version="0.1.0",
)

RESOURCES = get_seed_resources()

ACCESS_REQUESTS: list[AccessRequest] = []
ACCESS_GRANTS: list[AccessGrant] = []
AUDIT_LOGS: list[AuditLog] = []


def create_audit_log(
    actor_email: str,
    action: str,
    entity_type: str,
    entity_id: int,
    outcome: str,
) -> None:
    """Ajoute une trace dans le journal d'audit local."""
    audit_log = AuditLog(
        id=len(AUDIT_LOGS) + 1,
        actor_email=actor_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        created_at=datetime.now(timezone.utc),
    )
    AUDIT_LOGS.append(audit_log)


def get_access_request_or_404(request_id: int) -> AccessRequest:
    """Retourne une demande ou déclenche une erreur 404."""
    access_request = next(
        (item for item in ACCESS_REQUESTS if item.id == request_id),
        None,
    )

    if access_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La demande d'accès est introuvable.",
        )

    return access_request


def get_access_grant_or_404(grant_id: int) -> AccessGrant:
    """Retourne un accès attribué ou déclenche une erreur 404."""
    access_grant = next(
        (item for item in ACCESS_GRANTS if item.id == grant_id),
        None,
    )

    if access_grant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="L'accès attribué est introuvable.",
        )

    return access_grant


@app.get("/", tags=["Information"])
def root() -> dict[str, str]:
    """Retourne les informations de base de l'API."""
    return {
        "message": "Bienvenue sur l'API AccessGuard",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Vérifie que le service AccessGuard est disponible."""
    return {
        "status": "ok",
        "service": "AccessGuard",
        "version": "0.1.0",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get(
    "/resources",
    response_model=list[Resource],
    tags=["Resources"],
)
def list_resources() -> list[Resource]:
    """Retourne le catalogue des ressources internes actives."""
    return [resource for resource in RESOURCES if resource.is_active]


@app.post(
    "/access-requests",
    response_model=AccessRequest,
    status_code=status.HTTP_201_CREATED,
    tags=["Access Requests"],
)
def create_access_request(payload: AccessRequestCreate) -> AccessRequest:
    """Crée une demande d'accès soumise à la validation du manager."""
    resource = next(
        (
            item
            for item in RESOURCES
            if item.id == payload.resource_id and item.is_active
        ),
        None,
    )

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La ressource demandée est introuvable ou inactive.",
        )

    access_request = AccessRequest(
        id=len(ACCESS_REQUESTS) + 1,
        requester_email=payload.requester_email,
        resource_id=resource.id,
        resource_name=resource.name,
        reason=payload.reason,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status="PENDING_MANAGER",
        created_at=datetime.now(timezone.utc),
    )

    ACCESS_REQUESTS.append(access_request)

    create_audit_log(
        actor_email=payload.requester_email,
        action="ACCESS_REQUEST_CREATED",
        entity_type="access_request",
        entity_id=access_request.id,
        outcome="PENDING_MANAGER",
    )

    return access_request


@app.get(
    "/access-requests",
    response_model=list[AccessRequest],
    tags=["Access Requests"],
)
def list_access_requests() -> list[AccessRequest]:
    """Retourne les demandes d'accès créées dans l'environnement local."""
    return ACCESS_REQUESTS


@app.get(
    "/access-requests/{request_id}",
    response_model=AccessRequest,
    tags=["Access Requests"],
)
def get_access_request(request_id: int) -> AccessRequest:
    """Retourne le détail d'une demande d'accès à partir de son identifiant."""
    return get_access_request_or_404(request_id)


@app.post(
    "/access-requests/{request_id}/manager-decision",
    response_model=AccessRequest,
    tags=["Manager Workflow"],
)
def manager_decision(
    request_id: int,
    payload: ManagerDecisionCreate,
) -> AccessRequest:
    """Permet au manager d'approuver ou de refuser une demande."""
    access_request = get_access_request_or_404(request_id)

    if access_request.status != "PENDING_MANAGER":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cette demande ne peut plus être traitée par le manager "
                "dans son état actuel."
            ),
        )

    access_request.status = payload.decision

    create_audit_log(
        actor_email=payload.manager_email,
        action="MANAGER_DECISION",
        entity_type="access_request",
        entity_id=access_request.id,
        outcome=f"{payload.decision}: {payload.comment}",
    )

    return access_request


@app.post(
    "/access-requests/{request_id}/grant",
    response_model=AccessGrant,
    status_code=status.HTTP_201_CREATED,
    tags=["Access Grants"],
)
def grant_access(
    request_id: int,
    payload: AccessGrantCreate,
) -> AccessGrant:
    """Attribue un accès après approbation de la demande."""
    access_request = get_access_request_or_404(request_id)

    existing_grant = next(
        (
            grant
            for grant in ACCESS_GRANTS
            if grant.request_id == access_request.id and grant.status == "ACTIVE"
        ),
        None,
    )

    if existing_grant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un accès actif existe déjà pour cette demande.",
        )

    if access_request.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "L'accès ne peut être attribué que pour une demande "
                "approuvée."
            ),
        )

    access_grant = AccessGrant(
        id=len(ACCESS_GRANTS) + 1,
        request_id=access_request.id,
        requester_email=access_request.requester_email,
        resource_id=access_request.resource_id,
        resource_name=access_request.resource_name,
        status="ACTIVE",
        granted_at=datetime.now(timezone.utc),
        expires_at=access_request.end_date,
    )

    ACCESS_GRANTS.append(access_grant)
    access_request.status = "GRANTED"

    create_audit_log(
        actor_email=payload.it_admin_email,
        action="ACCESS_GRANTED",
        entity_type="access_grant",
        entity_id=access_grant.id,
        outcome=payload.comment,
    )

    return access_grant


@app.get(
    "/access-grants",
    response_model=list[AccessGrant],
    tags=["Access Grants"],
)
def list_access_grants() -> list[AccessGrant]:
    """Retourne les accès attribués dans l'environnement local."""
    return ACCESS_GRANTS


@app.post(
    "/access-grants/{grant_id}/revoke",
    response_model=AccessGrant,
    tags=["Access Grants"],
)
def revoke_access(
    grant_id: int,
    payload: AccessGrantRevoke,
) -> AccessGrant:
    """Révoque un accès actif et génère un événement d'audit."""
    access_grant = get_access_grant_or_404(grant_id)

    if access_grant.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet accès ne peut plus être révoqué dans son état actuel.",
        )

    access_grant.status = "REVOKED"
    access_grant.revoked_at = datetime.now(timezone.utc)

    create_audit_log(
        actor_email=payload.it_admin_email,
        action="ACCESS_REVOKED",
        entity_type="access_grant",
        entity_id=access_grant.id,
        outcome=payload.reason,
    )

    return access_grant


@app.get(
    "/audit-logs",
    response_model=list[AuditLog],
    tags=["Audit"],
)
def list_audit_logs() -> list[AuditLog]:
    """Retourne le journal d'audit local de la plateforme."""
    return AUDIT_LOGS
