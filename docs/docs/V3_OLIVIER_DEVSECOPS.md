# V3 — Partie Olivier : Monitoring, Prometheus, Grafana et Docker

## 1. Objectif de la V3

La V3 d’AccessGuard ajoute une couche DevSecOps autour de l’API existante.

L’objectif est de rendre l’application plus observable, plus industrialisée et plus proche d’un environnement professionnel. La V2 fournissait déjà une API sécurisée avec JWT, RBAC, persistance SQLite et Docker. La V3 ajoute la supervision avec Prometheus et Grafana.

## 2. Fonctionnalités ajoutées

### Endpoint `/metrics`

L’API expose maintenant un endpoint :

```text
/metrics
```

Ce endpoint permet à Prometheus de récupérer automatiquement les métriques de l’application FastAPI.

Exemples de métriques disponibles :

```text
http_requests_total
http_request_duration_highr_seconds_count
python_info
up
```

## 3. Prometheus

Prometheus est ajouté dans `docker-compose.yml`.

Il interroge régulièrement l’API AccessGuard sur :

```text
http://accessguard-api:8000/metrics
```

Le fichier de configuration est situé ici :

```text
monitoring/prometheus/prometheus.yml
```

Configuration utilisée :

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "accessguard-api"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["accessguard-api:8000"]
```

## 4. Grafana

Grafana est ajouté dans Docker Compose afin de visualiser les métriques collectées par Prometheus.

Accès Grafana :

```text
http://127.0.0.1:3000
```

Identifiants de démonstration :

```text
admin / admin
```

La datasource Prometheus est configurée avec l’URL interne Docker :

```text
http://prometheus:9090
```

Dashboard créé :

```text
AccessGuard V3 Monitoring
```

Panels principaux :

```text
AccessGuard - Service UP
AccessGuard - HTTP Requests Total
```

## 5. Docker Compose V3

La stack V3 contient trois services :

```text
accessguard-api
prometheus
grafana
```

Ports utilisés :

```text
API AccessGuard : http://127.0.0.1:8000/docs
Prometheus      : http://127.0.0.1:9090
Grafana         : http://127.0.0.1:3000
```

## 6. Healthcheck Docker

Un healthcheck Docker est ajouté sur l’API afin de vérifier automatiquement que le service répond correctement sur :

```text
/health
```

Le conteneur `accessguard-api` passe en état `Healthy` lorsque l’API répond avec succès.

## 7. Commandes de validation

Lancement de la stack :

```powershell
docker compose up --build --force-recreate
```

Vérification des services :

```powershell
docker compose ps
```

Tests Python :

```powershell
python -m pytest -v
```

## 8. Captures de preuve

Captures attendues :

```text
Capture-V3-01-Metrics-Prometheus-API.png
Capture-V3-02-Docker-Compose-Prometheus-Grafana-Healthy.png
Capture-V3-03-Prometheus-target-accessguard-UP.png
Capture-V3-04-Grafana-datasource-Prometheus-success.png
Capture-V3-05-Grafana-Explore-UP-1.png
Capture-V3-06-Grafana-dashboard-AccessGuard-Monitoring.png
Capture-V3-07-Tests-apres-monitoring-31-passed.png
Capture-V3-08-Docker-compose-services-running.png
```

## 9. Limites

Cette V3 met en place une supervision fonctionnelle, mais elle reste pédagogique.

Améliorations possibles :

- provisionner automatiquement la datasource Grafana ;
- versionner le dashboard Grafana en JSON ;
- ajouter des alertes Prometheus ;
- ajouter des métriques métier spécifiques ;
- ajouter Loki pour les logs applicatifs ;
- ajouter un scan de sécurité d’image Docker.
