# Frontend AccessGuard

## Lancement avec Live Server

1. Ouvrir le projet dans VS Code.
2. Installer l'extension Live Server.
3. Ouvrir `index.html`.
4. Cliquer sur « Open with Live Server ».

## Lancement avec Python sur Mac

Depuis le dossier `frontend` :

```bash
python3 -m http.server 5500
```

Puis ouvrir : http://localhost:5500

## Fichiers

- `index.html` : structure de l'interface (6 sections)
- `styles.css` : design, typographie, responsive
- `README.md` : documentation du frontend

## Pages représentées

- Login
- Dashboard
- Demandes d'accès
- Accès attribués
- Audit logs
- Monitoring

## Rôle dans la V3 / V4

Cette interface complète la partie backend et DevSecOps :

- API FastAPI
- JWT / RBAC
- SQLite
- Docker
- Prometheus
- Grafana

## Limites

Ce prototype est statique. Il n'est pas encore connecté à l'API FastAPI.

Une future version pourrait ajouter :

- connexion réelle avec `/auth/login` ;
- appels API vers `/access-requests` ;
- affichage dynamique des audits ;
- intégration complète React ou Vue.js.

## Contribution V4

La V4 apporte des améliorations de design, de lisibilité, d'ergonomie et de responsive design.