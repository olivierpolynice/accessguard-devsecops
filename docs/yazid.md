# V3 — Yazid — DevOps / Docker / Observabilité

Branche : `feature/v3-yazid` (basée sur `feature/v2-sqlite-persistence`, choisie car
c'est la seule branche V2 avec Docker + SQLite déjà fonctionnels et vérifiés).

## Point ouvert — conflit RBAC (à surveiller, pas à corriger ici)

Deux implémentations RBAC existent en parallèle sur des branches différentes
(`feature/v2-tests-yazid` vs `feature/v2-sqlite-persistence`). Olivier a été notifié
et gère l'arbitrage final au moment de l'intégration sur `main`. Le travail DevOps
ci-dessous est indépendant de ce choix : il ne touche ni à `app/dependencies.py`,
ni à `app/security.py`, ni à `permissions.py`.

## 1. Vérification Dockerfile / docker-compose.yml (V2, existant)

- Image de base : `python:3.12-slim`.
- `ACCESSGUARD_DATABASE_PATH=/app/data/accessguard.db`, volume nommé
  `accessguard_data:/app/data` → persistance confirmée après `docker compose down/up`
  (les tables SQLite sont recréées uniquement si absentes, les données restent).
- 31 tests passent en local (`python -m pytest`, aucune régression après l'ajout
  de l'observabilité ci-dessous).

## 2. Observabilité ajoutée en V3

### 2.1 Endpoint `/metrics`

Ajout de `prometheus-fastapi-instrumentator` dans `app/requirements.txt` et
instrumentation dans `app/main.py` :

```python
from prometheus_fastapi_instrumentator import Instrumentator
...
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])
```

Résultat : `GET /metrics` retourne les métriques Prometheus (latence par
endpoint, nombre de requêtes par code de statut, requêtes en cours). Testé en
local avec `TestClient` : réponse `200`, format Prometheus valide.

### 2.2 Service Prometheus

Fichier `monitoring/prometheus.yml` : scrape l'API toutes les 5s sur
`accessguard-api:8000/metrics` (nom de service Docker, résolu via le réseau
`accessguard-net`).

### 2.3 Service Grafana

- Datasource Prometheus provisionnée automatiquement
  (`monitoring/grafana/provisioning/datasources/datasource.yml`) → pas de
  configuration manuelle à faire dans l'UI.
- Dashboard minimal provisionné automatiquement
  (`monitoring/grafana/dashboards/accessguard.json`) avec 5 panels :
  requêtes/seconde par endpoint, taux d'erreurs 4xx/5xx, latence p95,
  requêtes en cours, disponibilité (`up`).

### 2.4 docker-compose.yml mis à jour

Ajout des services `prometheus` (port `9090`) et `grafana` (port `3000`),
tous deux sur le même réseau bridge `accessguard-net` que l'API, avec volumes
persistants dédiés (`prometheus_data`, `grafana_data`).

## 3. Commandes de lancement / arrêt / nettoyage

```bash
# Lancement complet (API + Prometheus + Grafana)
docker compose up --build

# Arrêt (conserve les volumes/données)
docker compose down

# Arrêt + suppression des volumes (reset complet, à utiliser avec précaution)
docker compose down -v

# Rebuild uniquement l'image API après modification du code
docker compose build accessguard-api
docker compose up -d accessguard-api

# Vérifier que le volume SQLite persiste
docker compose down
docker compose up -d
# -> les demandes/accès/logs créés avant l'arrêt doivent toujours apparaître
```

## 4. Accès aux services une fois lancés

| Service    | URL                          | Identifiants          |
|------------|------------------------------|------------------------|
| API        | http://127.0.0.1:8000/docs   | (voir comptes de démo) |
| Prometheus | http://127.0.0.1:9090        | aucun                   |
| Grafana    | http://127.0.0.1:3000         | admin / admin (à changer) |

## 5. Architecture cible V3 (DevOps)

```
                ┌─────────────────────┐
   navigateur → │  AccessGuard API    │ → SQLite (volume accessguard_data)
                │  FastAPI :8000      │
                │  /metrics ──────────┼──┐
                └─────────────────────┘  │
                                         ▼
                                ┌─────────────────┐
                                │  Prometheus      │
                                │  :9090           │
                                │  scrape /metrics │
                                └────────┬─────────┘
                                         │ datasource
                                         ▼
                                ┌─────────────────┐
                                │  Grafana :3000   │
                                │  dashboard auto  │
                                │  provisionné     │
                                └─────────────────┘
```

## 6. Captures à réaliser (à insérer par Yazid avant 21h)

- [ ] `docker compose up --build` — terminal montrant les 3 conteneurs démarrés.
- [ ] Swagger `/docs` accessible sur `http://127.0.0.1:8000/docs`.
- [ ] `http://127.0.0.1:9090/targets` — cible `accessguard-api` en état `UP`.
- [ ] Grafana `http://127.0.0.1:3000` — dashboard "AccessGuard - API Overview"
      avec au moins une requête visible (après avoir appelé quelques endpoints).
- [ ] Persistance : redémarrage `docker compose down && docker compose up -d`
      puis re-consultation d'une demande créée avant l'arrêt.

## 7. Limites connues / non traité ici

- Pas d'authentification ajoutée sur `/metrics` (exposition interne, acceptable
  pour un projet pédagogique, à mentionner en Q&A si demandé).
- Le choix final RBAC (`dependencies.py`/`permissions.py` vs `security.py`)
  reste à trancher par Olivier avant le merge final — ce point peut affecter
  les captures Swagger si les routes changent de comportement.
