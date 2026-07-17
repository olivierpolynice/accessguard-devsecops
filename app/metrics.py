from prometheus_client import Counter


login_success_total = Counter(
    "accessguard_login_success_total",
    "Nombre total de connexions réussies.",
)

login_failure_total = Counter(
    "accessguard_login_failure_total",
    "Nombre total de connexions échouées.",
)

access_requests_total = Counter(
    "accessguard_access_requests_total",
    "Nombre total de demandes d'accès créées.",
)

manager_approvals_total = Counter(
    "accessguard_manager_approvals_total",
    "Nombre total de demandes approuvées par un manager.",
)

manager_refusals_total = Counter(
    "accessguard_manager_refusals_total",
    "Nombre total de demandes refusées par un manager.",
)

access_grants_total = Counter(
    "accessguard_access_grants_total",
    "Nombre total d'accès accordés.",
)

access_revocations_total = Counter(
    "accessguard_access_revocations_total",
    "Nombre total d'accès révoqués.",
)

forbidden_actions_total = Counter(
    "accessguard_forbidden_actions_total",
    "Nombre total d'actions refusées pour cause de permissions insuffisantes.",
)
