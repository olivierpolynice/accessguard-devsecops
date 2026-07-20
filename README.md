# Projet DevOps - E4 ESTIAM - 2025/2026 - Groupe 22

# AccessGuard — Plateforme DevSecOps de gouvernance des accès

AccessGuard est une application de gestion sécurisée des demandes et des autorisations d’accès dans une entreprise fictive appelée **AsteriaTech**.

Nous avons conçu ce projet pour répondre à un besoin réel en entreprise : contrôler les accès aux ressources sensibles, tracer les décisions, appliquer des rôles clairs et superviser l’état technique de l’application.

L’objectif n’est pas seulement de créer une API ou une interface. Nous avons construit progressivement une plateforme complète, versionnée de **V1 à V5**, avec backend, frontend, base de données, authentification, audit, monitoring, tests automatisés et CI/CD.

---

## Membres du Groupe 22

| N° | Nom et Prénom | Rôle dans le projet |
|---:|---|---|
| 1 | Olivier POLYNICE | Chef de projet et lead technique |
| 2 | Yazid EL-BAK | Scrum Master et référent Backend / DevOps |
| 3 | Irina LETSARA | Référente Tests, CI/CD, Qualité et Sécurité |
| 4 | Élodie IPARRAGUIRRE | Responsable UI/UX et documentation fonctionnelle |

---

## Stack technique utilisée

![Python 3.12](https://img.shields.io/badge/PYTHON_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/REACT-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/VITE-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLITE-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

![Docker](https://img.shields.io/badge/DOCKER-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/DOCKER_COMPOSE-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub](https://img.shields.io/badge/GITHUB-181717?style=for-the-badge&logo=github&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GITHUB_ACTIONS-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

![Prometheus](https://img.shields.io/badge/PROMETHEUS-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/GRAFANA-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Pytest](https://img.shields.io/badge/PYTEST-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Flake8](https://img.shields.io/badge/FLAKE8-3776AB?style=for-the-badge&logo=python&logoColor=white)

![Gitleaks](https://img.shields.io/badge/GITLEAKS-8A2BE2?style=for-the-badge&logo=git&logoColor=white)
![pip-audit](https://img.shields.io/badge/PIP_AUDIT-FFD43B?style=for-the-badge&logo=python&logoColor=black)
![npm audit](https://img.shields.io/badge/NPM_AUDIT-CB3837?style=for-the-badge&logo=npm&logoColor=white)
![Swagger](https://img.shields.io/badge/SWAGGER-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

---

# Concept du projet

AccessGuard est une application web DevSecOps dédiée à la gouvernance des accès.

Dans une entreprise, un utilisateur ne devrait pas recevoir un accès sensible sans validation, sans justification ou sans traçabilité. AccessGuard simule ce processus en mettant en place un workflow complet :

```text
Demande d’accès → Validation manager → Attribution IT → Révocation → Audit → Monitoring

L’application permet :

aux employés de demander un accès à une ressource ;
aux managers d’approuver ou de refuser les demandes ;
aux administrateurs IT d’attribuer ou de révoquer les accès ;
aux administrateurs sécurité de consulter l’audit, les utilisateurs et le monitoring.

AccessGuard est donc à la fois :

une application métier ;
une API sécurisée ;
une interface utilisateur ;
un projet DevOps ;
un projet DevSecOps ;
un support de démonstration technique.
Contexte initial : de CyberPulse à AccessGuard

Au début du projet, nous avions travaillé sur une première orientation appelée CyberPulse.

CyberPulse était centré sur la cybersécurité, l’audit, la supervision et la sensibilisation aux risques numériques. Cette première réflexion nous a permis d’identifier plusieurs thèmes importants :

la sécurité des accès ;
la traçabilité ;
la supervision ;
la gestion des risques ;
la nécessité de preuves techniques ;
la logique DevSecOps.

Cependant, nous avons ensuite décidé de recentrer le projet sur une solution plus concrète, plus démontrable et plus directement exploitable dans un contexte DevOps.

Ce recentrage a donné naissance à AccessGuard.

AccessGuard conserve l’esprit cybersécurité de CyberPulse, mais avec un périmètre plus précis : la gestion des demandes d’accès internes dans une entreprise.

Ce choix nous a permis d’obtenir un projet plus cohérent, plus testable, plus facile à présenter et plus aligné avec les attentes du projet pédagogique.

Fonctionnalités principales
Fonctionnalité	Description
Authentification	Connexion sécurisée avec token JWT
Gestion des rôles	Séparation des droits selon employee, manager, it_admin et security_admin
Ressources	Consultation des ressources internes disponibles
Demandes d’accès	Création et suivi des demandes par les employés
Validation manager	Approbation ou refus d’une demande
Attribution IT	Attribution d’un accès après validation
Révocation	Suppression d’un accès existant
Audit	Journalisation des actions sensibles
Gestion utilisateurs	Création, modification de rôle, activation et désactivation
Monitoring	Exposition de métriques Prometheus
Grafana	Visualisation des métriques techniques
CI/CD	Tests et contrôles automatiques avec GitHub Actions
Sécurité	Hash des mots de passe, RBAC, audit, scan de secrets
Rôles applicatifs
Rôle	Description	Droits principaux
employee	Employé demandeur	Créer et consulter ses demandes d’accès
manager	Responsable hiérarchique	Approuver ou refuser les demandes
it_admin	Administrateur IT	Attribuer et révoquer les accès
security_admin	Administrateur sécurité	Gérer les utilisateurs, consulter l’audit et le monitoring
Workflow métier

Le workflow principal d’AccessGuard repose sur une séparation claire des responsabilités.

1. L’employé consulte les ressources disponibles.
2. Il crée une demande d’accès.
3. Le manager analyse la demande.
4. Le manager approuve ou refuse la demande.
5. Si la demande est approuvée, l’administrateur IT attribue l’accès.
6. L’accès peut ensuite être révoqué.
7. Les actions importantes sont enregistrées dans l’audit.
8. Les métriques techniques sont exposées pour Prometheus et Grafana.

Cette logique permet d’éviter qu’un accès soit accordé sans contrôle.

Architecture générale
Frontend React / Vite
        ↓
Backend FastAPI
        ↓
Base de données SQLite
        ↓
Audit logs / Métriques
        ↓
Prometheus / Grafana
        ↓
GitHub Actions / Tests / Sécurité
Structure du dépôt
accessguard-devsecops/
│
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── metrics.py
│   └── permissions.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── tests/
│   ├── test_auth.py
│   ├── test_access_requests.py
│   ├── test_users.py
│   ├── test_metrics.py
│   └── test_business_metrics.py
│
├── docs/
│   ├── screenshots/
│   ├── V5_OBSERVABILITY.md
│   ├── V5_SPRINT_SUMMARY.md
│   └── ...
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
Progression du projet
V1 — Socle API et workflow métier

La première version a posé les bases du projet.

Nous avons commencé par construire une API FastAPI permettant de représenter le workflow métier principal :

ressources internes ;
demandes d’accès ;
validation manager ;
attribution IT ;
révocation ;
audit.

Cette V1 a permis de valider la logique centrale du projet avant d’ajouter la sécurité, la persistance et l’interface.

Objectifs de la V1 :

créer un backend fonctionnel ;
définir les principales entités métier ;
vérifier le cycle de vie d’une demande ;
préparer les premiers tests ;
structurer le projet.
V2 — Authentification et RBAC

La V2 a ajouté la sécurité applicative.

Nous avons intégré :

une route de connexion ;
des tokens JWT ;
une gestion des rôles ;
des permissions selon le profil utilisateur ;
les erreurs 401 et 403 ;
la protection des routes sensibles.

Cette version a introduit le principe RBAC : Role-Based Access Control.

Les utilisateurs ne peuvent accéder qu’aux fonctionnalités correspondant à leur rôle.

Exemples :

un employee peut créer une demande ;
un manager peut valider ou refuser ;
un it_admin peut attribuer ou révoquer ;
un security_admin peut consulter les utilisateurs, l’audit et le monitoring.
V3 — Persistance et base SQLite

La V3 a renforcé le projet avec la persistance des données.

Nous avons utilisé SQLite pour conserver les données de l’application.

Cette étape a permis de ne plus dépendre uniquement de données temporaires en mémoire.

La V3 a amélioré :

la stabilité du backend ;
la conservation des données ;
la structure des modèles ;
la fiabilité des tests ;
la préparation du projet pour Docker.

Cette version a également permis de mieux organiser les données liées aux demandes, aux ressources, aux accès et aux journaux d’audit.

V4 — Frontend, Docker et monitoring

La V4 a transformé AccessGuard en application complète.

Nous avons ajouté une interface frontend avec React et Vite.

Le frontend permet aux utilisateurs de se connecter et d’accéder à des pages adaptées à leur rôle.

Pages principales :

login ;
dashboard ;
ressources ;
demandes ;
validation manager ;
accès attribués ;
audit ;
utilisateurs ;
monitoring.

Nous avons également intégré Docker et Docker Compose pour faciliter le lancement du projet.

La supervision a été ajoutée avec :

Prometheus ;
endpoint /metrics ;
Grafana ;
vérification de santé avec /health.

Cette version a rendu le projet plus démontrable et plus proche d’une application réelle.

V5 — Stabilisation finale, qualité et DevSecOps

La V5 correspond à la phase de consolidation du projet.

Nous avons stabilisé les fonctionnalités existantes et renforcé la qualité globale.

Travaux réalisés en V5 :

amélioration de la gestion des utilisateurs ;
routes utilisateurs ;
gestion des rôles ;
activation et désactivation des comptes ;
sécurité renforcée ;
tests automatisés ;
CI/CD GitHub Actions ;
contrôle qualité Python ;
build frontend ;
audit des dépendances ;
scan de secrets ;
validation Docker Compose ;
documentation technique ;
captures de démonstration.

La V5 montre que le projet ne se limite pas à une interface fonctionnelle. Elle montre aussi une démarche DevSecOps avec validation, sécurité, supervision et traçabilité.

Endpoints principaux de l’API
Authentification
Endpoint	Méthode	Description
/auth/login	POST	Connexion utilisateur et génération du token JWT
Ressources
Endpoint	Méthode	Description
/resources	GET	Liste les ressources internes
/resources/{resource_id}	GET	Affiche le détail d’une ressource
Demandes d’accès
Endpoint	Méthode	Description
/access-requests	GET	Liste les demandes d’accès
/access-requests	POST	Crée une demande d’accès
/access-requests/{request_id}/manager-decision	PATCH	Approuve ou refuse une demande
/access-requests/{request_id}/grant	PATCH	Attribue un accès après validation
Accès attribués
Endpoint	Méthode	Description
/access-grants	GET	Liste les accès attribués
/access-grants/{grant_id}/revoke	PATCH	Révoque un accès
Utilisateurs
Endpoint	Méthode	Description
/users	GET	Liste les utilisateurs
/users/{user_id}	GET	Affiche un utilisateur
/users	POST	Crée un utilisateur
/users/{user_id}/role	PATCH	Modifie le rôle d’un utilisateur
/users/{user_id}/status	PATCH	Active ou désactive un utilisateur
Audit et monitoring
Endpoint	Méthode	Description
/audit-logs	GET	Liste les événements d’audit
/metrics	GET	Expose les métriques Prometheus
/health	GET	Vérifie l’état de l’API
Comptes de démonstration
Rôle	Email	Utilisation
employee	alice.employee@asteriatech.local	Créer des demandes d’accès
manager	marc.manager@asteriatech.local	Valider ou refuser les demandes
it_admin	ines.itadmin@asteriatech.local	Attribuer et révoquer les accès
security_admin	paul.security@asteriatech.local	Gérer les utilisateurs, l’audit et le monitoring

Les mots de passe de démonstration sont définis dans le seed ou la documentation interne du projet.

Installation locale
1. Cloner le dépôt
git clone https://github.com/olivierpolynice/accessguard-devsecops.git
cd accessguard-devsecops
2. Créer et activer l’environnement Python
Windows PowerShell
python -m venv app\.venv
.\app\.venv\Scripts\Activate.ps1
Linux / macOS
python -m venv app/.venv
source app/.venv/bin/activate
3. Installer les dépendances backend
pip install -r requirements.txt
4. Lancer l’API backend
uvicorn app.main:app --reload --port 8000

L’API est disponible sur :

http://localhost:8000

Documentation Swagger :

http://localhost:8000/docs
Lancement du frontend
cd frontend
npm install
npm run dev

Frontend disponible sur :

http://localhost:8080
Lancement avec Docker Compose
docker compose up --build

Services disponibles :

Service	URL
API FastAPI	http://localhost:8000
Swagger	http://localhost:8000/docs
Frontend	http://localhost:8080
Prometheus	http://localhost:9090
Grafana	http://localhost:3000
Metrics API	http://localhost:8000/metrics
Tests et validation
Lancer les tests backend
python -m pytest -v

Résultat de validation observé pendant la stabilisation V5 :

78 passed, 10 skipped, 1 warning

Les tests ignorés concernaient les routes utilisateurs V5 pendant leur phase d’implémentation.

Lancer le contrôle qualité Python
flake8 app tests
Vérifier le build frontend
cd frontend
npm ci
npm run build
Vérifier Docker Compose
docker compose config
Qualité et sécurité

Le projet intègre plusieurs contrôles qualité et sécurité.

Contrôle	Objectif
Pytest	Vérifier le comportement du backend
Flake8	Contrôler la qualité du code Python
npm run build	Vérifier la compilation frontend
pip-audit	Vérifier les vulnérabilités Python
npm audit	Vérifier les vulnérabilités frontend
Gitleaks	Détecter les secrets exposés
Docker Compose config	Vérifier la configuration Docker
GitHub Actions	Automatiser les validations
GitHub Actions

La CI/CD GitHub Actions permet de vérifier automatiquement le projet.

Les contrôles utilisés couvrent :

les tests backend ;
le lint Python ;
la construction du frontend ;
l’audit des dépendances ;
la détection de secrets ;
la validation Docker Compose.

Cette approche limite les risques d’intégrer du code instable dans la branche principale.

Monitoring

AccessGuard expose des métriques Prometheus via :

http://localhost:8000/metrics

Exemples de métriques suivies :

connexions réussies ;
connexions échouées ;
demandes créées ;
approbations ;
refus ;
attributions ;
révocations ;
actions interdites.

Prometheus collecte ces métriques et Grafana permet de les visualiser.

Sécurité applicative

AccessGuard applique plusieurs règles de sécurité :

authentification obligatoire sur les routes protégées ;
token JWT ;
contrôle des rôles ;
séparation des responsabilités ;
mots de passe hashés ;
absence de password_hash dans les réponses API ;
refus 401 sans token ;
refus 403 si le rôle est insuffisant ;
audit des actions sensibles ;
fichiers .env non versionnés ;
scan de secrets avec Gitleaks.
Captures de démonstration

Les captures sont rangées dans :

docs/screenshots/

Organisation recommandée :

docs/screenshots/rendu-08/v5/

Captures importantes :

Capture	Description
01_login_employee.png	Connexion employé
02_employee_dashboard.png	Tableau de bord employé
03_manager_requests.png	Validation manager
04_it_admin_grants.png	Attribution IT
05_security_admin_users.png	Gestion utilisateurs
06_user_creation.png	Création utilisateur
07_user_deactivation_confirmation.png	Désactivation utilisateur
08_access_revocation_confirmation.png	Révocation d’accès
09_error_403.png	Contrôle RBAC
10_mobile_responsive.png	Responsive mobile
11_audit_screen.png	Journal d’audit
12_monitoring_screen.png	Monitoring
Démonstration fonctionnelle
Parcours employee

L’utilisateur employee peut :

se connecter ;
consulter les ressources ;
créer une demande d’accès ;
suivre l’état de ses demandes.
Parcours manager

L’utilisateur manager peut :

consulter les demandes en attente ;
approuver une demande ;
refuser une demande ;
ajouter une justification.
Parcours it_admin

L’utilisateur it_admin peut :

consulter les demandes approuvées ;
attribuer un accès ;
révoquer un accès ;
ajouter une justification de révocation.
Parcours security_admin

L’utilisateur security_admin peut :

consulter les utilisateurs ;
créer un utilisateur ;
modifier un rôle ;
activer ou désactiver un compte ;
consulter les audits ;
accéder au monitoring.
Limites actuelles

AccessGuard reste un projet pédagogique. Certaines améliorations peuvent être ajoutées dans une version future :

déploiement cloud complet ;
HTTPS avec reverse proxy ;
refresh tokens ;
tests E2E Playwright ;
export CSV des audits ;
alertes Grafana plus avancées ;
gestion plus fine des permissions ;
amélioration de l’interface d’administration.
Perspectives V6

Une V6 pourrait permettre de poursuivre la professionnalisation du projet avec :

déploiement en ligne ;
environnement staging ;
tests end-to-end ;
durcissement sécurité ;
alertes Prometheus / Grafana ;
documentation utilisateur complète ;
préparation finale à la soutenance.
Conclusion

AccessGuard est le résultat d’un travail progressif mené par le Groupe 22.

Nous sommes partis d’une première réflexion autour de CyberPulse, puis nous avons recentré le projet vers une application plus précise : la gouvernance des accès internes.

De la V1 à la V5, nous avons construit un projet intégrant backend, frontend, base de données, authentification, rôles, audit, monitoring, Docker, tests automatisés et CI/CD.

Cette progression montre notre capacité à organiser un projet DevSecOps, à le faire évoluer par versions successives et à produire des preuves techniques vérifiables.

Auteurs

Projet réalisé par le Groupe 22 dans le cadre du projet pédagogique DevOps / DevSecOps ESTIAM 2025/2026.