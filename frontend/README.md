# Frontend AccessGuard

Interface utilisateur React/Vite pour AccessGuard, connectée à l’API FastAPI.

## Fonctionnalités

Le frontend permet notamment :

- la connexion avec les comptes de démonstration ;
- l’identification du rôle de l’utilisateur ;
- l’affichage des ressources disponibles ;
- la création de demandes d’accès ;
- la consultation des demandes ;
- la validation ou le refus côté Manager ;
- l’attribution et la révocation des accès côté IT Admin ;
- la consultation des journaux d’audit ;
- l’affichage d’un tableau de bord adapté au rôle.

## Technologies

- React
- Vite
- JavaScript
- CSS
- API REST FastAPI
- authentification JWT
- contrôle d’accès RBAC

## Installation

Depuis la racine du projet :

```bash
cd frontend
npm install


Lancement
npm run dev

L’application est généralement disponible à l’adresse :

http://localhost:5173

Le backend FastAPI doit être lancé séparément sur :

http://127.0.0.1:8000
Comptes de démonstration

Mot de passe commun :

AccessGuard123!
Employee
alice.employee@asteriatech.local
Manager
marc.manager@asteriatech.local
IT Admin
ines.itadmin@asteriatech.local
Security Admin
paul.security@asteriatech.local
Rôles
Employee
consulter les ressources ;
créer une demande d’accès ;
consulter ses propres demandes ;
consulter ses propres accès.
Manager
consulter les demandes ;
approuver ou refuser les demandes en attente.
IT Admin
consulter les demandes approuvées ;
attribuer les accès ;
consulter les accès actifs ;
révoquer les accès ;
consulter les journaux d’audit selon les règles définies.
Security Admin
consulter les journaux d’audit ;
consulter les événements sensibles ;
révoquer un accès lorsque cette permission est autorisée.
Principales routes utilisées
POST /auth/login
GET /me
GET /resources
GET /dashboard/summary
POST /access-requests
GET /access-requests
GET /access-requests/status/{status}
POST /access-requests/{id}/manager-decision
POST /access-requests/{id}/grant
GET /access-grants
GET /access-grants/active
POST /access-grants/{id}/revoke
GET /audit-logs
Structure principale
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
Contribution UI/UX V4

La V4 améliore notamment :

la lisibilité ;
l’ergonomie ;
la navigation ;
l’organisation des écrans ;
le responsive design ;
la cohérence visuelle entre les rôles ;
la documentation utilisateur.
Limites actuelles

Le projet utilise encore des comptes de démonstration définis dans le backend.

Pour une version de production, il faudrait notamment :

utiliser une base utilisateurs persistante ;
protéger davantage le stockage du token ;
configurer les URLs de l’API avec des variables d’environnement ;
ajouter une gestion centralisée des erreurs ;
compléter les tests automatisés du frontend ;
améliorer l’accessibilité.