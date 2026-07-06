# AccessGuard DevSecOps

API pédagogique de gestion et de gouvernance des accès internes pour l’entreprise fictive **AsteriaTech**.

AccessGuard met en œuvre un workflow de demande d’accès à une ressource interne, avec authentification JWT, contrôle d’accès basé sur les rôles (RBAC), journalisation des actions sensibles et tests automatisés.

> **État du projet : V2 — JWT/RBAC et contrôles de sécurité validés**

---

## Objectifs du projet

Le projet permet de démontrer les principes suivants :

- authentification par JWT ;
- contrôle d’accès par rôles (RBAC) ;
- gestion d’une demande d’accès de bout en bout ;
- validation par un manager ;
- attribution et révocation d’un accès par les rôles autorisés ;
- journalisation des actions sensibles ;
- tests automatisés avec Pytest ;
- intégration continue avec GitHub Actions.

---

## Workflow fonctionnel

1. Un **employee** s’authentifie et crée une demande d’accès à une ressource.
2. Un **manager** approuve ou refuse la demande.
3. Un **it_admin** attribue l’accès après approbation.
4. Un **it_admin** ou un **security_admin** peut révoquer un accès actif.
5. Les actions sensibles sont enregistrées dans les logs d’audit.
6. Les logs d’audit sont réservés aux rôles autorisés.

---

## Architecture du projet

```text
accessguard-devsecops/
├── .github/
│   └── workflows/
│       └── test.yml
├── app/
│   ├── auth.py
│   ├── dependencies.py
│   ├── main.py
│   ├── schemas.py
│   ├── security.py
│   └── seed.py
├── docs/
│   ├── screenshots/
│   │   └── rendu-07/
│   ├── V2_PLAN.md
│   └── V2_RBAC_MATRIX.md
├── tests/
│   ├── test_accessguard.py
│   ├── test_auth.py
│   └── test_security.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Technologies utilisées

| Domaine | Technologies |
|---|---|
| API | Python, FastAPI |
| Validation des données | Pydantic |
| Authentification | JWT / PyJWT |
| Hachage des mots de passe | bcrypt |
| Tests | Pytest, FastAPI TestClient |
| CI | GitHub Actions |
| Documentation API | Swagger / OpenAPI |

---

## Installation locale

### Prérequis

- Python 3.11 ou version compatible ;
- Git ;
- Visual Studio Code recommandé ;
- un environnement virtuel Python.

### 1. Cloner le dépôt

```powershell
git clone https://github.com/olivierpolynice/accessguard-devsecops.git
cd accessguard-devsecops
```

### 2. Créer et activer l’environnement virtuel

Sous PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt
```

Si le fichier `requirements.txt` est placé à la racine du dépôt, utilisez plutôt :

```powershell
python -m pip install -r requirements.txt
```

### 4. Lancer l’API

```powershell
python -m uvicorn app.main:app --reload
```

L’API est ensuite disponible sur :

```text
http://127.0.0.1:8000
```

La documentation Swagger est disponible sur :

```text
http://127.0.0.1:8000/docs
```

---

## Authentification JWT

La connexion est réalisée via :

```text
POST /auth/login
```

Exemple de body :

```json
{
  "email": "alice.employee@asteriatech.local",
  "password": "Employee123!"
}
```

La réponse contient :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "employee"
}
```

Le token est ensuite transmis dans l’en-tête HTTP :

```text
Authorization: Bearer <access_token>
```

Dans Swagger, utiliser le bouton **Authorize**, coller le token JWT, puis valider.

---

## Comptes de démonstration

> Ces comptes sont prévus uniquement pour l’environnement pédagogique local.

| Utilisateur | E-mail | Mot de passe | Rôle |
|---|---|---|---|
| Alice Employee | `alice.employee@asteriatech.local` | `Employee123!` | `employee` |
| Marc Manager | `marc.manager@asteriatech.local` | `Manager123!` | `manager` |
| Inès IT Admin | `ines.itadmin@asteriatech.local` | `Admin123!` | `it_admin` |
| Sam Security | `sam.security@asteriatech.local` | `Security123!` | `security_admin` |

---

## Matrice RBAC V2

| Endpoint / action | employee | manager | it_admin | security_admin |
|---|---:|---:|---:|---:|
| `POST /auth/login` | Oui | Oui | Oui | Oui |
| `GET /health` | Oui | Oui | Oui | Oui |
| `GET /resources` | Oui | Oui | Oui | Oui |
| `POST /access-requests` | Oui | Oui | Oui | Oui |
| `GET /access-requests` | Ses demandes | Oui | Oui | Oui |
| `GET /access-requests/{request_id}` | Ses demandes | Oui | Oui | Oui |
| `POST /access-requests/{request_id}/manager-decision` | Non | Oui | Non | Non |
| `POST /access-requests/{request_id}/grant` | Non | Non | Oui | Non |
| `GET /access-grants` | Ses accès | Non | Oui | Oui |
| `POST /access-grants/{grant_id}/revoke` | Non | Non | Oui | Oui |
| `GET /audit-logs` | Non | Non | Oui | Oui |

### Codes HTTP attendus

| Situation | Résultat attendu |
|---|---|
| Token absent | `401 Unauthorized` |
| Token invalide ou expiré | `401 Unauthorized` |
| Token valide avec rôle insuffisant | `403 Forbidden` |
| Token valide avec rôle autorisé | `200 OK` ou `201 Created` |
| Ressource ou objet introuvable après authentification | `404 Not Found` |
| Action incohérente avec l’état métier | `409 Conflict` |
| Données invalides | `422 Unprocessable Content` |

---

## Endpoints principaux

### Authentification

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login` | Connexion et génération d’un token JWT |

### Informations et ressources

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Informations de base de l’API |
| `GET` | `/health` | Vérification de disponibilité |
| `GET` | `/resources` | Liste des ressources actives |

### Demandes d’accès

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/access-requests` | Créer une demande d’accès |
| `GET` | `/access-requests` | Lister les demandes selon le rôle |
| `GET` | `/access-requests/{request_id}` | Consulter une demande |
| `POST` | `/access-requests/{request_id}/manager-decision` | Approuver ou refuser une demande |

### Accès attribués

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/access-requests/{request_id}/grant` | Attribuer un accès après approbation |
| `GET` | `/access-grants` | Lister les accès attribués |
| `POST` | `/access-grants/{grant_id}/revoke` | Révoquer un accès actif |

### Audit

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/audit-logs` | Consulter les logs d’audit, réservé aux administrateurs |

---

## Exemples de scénarios V2

### 1. Tentative sans JWT

```text
GET /audit-logs
```

Résultat :

```text
401 Unauthorized
```

### 2. JWT valide mais rôle insuffisant

Un utilisateur `employee` tente d’attribuer un accès :

```text
POST /access-requests/1/grant
```

Résultat :

```text
403 Forbidden
```

### 3. JWT valide et rôle autorisé

Un utilisateur `it_admin` consulte les logs :

```text
GET /audit-logs
```

Résultat :

```text
200 OK
```

### 4. Workflow complet

1. Connexion `employee`.
2. Création d’une demande d’accès.
3. Connexion `manager`.
4. Approbation de la demande.
5. Connexion `it_admin`.
6. Attribution de l’accès.
7. Révocation éventuelle par `it_admin` ou `security_admin`.
8. Consultation des logs d’audit par un rôle autorisé.

---

## Tests automatisés

Exécuter les tests depuis la racine du projet :

```powershell
python -m pytest -v
```

Résultat de validation V2 :

```text
31 passed
```

Les tests couvrent notamment :

- génération de token JWT ;
- authentification ;
- accès sans token (`401`) ;
- accès avec mauvais rôle (`403`) ;
- création de demandes ;
- validation manager ;
- attribution d’accès ;
- révocation d’accès ;
- logs d’audit ;
- erreurs `404`, `409` et `422`.

> Un avertissement lié à `TestClient` / `httpx` peut apparaître. Il n’empêche pas l’exécution ni la réussite des tests.

---

## Intégration continue

Le dépôt contient un workflow GitHub Actions qui exécute les tests automatiquement :

- à chaque `push` sur `main` ;
- à chaque `push` sur une branche `feature/**` ;
- à chaque Pull Request vers `main`.

Avant toute fusion dans `main`, vérifier :

1. que les tests locaux passent ;
2. que les checks GitHub Actions sont verts ;
3. que la Pull Request ne contient aucun secret ;
4. que la documentation et les captures sont ajoutées si nécessaire.

---

## Preuves et captures V2

Les captures de validation sont stockées dans :

```text
docs/screenshots/rendu-07/
```

Exemples de preuves attendues :

| Capture | Preuve |
|---|---|
| `Capture-V2-02-Tests-automatises-JWT-RBAC-reussis.png` | Tests Pytest réussis |
| `Capture-V2-03-Audit-logs-sans-JWT-401.png` | Audit refusé sans JWT |
| `Capture-V2-04-Audit-logs-role-employee-403.png` | Audit refusé pour le rôle employee |
| `Capture-V2-05-Audit-logs-it-admin-200.png` | Audit autorisé pour it_admin |
| `Capture-V2-06-Grant-sans-JWT-401.png` | Attribution refusée sans JWT |
| `Capture-V2-07-Grant-role-employee-403.png` | Attribution refusée pour employee |
| `Capture-V2-08-Creation-demande-access-employee-201.png` | Création d’une demande |
| `Capture-V2-09-Decision-manager-approved-200.png` | Approbation manager |
| `Capture-V2-10-Attribution-acces-it-admin-201.png` | Attribution par it_admin |
| `Capture-V2-11-Revocation-acces-it-admin-200.png` | Révocation d’un accès |
| `Capture-V2-12-Audit-logs-workflow-200.png` | Consultation des logs après le workflow |

---

## Sécurité

Les règles de sécurité appliquées dans la V2 sont les suivantes :

- aucune route sensible ne doit être accessible sans token JWT ;
- les rôles sont extraits depuis le token, pas depuis le body de la requête ;
- les actions sensibles sont contrôlées avec RBAC ;
- les opérations sensibles génèrent une trace d’audit ;
- les mots de passe sont hachés avec bcrypt ;
- les secrets sont lus depuis l’environnement avec une valeur locale de démonstration ;
- aucun token JWT complet ne doit être enregistré dans les logs ;
- les modifications passent par des branches et Pull Requests.

---

## Limites actuelles

Cette version reste une API pédagogique locale :

- les données sont conservées en mémoire ;
- un redémarrage de l’API réinitialise les demandes, accès et audits ;
- aucune base de données persistante n’est encore utilisée ;
- aucune interface front-end n’est implémentée ;
- aucun déploiement cloud n’est inclus dans cette V2.

---

## Évolutions possibles — V3

Les améliorations suivantes pourront être ajoutées dans une V3 :

- persistance SQLite ou PostgreSQL ;
- Dockerfile et Docker Compose ;
- gestion de migrations ;
- dashboard Prometheus / Grafana ;
- journalisation structurée ;
- gestion de secrets via Vault ou variables CI ;
- scan de sécurité des dépendances ;
- déploiement cloud ;
- interface front-end ;
- intégration LDAP, Active Directory ou Azure Entra ID.

---

## Auteur

**Olivier Polynice**  
Projet pédagogique Master Réseaux, Cybersécurité & Cloud.
