# AccessGuard V5 — Observabilité métier

## Objectif

La V5 enrichit l’observabilité AccessGuard avec des métriques métier
liées à l’authentification, aux demandes d’accès, aux décisions manager
et aux opérations d’administration des droits.

## Métriques disponibles

- `accessguard_login_success_total`
- `accessguard_login_failure_total`
- `accessguard_access_requests_total`
- `accessguard_manager_approvals_total`
- `accessguard_manager_refusals_total`
- `accessguard_access_grants_total`
- `accessguard_access_revocations_total`
- `accessguard_forbidden_actions_total`

## Endpoint Prometheus

Les métriques sont exposées à l’adresse :

```text
GET /metrics

Lancement
docker compose up --build -d
docker compose ps

Services :

API : http://localhost:8000
Prometheus : http://localhost:9090
Grafana : http://localhost:3000
Dashboard Grafana

Le dashboard exporté est stocké dans :

monitoring/grafana/dashboards/accessguard-v5.json
Validation

La validation comprend :

vérification de /metrics ;
requêtes PromQL ;
affichage Grafana ;
tests Pytest ;
validation Docker Compose.

---

# LOT 9 — Validation finale

## 22. Lancer les contrôles

```powershell
python -m pytest -v
python -m flake8 app tests
docker compose config --quiet
docker compose ps

Puis :

git status