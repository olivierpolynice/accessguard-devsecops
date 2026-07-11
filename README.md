# AccessGuard

AccessGuard est une application pédagogique de gestion et de gouvernance des accès internes pour l’entreprise fictive **AsteriaTech**.

L’application permet de simuler le cycle complet d’une demande d’accès :

1. un employé crée une demande ;
2. un manager approuve ou refuse la demande ;
3. un administrateur IT attribue techniquement l’accès ;
4. un administrateur sécurité consulte et contrôle les opérations.

---

## Objectifs du projet

AccessGuard permet de mettre en pratique plusieurs notions :

- authentification sécurisée ;
- gestion des rôles ;
- contrôle d’accès basé sur les rôles, ou RBAC ;
- création et validation des demandes d’accès ;
- attribution et révocation des accès ;
- journalisation des actions ;
- séparation des responsabilités ;
- gouvernance des identités et des accès.

---

## Technologies utilisées

### Backend

- Python
- FastAPI
- Pydantic
- JWT
- Uvicorn

### Frontend

- React
- Vite
- JavaScript
- CSS
- API Fetch

### Outils

- Visual Studio Code
- Git
- GitHub
- Swagger UI

---

## Structure générale

```text
AccessGuard/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── security.py
│   │   ├── schemas.py
│   │   └── seed.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   └── package.json
│
└── README.md
La structure exacte peut évoluer au cours du projet.

Rôles disponibles

L’application contient quatre rôles principaux.

Employee

L’employé peut :

se connecter ;
consulter les ressources disponibles ;
créer une demande d’accès ;
renseigner une justification ;
sélectionner une période ;
consulter le statut de ses demandes ;
consulter ses accès attribués.
Manager

Le manager peut :

consulter les demandes en attente ;
approuver une demande ;
refuser une demande ;
ajouter un commentaire de décision ;
consulter les demandes déjà traitées.
IT Admin

L’administrateur IT peut :

consulter les demandes approuvées ;
attribuer techniquement un accès ;
ajouter un commentaire d’attribution ;
consulter les accès déjà attribués ;
révoquer un accès lorsque cette fonction est disponible.
Security Admin

L’administrateur sécurité peut :

consulter les demandes ;
consulter les accès attribués ;
consulter les journaux d’audit ;
contrôler les actions réalisées dans l’application ;
vérifier la cohérence des autorisations.
Comptes de démonstration

Ces comptes sont prévus uniquement pour l’environnement pédagogique local.

Tous les comptes utilisent le même mot de passe de démonstration :

AccessGuard123!
Utilisateur	Adresse e-mail	Mot de passe	Rôle
Alice Employee	alice.employee@asteriatech.local	AccessGuard123!	employee
Marc Manager	marc.manager@asteriatech.local	AccessGuard123!	manager
Inès IT Admin	ines.itadmin@asteriatech.local	AccessGuard123!	it_admin
Paul Security	paul.security@asteriatech.local	AccessGuard123!	security_admin

Le mot de passe est sensible à la casse. Il faut saisir exactement :

AccessGuard123!
Configuration des comptes dans le backend

Dans le backend, le mot de passe commun est défini avec une constante :

from typing import Final

DEMO_PASSWORD: Final[str] = "AccessGuard123!"

Les comptes utilisent ensuite le mot de passe haché :

DEMO_USERS: Final[dict[str, dict[str, str]]] = {
    "alice.employee@asteriatech.local": {
        "email": "alice.employee@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "employee",
    },
    "marc.manager@asteriatech.local": {
        "email": "marc.manager@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "manager",
    },
    "ines.itadmin@asteriatech.local": {
        "email": "ines.itadmin@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "it_admin",
    },
    "paul.security@asteriatech.local": {
        "email": "paul.security@asteriatech.local",
        "password_hash": hash_password(DEMO_PASSWORD),
        "role": "security_admin",
    },
}
Installation du backend

Ouvrir un terminal dans le dossier du backend :

cd backend

Créer un environnement virtuel :

python -m venv .venv

Activer l’environnement virtuel sous Windows :

.\.venv\Scripts\Activate.ps1

Installer les dépendances :

pip install -r requirements.txt

Démarrer le serveur FastAPI :

uvicorn app.main:app --reload

Le backend est normalement accessible à l’adresse suivante :

http://127.0.0.1:8000

La documentation Swagger est accessible ici :

http://127.0.0.1:8000/docs
Installation du frontend

Ouvrir un deuxième terminal :

cd frontend

Installer les dépendances :

npm install

Démarrer l’application React :

npm run dev

Le frontend est normalement accessible à l’adresse suivante :

http://localhost:5173
Test de l’authentification avec Swagger

Ouvrir :

http://127.0.0.1:8000/docs

Sélectionner la route :

POST /auth/login

Cliquer sur Try it out puis utiliser, par exemple, le compte IT Admin :

{
  "email": "ines.itadmin@asteriatech.local",
  "password": "AccessGuard123!"
}

Une réponse avec le code 200 indique que l’authentification fonctionne.

Une réponse 401 Unauthorized indique que :

l’adresse e-mail est incorrecte ;
le mot de passe est incorrect ;
le compte n’est pas présent dans DEMO_USERS ;
le backend n’a pas été redémarré après une modification.
Workflow d’une demande d’accès
Étape 1 — Création de la demande

Alice se connecte avec le rôle employee.

Elle sélectionne une ressource, indique une justification et choisit une période.

La demande est créée avec un statut similaire à :

PENDING
Étape 2 — Décision du manager

Marc se connecte avec le rôle manager.

Il consulte la demande puis peut :

l’approuver ;
la refuser ;
ajouter un commentaire.

Une demande approuvée reçoit le statut :

APPROVED
Étape 3 — Attribution par l’IT

Inès se connecte avec le rôle it_admin.

Elle consulte les demandes approuvées, ajoute un commentaire et clique sur :

Attribuer l’accès

L’accès apparaît ensuite dans la section :

Accès attribués
Étape 4 — Contrôle de sécurité

Paul se connecte avec le rôle security_admin.

Il peut consulter les opérations et les journaux d’audit afin de vérifier :

qui a demandé l’accès ;
qui a approuvé la demande ;
qui a attribué l’accès ;
à quelle date l’action a été réalisée ;
quelle ressource a été concernée.
Exemples de ressources

Les ressources peuvent notamment représenter :

un VPN d’entreprise ;
une base de données ;
un dépôt Git ;
une application interne ;
un espace documentaire ;
une console cloud ;
un serveur d’administration.

Exemple :

VPN Entreprise
Statuts possibles

Selon l’implémentation du projet, une demande peut utiliser les statuts suivants :

PENDING
APPROVED
REJECTED
GRANTED
REVOKED

Signification :

PENDING : demande en attente de décision ;
APPROVED : demande approuvée par le manager ;
REJECTED : demande refusée ;
GRANTED : accès attribué par l’administrateur IT ;
REVOKED : accès retiré.
Sécurité

Le projet utilise plusieurs mécanismes de sécurité :

hachage des mots de passe ;
authentification par jeton JWT ;
contrôle des rôles ;
vérification des autorisations ;
séparation des responsabilités ;
validation des données avec Pydantic ;
journalisation des opérations.

Le mot de passe commun AccessGuard123! est utilisé uniquement pour simplifier les démonstrations locales.

Il ne doit jamais être utilisé dans un environnement de production.

Dans une version de production, il faudrait notamment :

utiliser une base de données ;
utiliser un secret JWT stocké dans une variable d’environnement ;
imposer des mots de passe individuels ;
ajouter une politique de complexité ;
activer une authentification multifacteur ;
limiter les tentatives de connexion ;
utiliser HTTPS ;
gérer l’expiration et le renouvellement des jetons ;
protéger les journaux d’audit ;
mettre en place une gestion des secrets.
Vérification des rôles

Après la connexion, l’interface affiche l’utilisateur et son rôle.

Exemple pour l’administrateur IT :

Utilisateur : ines.itadmin@asteriatech.local
Rôle : it_admin

Exemple pour le manager :

Utilisateur : marc.manager@asteriatech.local
Rôle : manager
Résolution des problèmes
Erreur 401 lors de la connexion

Vérifier que le mot de passe utilisé est :

AccessGuard123!

Vérifier également que le compte existe dans DEMO_USERS.

Redémarrer le backend :

Ctrl + C
uvicorn app.main:app --reload
Le frontend ne contacte pas le backend

Vérifier que le backend fonctionne sur :

http://127.0.0.1:8000

Vérifier que l’URL de connexion utilisée dans React est correcte :

http://127.0.0.1:8000/auth/login
Erreur CORS

Vérifier que FastAPI autorise le frontend :

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Les modifications ne sont pas prises en compte

Arrêter puis relancer le backend et le frontend.

Backend :

Ctrl + C
uvicorn app.main:app --reload

Frontend :

Ctrl + C
npm run dev
Limites actuelles

Cette version est destinée à une démonstration pédagogique.

Certaines données peuvent être conservées uniquement en mémoire. Elles peuvent donc disparaître lors du redémarrage du backend.

Les comptes de démonstration utilisent également un mot de passe commun afin de faciliter les tests.

Améliorations prévues

Les prochaines versions pourront inclure :

une base de données PostgreSQL ;
une interface graphique améliorée ;
un tableau de bord par rôle ;
des filtres et une recherche ;
la révocation des accès ;
l’expiration automatique des autorisations ;
des notifications ;
un historique complet ;
des métriques Prometheus ;
des tableaux de bord Grafana ;
une conteneurisation Docker ;
un déploiement automatisé ;
Terraform ;
une intégration continue avec GitHub Actions ;
des tests automatisés ;
une gestion centralisée des secrets.
Avertissement

AccessGuard est un projet pédagogique.

Les utilisateurs, ressources, mots de passe et données présentés dans l’application sont fictifs.

Aucun compte de démonstration ne doit être utilisé sur un service réel.

Auteur

Projet AccessGuard réalisé dans le cadre d’un projet pédagogique consacré à la cybersécurité, au cloud, au DevOps et à la gouvernance des accès.


La correction principale est que les quatre comptes utilisent désormais tous :

```text
AccessGuard123!

et que le compte sécurité correspond au code actuel :

paul.security@asteriatech.local