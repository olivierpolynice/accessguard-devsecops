# AccessGuard

AccessGuard est une application de gestion sécurisée des demandes et des autorisations d’accès.

Elle permet :

- aux employés de demander un accès à une ressource ;
- aux managers d’approuver ou de refuser les demandes ;
- aux administrateurs IT d’attribuer et de révoquer les accès ;
- aux administrateurs sécurité de gérer les utilisateurs, consulter l’audit et accéder au monitoring.

## Architecture

Le projet comprend les composants suivants :

- une API FastAPI ;
- une interface React avec Vite ;
- une base de données SQLite ;
- Prometheus pour la collecte des métriques ;
- Grafana pour la visualisation ;
- Docker Compose pour le lancement des services.

## Prérequis

Avant de démarrer le projet, installer :

- Docker Desktop ;
- Docker Compose ;
- Git ;
- Node.js et npm pour le développement du frontend ;
- Python 3 pour le développement local du backend.

## Lancement avec Docker

Depuis la racine du projet, exécuter :

```bash
docker compose up --build -d
```

Vérifier l’état des services :

```bash
docker compose ps
```

Afficher les journaux de l’API :

```bash
docker compose logs accessguard-api --tail=100
```

Suivre les journaux en temps réel :

```bash
docker compose logs -f accessguard-api
```

Arrêter les services :

```bash
docker compose down
```

Reconstruire les conteneurs après une modification :

```bash
docker compose up --build -d
```

## URL des services

| Service | URL |
|---|---|
| Frontend AccessGuard | http://localhost:5173 |
| API FastAPI | http://localhost:8000 |
| Documentation Swagger | http://localhost:8000/docs |
| Documentation ReDoc | http://localhost:8000/redoc |
| Vérification de l’API | http://localhost:8000/health |
| Métriques Prometheus de l’API | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Certaines URL peuvent changer selon la configuration définie dans `docker-compose.yml`.

## Comptes de démonstration

| Utilisateur | Adresse e-mail | Rôle |
|---|---|---|
| Alice | `alice.employee@asteriatech.local` | `employee` |
| Marc | `marc.manager@asteriatech.local` | `manager` |
| Inès | `ines.itadmin@asteriatech.local` | `it_admin` |
| Paul | `paul.security@asteriatech.local` | `security_admin` |

Les mots de passe de démonstration sont définis dans le fichier :

```text
app/seed.py
```

Les mots de passe et les valeurs `password_hash` ne doivent jamais être ajoutés dans ce README, affichés dans le frontend ou enregistrés dans Git.

## Authentification

La connexion s’effectue avec :

```http
POST /auth/login
```

Exemple de corps JSON :

```json
{
  "email": "alice.employee@asteriatech.local",
  "password": "mot-de-passe"
}
```

L’API retourne un jeton JWT. Le frontend l’envoie ensuite dans les requêtes protégées :

```http
Authorization: Bearer <access_token>
```

## Routes frontend

| Route | Utilisateur autorisé | Description |
|---|---|---|
| `/` | Tous | Page de connexion |
| `/dashboard` | Utilisateur connecté | Tableau de bord adapté au rôle |
| `/resources` | `employee` | Catalogue des ressources |
| `/requests` | `employee` | Création et suivi des demandes |
| `/manager-requests` | `manager` | Approbation et refus des demandes |
| `/grants` | `it_admin` | Attribution et révocation des accès |
| `/users` | `security_admin` | Administration des utilisateurs |
| `/audit` | `security_admin` | Consultation du journal d’audit |
| `/monitoring` | `security_admin` | Accès aux outils de supervision |

## Matrice RBAC

| Fonctionnalité | Employee | Manager | IT Admin | Security Admin |
|---|:---:|:---:|:---:|:---:|
| Consulter les ressources | Oui | Non | Non | Non |
| Créer une demande d’accès | Oui | Non | Non | Non |
| Consulter ses demandes | Oui | Non | Non | Non |
| Consulter les demandes à valider | Non | Oui | Non | Non |
| Approuver une demande | Non | Oui | Non | Non |
| Refuser une demande | Non | Oui | Non | Non |
| Attribuer un accès approuvé | Non | Non | Oui | Non |
| Consulter les accès attribués | Non | Non | Oui | Non |
| Révoquer un accès | Non | Non | Oui | Non |
| Consulter les utilisateurs | Non | Non | Non | Oui |
| Créer un utilisateur | Non | Non | Non | Oui |
| Modifier un rôle | Non | Non | Non | Oui |
| Activer ou désactiver un utilisateur | Non | Non | Non | Oui |
| Consulter le journal d’audit | Non | Non | Non | Oui |
| Accéder au monitoring | Non | Non | Non | Oui |

Les autorisations doivent être vérifiées par le backend. Le masquage d’une page ou d’un bouton dans le frontend ne remplace pas un contrôle RBAC côté API.

## Workflow d’une demande d’accès

1. L’employé se connecte.
2. Il consulte les ressources disponibles.
3. Il crée une demande en ajoutant une justification.
4. La demande reçoit le statut `PENDING_MANAGER`.
5. Le manager ajoute un commentaire.
6. Il approuve ou refuse la demande.
7. Une demande approuvée reçoit le statut `APPROVED`.
8. L’administrateur IT attribue l’accès.
9. L’accès attribué reçoit le statut `ACTIVE` ou `GRANTED`, selon l’objet renvoyé par l’API.
10. L’administrateur IT peut ensuite révoquer l’accès avec une justification.
11. L’accès révoqué reçoit le statut `REVOKED`.

Le backend de décision du manager peut utiliser la valeur `REFUSED`. Le frontend doit néanmoins afficher un libellé français cohérent, comme « Refusée ».

## Routes principales de l’API

### Authentification

```http
POST /auth/login
```

### Ressources

```http
GET /resources
GET /resources/{id}
```

### Demandes d’accès

```http
GET  /access-requests
POST /access-requests
GET  /access-requests/{id}
```

Les routes exactes de décision du manager doivent être consultées dans Swagger :

```text
http://localhost:8000/docs
```

La décision doit contenir une valeur acceptée par le backend et un commentaire d’au moins cinq caractères.

Exemple :

```json
{
  "decision": "APPROVED",
  "comment": "Demande conforme au besoin métier."
}
```

Exemple de refus :

```json
{
  "decision": "REFUSED",
  "comment": "La ressource ne correspond pas au besoin indiqué."
}
```

### Attribution et révocation

Lors d’une attribution, l’API attend notamment un commentaire :

```json
{
  "comment": "Accès attribué après validation du manager."
}
```

Lors d’une révocation, l’API attend un motif :

```json
{
  "reason": "Le collaborateur ne travaille plus sur ce projet."
}
```

Consulter Swagger pour vérifier le chemin exact des routes d’attribution et de révocation.

## Routes V5 des utilisateurs

Ces routes sont réservées au rôle `security_admin`.

### Lister les utilisateurs

```http
GET /users
```

### Consulter un utilisateur

```http
GET /users/{id}
```

### Créer un utilisateur

```http
POST /users
```

Exemple :

```json
{
  "email": "nouveau.employee@asteriatech.local",
  "password": "MotDePasseSecurise",
  "role": "employee",
  "is_active": true
}
```

Le champ `is_active` doit être envoyé uniquement s’il est accepté par le schéma du backend.

### Modifier le rôle

```http
PATCH /users/{id}/role
```

Exemple :

```json
{
  "role": "manager"
}
```

### Modifier le statut

```http
PATCH /users/{id}/status
```

Exemple de désactivation :

```json
{
  "is_active": false
}
```

Une confirmation utilisateur est obligatoire avant une désactivation.

Valeurs de rôle utilisées :

```text
employee
manager
it_admin
security_admin
```

L’API ne doit jamais retourner le mot de passe ni le `password_hash`.

## États et badges

| État backend | Affichage conseillé | Couleur |
|---|---|---|
| `PENDING_MANAGER` | En attente | Orange |
| `APPROVED` | Approuvée | Bleu |
| `REFUSED` ou `REJECTED` | Refusée | Rouge |
| `GRANTED` | Attribué | Vert |
| `ACTIVE` | Actif | Vert |
| `REVOKED` | Révoqué | Rouge foncé ou gris |

Le frontend doit utiliser en priorité les valeurs réellement renvoyées par l’API.

## Messages et confirmations

Une confirmation est obligatoire avant :

- la révocation d’un accès ;
- la désactivation d’un utilisateur ;
- un changement de rôle sensible, si nécessaire.

Exemple de confirmation :

> Voulez-vous vraiment révoquer cet accès ? Cette action prendra effet immédiatement.

Après une action réussie, le frontend affiche un message temporaire ou pouvant être fermé :

- « Demande envoyée avec succès. »
- « Demande approuvée. »
- « Accès attribué avec succès. »
- « Accès révoqué. »
- « Utilisateur créé. »
- « Rôle mis à jour. »
- « Utilisateur désactivé. »

## Erreurs HTTP

| Code | Message affiché |
|---:|---|
| `400` | La demande envoyée est incorrecte. |
| `401` | Votre session a expiré. Veuillez vous reconnecter. |
| `403` | Vous n’avez pas l’autorisation nécessaire. |
| `404` | L’élément demandé est introuvable. |
| `409` | Cet élément existe déjà. |
| `422` | Certaines informations sont invalides. |
| `500` | Une erreur interne est survenue. |

Les erreurs doivent être affichées dans l’interface. Elles ne doivent pas apparaître uniquement dans la console du navigateur.

## Développement du frontend

Se placer dans le dossier frontend :

```bash
cd frontend
```

Installer les dépendances :

```bash
npm install
```

Démarrer le serveur de développement :

```bash
npm run dev
```

Vérifier le code :

```bash
npm run lint
```

Construire la version de production :

```bash
npm run build
```

## Développement du backend

Créer et activer un environnement virtuel, puis installer les dépendances.

Sous PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Démarrer l’API depuis la racine :

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Si les dépendances du backend sont uniquement déclarées dans `app/requirements.txt`, utiliser :

```bash
pip install -r app/requirements.txt
```

## Commandes de test

### Tests Python

Depuis la racine du projet :

```bash
pytest
```

Affichage détaillé :

```bash
pytest -v
```

Arrêter au premier échec :

```bash
pytest -x
```

Tester un fichier précis :

```bash
pytest tests/nom_du_test.py -v
```

### Qualité Python

```bash
flake8 app tests
```

### Vérification du frontend

```bash
cd frontend
npm run lint
npm run build
```

### Vérification Docker

```bash
docker compose config
docker compose ps
docker compose logs accessguard-api --tail=100
```

### Vérification manuelle de l’API

```bash
curl http://localhost:8000/health
```

Réponse attendue :

```json
{
  "status": "ok"
}
```

## Monitoring

Prometheus collecte les métriques exposées par l’API :

```text
http://localhost:8000/metrics
```

Interfaces disponibles :

- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000

Les identifiants Grafana dépendent de la configuration du projet et des variables d’environnement.

## Sécurité

Le projet applique notamment les règles suivantes :

- authentification par JWT ;
- autorisation RBAC côté backend ;
- mots de passe hachés ;
- mots de passe et `password_hash` jamais affichés ;
- journalisation des actions sensibles ;
- confirmation avant une action destructive ;
- justification obligatoire pour les décisions et révocations ;
- traduction des erreurs HTTP dans l’interface ;
- secrets stockés hors du code source.

Ne jamais versionner :

- les jetons JWT ;
- les mots de passe ;
- les fichiers `.env` contenant des secrets ;
- les clés privées ;
- les valeurs `password_hash`.

## Guide utilisateur V5

Le guide utilisateur complet est disponible ici :

[Consulter le guide utilisateur V5](docs/V5_USER_GUIDE.md)

Les captures d’écran du guide sont rangées dans :

```text
docs/screenshots/v5/
```

## Structure principale

```text
accessguard-devsecops/
├── app/                         # API FastAPI
├── docs/
│   ├── V5_USER_GUIDE.md
│   └── screenshots/
│       └── v5/
├── frontend/                    # Application React/Vite
├── infrastructure/
├── monitoring/
├── security/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
└── README.md
```