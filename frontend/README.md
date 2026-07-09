# Frontend V3 — Prototype AccessGuard

## Objectif

Ce dossier contient un prototype frontend statique pour la V3 du projet AccessGuard.

Il sert à présenter une interface professionnelle destinée à rendre le projet plus lisible pour un utilisateur non technique ou un jury.

## Pages représentées

- Dashboard
- Demandes d’accès
- Accès attribués
- Audit logs
- Monitoring

## Lancement

Ouvrir directement le fichier suivant dans un navigateur :

```text
frontend/index.html
```

Aucun serveur frontend n’est nécessaire.

## Rôle dans la V3

Cette interface complète la partie backend et DevSecOps :

- API FastAPI
- JWT / RBAC
- SQLite
- Docker
- Prometheus
- Grafana

## Limites

Ce prototype est statique. Il n’est pas encore connecté à l’API FastAPI.

Une future version pourrait ajouter :

- connexion réelle avec `/auth/login` ;
- appels API vers `/access-requests` ;
- affichage dynamique des audits ;
- intégration complète React ou Vue.js.
