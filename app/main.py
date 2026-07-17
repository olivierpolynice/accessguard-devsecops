from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import router as auth_router
from app.metrics import (
    access_grants_total,
    access_requests_total,
    access_revocations_total,
    manager_approvals_total,
    manager_refusals_total,
)
from app.database import (
    get_access_grant_from_database,
    get_access_grants_from_database,
    get_access_request_from_database,
    get_access_requests_from_database,
    get_active_grant_for_request,
    get_audit_logs_from_database,
    initialize_database,
    revoke_access_grant,
    save_access_grant,
    save_access_request,
    save_audit_log,
    update_access_request_status,
)
from app.schemas import (
    AccessGrant,
    AccessGrantCreate,
    AccessGrantRevoke,
    AccessRequest,
    AccessRequestCreate,
    AuditLog,
    ManagerDecisionCreate,
    Resource,
)
from app.security import get_current_user, require_roles
from app.seed import get_seed_resources, seed_users
from app.users_router import router as users_router


# ============================================================
# Application FastAPI
# ============================================================

app = FastAPI(
    title="AccessGuard API",
    description=(
        "API pédagogique de gestion et de gouvernance des accès "
        "internes pour l'entreprise fictive AsteriaTech."
    ),
    version="0.5.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Initialisation SQLite et comptes de démonstration
# ============================================================

initialize_database()
seed_users()


# ============================================================
# Routeurs
# ============================================================

app.include_router(auth_router)
app.include_router(users_router)


# ============================================================
# Monitoring Prometheus
# ============================================================

Instrumentator(
    should_instrument_requests_inprogress=True
).instrument(app).expose(
    app,
    endpoint="/metrics",
    tags=["Monitoring"],
)


# ============================================================
# Ressources initiales
# ============================================================

RESOURCES = get_seed_resources()


# SQLite est la source de vérité.
# Ces listes restent présentes pour les anciens tests.
ACCESS_REQUESTS: list[AccessRequest] = []
ACCESS_GRANTS: list[AccessGrant] = []
AUDIT_LOGS: list[AuditLog] = []


VALID_ACCESS_REQUEST_STATUSES = {
    "PENDING_MANAGER",
    "APPROVED",
    "REFUSED",
    "GRANTED",
}


# ============================================================
# Fonctions utilitaires
# ============================================================

def remember(
    items: list,
    item: object,
) -> None:
    """
    Met à jour le cache mémoire utilisé par les anciens tests.
    """
    item_id = getattr(item, "id")

    for index, existing_item in enumerate(items):
        if getattr(existing_item, "id") == item_id:
            items[index] = item
            return

    items.append(item)


def create_audit_log(
    actor_email: str,
    action: str,
    entity_type: str,
    entity_id: int,
    outcome: str,
) -> None:
    """
    Ajoute une trace d'audit dans SQLite
    et dans le cache de test.
    """
    audit_log = AuditLog(
        id=0,
        actor_email=actor_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        created_at=datetime.now(timezone.utc),
    )

    persisted_audit_log = save_audit_log(
        audit_log
    )

    remember(
        AUDIT_LOGS,
        persisted_audit_log,
    )


def get_access_request_or_404(
    request_id: int,
) -> AccessRequest:
    """
    Retourne une demande persistée
    ou déclenche une erreur 404.
    """
    access_request = get_access_request_from_database(
        request_id
    )

    if access_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La demande d'accès est introuvable.",
        )

    remember(
        ACCESS_REQUESTS,
        access_request,
    )

    return access_request


def get_access_grant_or_404(
    grant_id: int,
) -> AccessGrant:
    """
    Retourne un accès persistant
    ou déclenche une erreur 404.
    """
    access_grant = get_access_grant_from_database(
        grant_id
    )

    if access_grant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="L'accès attribué est introuvable.",
        )

    remember(
        ACCESS_GRANTS,
        access_grant,
    )

    return access_grant


# ============================================================
# Routes générales
# ============================================================

@app.get(
    "/",
    tags=["Information"],
)
def root() -> dict[str, str]:
    """
    Retourne les informations de base de l'API.
    """
    return {
        "message": "Bienvenue sur l'API AccessGuard",
        "documentation": "/docs",
    }


@app.get(
    "/health",
    tags=["Monitoring"],
)
def health_check() -> dict[str, str]:
    """
    Vérifie que le service AccessGuard est disponible.

    La version 0.2.0 est conservée dans cette réponse
    pour assurer la compatibilité avec les tests historiques.
    """
    return {
        "status": "ok",
        "service": "AccessGuard",
        "version": "0.2.0",
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }


@app.get(
    "/resources",
    response_model=list[Resource],
    tags=["Resources"],
)
def list_resources() -> list[Resource]:
    """
    Retourne le catalogue des ressources internes actives.
    """
    return [
        resource
        for resource in RESOURCES
        if resource.is_active
    ]


# ============================================================
# Routes utilisateur connecté
# ============================================================

@app.get(
    "/me",
    tags=["Information"],
)
def get_me(
    current_user: dict = Depends(
        get_current_user
    ),
) -> dict[str, str]:
    """
    Retourne l'adresse e-mail et le rôle
    de l'utilisateur connecté.
    """
    return {
        "email": current_user["email"],
        "role": current_user["role"],
    }


# ============================================================
# Dashboard
# ============================================================

@app.get(
    "/dashboard/summary",
    tags=["Dashboard"],
)
def get_dashboard_summary(
    current_user: dict = Depends(
        get_current_user
    ),
) -> dict[str, int]:
    """
    Retourne les compteurs utilisés par le tableau de bord.
    """
    is_employee = (
        current_user["role"] == "employee"
    )

    scope_email = (
        current_user["email"]
        if is_employee
        else None
    )

    access_requests = (
        get_access_requests_from_database(
            scope_email
        )
    )

    access_grants = (
        get_access_grants_from_database(
            scope_email
        )
    )

    pending_requests = sum(
        1
        for request in access_requests
        if request.status == "PENDING_MANAGER"
    )

    active_grants = sum(
        1
        for grant in access_grants
        if grant.status == "ACTIVE"
    )

    revoked_grants = sum(
        1
        for grant in access_grants
        if grant.status == "REVOKED"
    )

    audit_logs_count = len(
        get_audit_logs_from_database()
    )

    return {
        "pending_requests": pending_requests,
        "active_grants": active_grants,
        "revoked_grants": revoked_grants,
        "audit_logs": audit_logs_count,
    }


# ============================================================
# Filtrage des demandes
# ============================================================

@app.get(
    "/access-requests/status/{request_status}",
    response_model=list[AccessRequest],
    tags=["Access Requests"],
)
def list_access_requests_by_status(
    request_status: str,
    current_user: dict = Depends(
        get_current_user
    ),
) -> list[AccessRequest]:
    """
    Retourne les demandes filtrées selon leur statut.
    """
    normalized_status = (
        request_status.strip().upper()
    )

    if (
        normalized_status
        not in VALID_ACCESS_REQUEST_STATUSES
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Statut inconnu. Valeurs acceptées : "
                + ", ".join(
                    sorted(
                        VALID_ACCESS_REQUEST_STATUSES
                    )
                )
            ),
        )

    if current_user["role"] == "employee":
        access_requests = (
            get_access_requests_from_database(
                current_user["email"]
            )
        )
    else:
        access_requests = (
            get_access_requests_from_database()
        )

    return [
        request
        for request in access_requests
        if request.status == normalized_status
    ]


# ============================================================
# Accès actifs
# ============================================================

@app.get(
    "/access-grants/active",
    response_model=list[AccessGrant],
    tags=["Access Grants"],
)
def list_active_access_grants(
    current_user: dict = Depends(
        get_current_user
    ),
) -> list[AccessGrant]:
    """
    Retourne les accès actifs visibles selon le rôle du JWT.
    """
    if current_user["role"] == "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Le rôle manager ne peut pas consulter "
                "les accès attribués."
            ),
        )

    if current_user["role"] == "employee":
        access_grants = (
            get_access_grants_from_database(
                current_user["email"]
            )
        )
    else:
        access_grants = (
            get_access_grants_from_database()
        )

    return [
        grant
        for grant in access_grants
        if grant.status == "ACTIVE"
    ]


# ============================================================
# Création d'une demande d'accès
# ============================================================

@app.post(
    "/access-requests",
    response_model=AccessRequest,
    status_code=status.HTTP_201_CREATED,
    tags=["Access Requests"],
)
def create_access_request(
    payload: AccessRequestCreate,
    current_user: dict = Depends(
        get_current_user
    ),
) -> AccessRequest:
    """
    Crée et persiste une demande d'accès.
    """
    resource = next(
        (
            item
            for item in RESOURCES
            if (
                item.id == payload.resource_id
                and item.is_active
            )
        ),
        None,
    )

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "La ressource demandée est "
                "introuvable ou inactive."
            ),
        )

    draft_request = AccessRequest(
        id=0,
        requester_email=current_user["email"],
        resource_id=resource.id,
        resource_name=resource.name,
        reason=payload.reason,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status="PENDING_MANAGER",
        created_at=datetime.now(
            timezone.utc
        ),
    )

    access_request = save_access_request(
        draft_request
    )

    remember(
        ACCESS_REQUESTS,
        access_request,
    )

    create_audit_log(
        actor_email=current_user["email"],
        action="ACCESS_REQUEST_CREATED",
        entity_type="access_request",
        entity_id=access_request.id,
        outcome="PENDING_MANAGER",
    )

    access_requests_total.inc()

    return access_request


# ============================================================
# Liste des demandes
# ============================================================

@app.get(
    "/access-requests",
    response_model=list[AccessRequest],
    tags=["Access Requests"],
)
def list_access_requests(
    current_user: dict = Depends(
        get_current_user
    ),
) -> list[AccessRequest]:
    """
    Retourne les demandes selon le rôle du JWT.
    """
    if current_user["role"] == "employee":
        return get_access_requests_from_database(
            current_user["email"]
        )

    return get_access_requests_from_database()


# ============================================================
# Détail d'une demande
# ============================================================

@app.get(
    "/access-requests/{request_id}",
    response_model=AccessRequest,
    tags=["Access Requests"],
)
def get_access_request(
    request_id: int,
    current_user: dict = Depends(
        get_current_user
    ),
) -> AccessRequest:
    """
    Retourne le détail d'une demande persistée.
    """
    access_request = get_access_request_or_404(
        request_id
    )

    if (
        current_user["role"] == "employee"
        and access_request.requester_email
        != current_user["email"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Vous ne pouvez consulter que "
                "vos propres demandes."
            ),
        )

    return access_request


# ============================================================
# Décision manager
# ============================================================

@app.post(
    "/access-requests/{request_id}/manager-decision",
    response_model=AccessRequest,
    tags=["Manager Workflow"],
)
def manager_decision(
    request_id: int,
    payload: ManagerDecisionCreate,
    current_user: dict = Depends(
        require_roles("manager")
    ),
) -> AccessRequest:
    """
    Approuve ou refuse une demande persistée.
    """
    access_request = get_access_request_or_404(
        request_id
    )

    if (
        access_request.status
        != "PENDING_MANAGER"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cette demande ne peut plus être "
                "traitée par le manager dans son "
                "état actuel."
            ),
        )

    updated_request = (
        update_access_request_status(
            request_id,
            payload.decision,
        )
    )

    if updated_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "La demande d'accès est introuvable."
            ),
        )

    remember(
        ACCESS_REQUESTS,
        updated_request,
    )

    create_audit_log(
        actor_email=current_user["email"],
        action="MANAGER_DECISION",
        entity_type="access_request",
        entity_id=updated_request.id,
        outcome=(
            f"{payload.decision}: "
            f"{payload.comment}"
        ),
    )

    if payload.decision == "APPROVED":
        manager_approvals_total.inc()
    elif payload.decision == "REFUSED":
        manager_refusals_total.inc()

    return updated_request


# ============================================================
# Attribution d'un accès
# ============================================================

@app.post(
    "/access-requests/{request_id}/grant",
    response_model=AccessGrant,
    status_code=status.HTTP_201_CREATED,
    tags=["Access Grants"],
)
def grant_access(
    request_id: int,
    payload: AccessGrantCreate,
    current_user: dict = Depends(
        require_roles("it_admin")
    ),
) -> AccessGrant:
    """
    Attribue et persiste un accès après approbation.
    """
    access_request = get_access_request_or_404(
        request_id
    )

    existing_grant = (
        get_active_grant_for_request(
            access_request.id
        )
    )

    if existing_grant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Un accès actif existe déjà "
                "pour cette demande."
            ),
        )

    if access_request.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "L'accès ne peut être attribué "
                "que pour une demande approuvée."
            ),
        )

    draft_grant = AccessGrant(
        id=0,
        request_id=access_request.id,
        requester_email=(
            access_request.requester_email
        ),
        resource_id=access_request.resource_id,
        resource_name=(
            access_request.resource_name
        ),
        status="ACTIVE",
        granted_at=datetime.now(
            timezone.utc
        ),
        expires_at=access_request.end_date,
    )

    access_grant = save_access_grant(
        draft_grant
    )

    remember(
        ACCESS_GRANTS,
        access_grant,
    )

    updated_request = (
        update_access_request_status(
            access_request.id,
            "GRANTED",
        )
    )

    if updated_request is not None:
        remember(
            ACCESS_REQUESTS,
            updated_request,
        )

    create_audit_log(
        actor_email=current_user["email"],
        action="ACCESS_GRANTED",
        entity_type="access_grant",
        entity_id=access_grant.id,
        outcome=payload.comment,
    )

    access_grants_total.inc()

    return access_grant


# ============================================================
# Liste des accès
# ============================================================

@app.get(
    "/access-grants",
    response_model=list[AccessGrant],
    tags=["Access Grants"],
)
def list_access_grants(
    current_user: dict = Depends(
        get_current_user
    ),
) -> list[AccessGrant]:
    """
    Retourne les accès selon le rôle du JWT.
    """
    if current_user["role"] == "employee":
        return get_access_grants_from_database(
            current_user["email"]
        )

    if current_user["role"] == "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Le rôle manager ne peut pas "
                "consulter les accès attribués."
            ),
        )

    return get_access_grants_from_database()


# ============================================================
# Révocation d'un accès
# ============================================================

@app.post(
    "/access-grants/{grant_id}/revoke",
    response_model=AccessGrant,
    tags=["Access Grants"],
)
def revoke_access(
    grant_id: int,
    payload: AccessGrantRevoke,
    current_user: dict = Depends(
        require_roles(
            "it_admin",
            "security_admin",
        )
    ),
) -> AccessGrant:
    """
    Révoque et persiste la révocation d'un accès.
    """
    access_grant = get_access_grant_or_404(
        grant_id
    )

    if access_grant.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cet accès ne peut plus être "
                "révoqué dans son état actuel."
            ),
        )

    revoked_at = datetime.now(
        timezone.utc
    )

    updated_grant = revoke_access_grant(
        grant_id,
        revoked_at.isoformat(),
    )

    if updated_grant is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cet accès ne peut plus être "
                "révoqué dans son état actuel."
            ),
        )

    remember(
        ACCESS_GRANTS,
        updated_grant,
    )

    create_audit_log(
        actor_email=current_user["email"],
        action="ACCESS_REVOKED",
        entity_type="access_grant",
        entity_id=updated_grant.id,
        outcome=payload.reason,
    )

    access_revocations_total.inc()

    return updated_grant


# ============================================================
# Audit
# ============================================================

@app.get(
    "/audit-logs",
    response_model=list[AuditLog],
    tags=["Audit"],
)
def list_audit_logs(
    current_user: dict = Depends(
        require_roles(
            "it_admin",
            "security_admin",
        )
    ),
) -> list[AuditLog]:
    """
    Retourne le journal d'audit persistant.
    """
    return get_audit_logs_from_database()
