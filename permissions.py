# permissions.py
from typing import Final

ROLE_PERMISSIONS: Final[dict[str, set[str]]] = {
    "create_access_request": {"employee"},
    "manager_decision": {"manager"},
    "grant_access": {"it_admin"},
    "revoke_access": {"it_admin"},
    "list_audit_logs": {"security_admin"},
}
