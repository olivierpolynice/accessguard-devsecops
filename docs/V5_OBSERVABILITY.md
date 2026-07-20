# AccessGuard V5 — Observabilité

## 1. Objectif

La V5 renforce l’observabilité d’AccessGuard afin de surveiller le fonctionnement de l’API, les actions métier sensibles et l’état des services techniques.

La solution repose sur :

- FastAPI pour l’exposition des métriques ;
- Prometheus pour la collecte et l’interrogation ;
- Grafana pour la visualisation ;
- Docker Compose pour l’orchestration des services ;
- le journal d’audit pour la traçabilité des actions.

## 2. Architecture

Les services d’observabilité sont accessibles aux adresses suivantes :

| Service | Adresse | Utilité |
|---|---|---|
| API AccessGuard | http://localhost:8000 | API principale |
| Santé de l’API | http://localhost:8000/health | Vérification de disponibilité |
| Métriques | http://localhost:8000/metrics | Exposition des métriques Prometheus |
| Prometheus | http://localhost:9090 | Collecte et interrogation des métriques |
| Grafana | http://localhost:3000 | Tableaux de bord |
| Frontend | http://localhost:5173 | Interface React en développement |

## 3. Démarrage des services

Depuis la racine du projet :

```bash
docker compose up -d --build