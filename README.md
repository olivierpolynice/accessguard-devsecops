1. README.md
AccessGuard

AccessGuard est une application pédagogique de gestion et de gouvernance des accès internes pour l’entreprise fictive AsteriaTech.

Le projet permet de gérer :

l’authentification des utilisateurs ;
les rôles et autorisations RBAC ;
les demandes d’accès ;
la validation par un manager ;
l’attribution et la révocation des accès ;
les journaux d’audit ;
la supervision avec Prometheus et Grafana ;
l’administration des utilisateurs depuis la version V5.
Technologies utilisées
Backend
Python 3.12
FastAPI
SQLite
Pydantic
JWT
Passlib / bcrypt
Pytest
Frontend
HTML
CSS
JavaScript
DevOps et supervision
Docker
Docker Compose
GitHub Actions
Prometheus
Grafana
Lancer le projet
Prérequis

Installer les outils suivants :

Git
Docker Desktop
Docker Compose
1. Cloner le dépôt
git clone <URL_DU_DEPOT>
cd accessguard-devsecops
2. Créer le fichier d’environnement

Créer un fichier .env à la racine du projet si celui-ci n’existe pas.

Exemple :

SECRET_KEY=accessguard-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./data/accessguard.db

Ne pas utiliser cette clé secrète en production.

3. Démarrer les services
docker compose up --build

Pour lancer les services en arrière-plan :

docker compose up --build -d
4. Vérifier les conteneurs
docker compose ps
5. Accéder aux services
Service	Adresse
API AccessGuard	http://localhost:8000
Documentation Swagger	http://localhost:8000/docs
Documentation ReDoc	http://localhost:8000/redoc
Métriques Prometheus	http://localhost:8000/metrics
Prometheus	http://localhost:9090
Grafana	http://localhost:3000
Arrêter le projet
docker compose down

Pour supprimer également les volumes :

docker compose down -v

Attention : la suppression des volumes peut supprimer les données SQLite persistantes.

Comptes de test

Les comptes suivants sont créés automatiquement par le script de seed.

Rôle	Adresse email	Mot de passe
Employee	alice.employee@asteriatech.local	AccessGuard123!
Manager	marc.manager@asteriatech.local	AccessGuard123!
IT Admin	ines.itadmin@asteriatech.local	AccessGuard123!
Security Admin	paul.security@asteriatech.local	AccessGuard123!

Ces identifiants sont réservés à l’environnement pédagogique.

Authentification
Connexion
POST /auth/login

Exemple de requête :

{
  "email": "paul.security@asteriatech.local",
  "password": "AccessGuard123!"
}

La réponse contient un jeton JWT :

{
  "access_token": "<JWT>",
  "token_type": "bearer"
}

Dans Swagger, cliquer sur Authorize, puis saisir :

Bearer <JWT>
Routes principales
Santé et supervision
Méthode	Route	Description
GET	/health	Vérifie l’état de l’API
GET	/metrics	Expose les métriques Prometheus
Authentification
Méthode	Route	Description
POST	/auth/login	Authentifie un utilisateur
Ressources
Méthode	Route	Description
GET	/resources	Liste les ressources disponibles
Demandes d’accès
Méthode	Route	Description
POST	/access-requests	Crée une demande d’accès
GET	/access-requests	Liste les demandes
PATCH	/access-requests/{id}/manager-decision	Accepte ou refuse une demande
Attributions d’accès
Méthode	Route	Description
GET	/access-grants	Liste les accès attribués
POST	/access-requests/{id}/grant	Attribue un accès approuvé
PATCH	/access-grants/{id}/revoke	Révoque un accès
Audit
Méthode	Route	Description
GET	/audit-logs	Consulte les journaux d’audit
Routes d’administration des utilisateurs — V5

Toutes les routes /users sont réservées au rôle security_admin.

Méthode	Route	Description
GET	/users	Liste tous les utilisateurs
GET	/users/{user_id}	Consulte un utilisateur
POST	/users	Crée un utilisateur
PATCH	/users/{user_id}/role	Modifie le rôle d’un utilisateur
PATCH	/users/{user_id}/status	Active ou désactive un utilisateur

Les mots de passe ne sont jamais retournés par l’API.

Règles RBAC

AccessGuard applique un contrôle d’accès basé sur les rôles.

Action	Employee	Manager	IT Admin	Security Admin
Se connecter	Oui	Oui	Oui	Oui
Voir les ressources	Oui	Oui	Oui	Oui
Créer une demande d’accès	Oui	Non	Non	Non
Accepter ou refuser une demande	Non	Oui	Non	Non
Attribuer un accès	Non	Non	Oui	Non
Révoquer un accès	Non	Non	Oui	Non
Consulter les journaux d’audit	Non	Non	Non	Oui
Administrer les utilisateurs	Non	Non	Non	Oui
Codes d’erreur principaux
Code	Signification
200	Requête réussie
201	Ressource créée
401	Authentification absente ou invalide
403	Rôle non autorisé
404	Ressource introuvable
409	Conflit, par exemple adresse email déjà utilisée
422	Données de requête invalides
Tester le projet
Tests automatisés dans Docker
docker compose exec accessguard-api pytest -v
Tests locaux

Créer puis activer un environnement virtuel :

python -m venv .venv

Sous Windows PowerShell :

.\.venv\Scripts\Activate.ps1

Installer les dépendances :

pip install -r requirements.txt

Lancer les tests :

pytest -v

Lancer uniquement les tests liés aux utilisateurs :

pytest -v tests/test_users.py
Vérifier la qualité du code

Selon les outils présents dans le projet :

ruff check .
black --check .
bandit -r app
Scénario de démonstration V5
Se connecter avec le compte security_admin.
Récupérer le jeton JWT.
Appeler GET /users.
Créer un nouvel utilisateur avec POST /users.
Vérifier qu’une adresse email existante retourne 409.
Modifier le rôle de l’utilisateur.
Désactiver l’utilisateur.
Vérifier que l’utilisateur désactivé ne peut plus se connecter.
Réactiver l’utilisateur.
Vérifier les journaux et résultats des tests.
Captures disponibles

Les captures de validation disponibles comprennent notamment :

Capture	Description
02_v5_users_table_created.png	Création et structure de la table users
03_v5_login_sqlite_success.png	Connexion réussie avec un utilisateur SQLite
04_v5_inactive_user_denied.png	Refus de connexion pour un utilisateur désactivé
05_v5_security_users_admin.png	Administration des utilisateurs par le Security Admin

D’autres captures peuvent être ajoutées dans un dossier comme :

docs/screenshots/v5/
Limites restantes

La version actuelle présente encore plusieurs limites :

aucune fonctionnalité de réinitialisation de mot de passe ;
aucun mécanisme de renouvellement de jeton JWT ;
aucune authentification multifacteur ;
absence de suppression définitive d’utilisateur ;
interface graphique d’administration des utilisateurs encore limitée ou absente ;
secrets de démonstration non adaptés à un environnement de production ;
base SQLite adaptée à la démonstration, mais limitée pour un déploiement distribué ;
gestion des sessions et révocation des jetons non implémentées ;
couverture de tests à maintenir lors des prochaines évolutions ;
observabilité et alertes encore perfectibles ;
absence de gestion complète des migrations de base de données.
Avertissement

AccessGuard est un projet pédagogique.

Les comptes, mots de passe, secrets JWT et configurations fournis dans ce dépôt ne doivent pas être réutilisés dans un environnement réel.