# Projet DevOps - E4 ESTIAM - 2025/2026 - Groupe 22

## AccessGuard — Plateforme DevSecOps de gouvernance des accès

AccessGuard est une application pédagogique conçue pour simuler la gestion sécurisée des accès internes dans une entreprise fictive nommée **AsteriaTech**.

Le projet permet de gérer le cycle complet d’une demande d’accès : création d’une demande par un employé, validation par un manager, attribution par un administrateur IT, révocation d’un accès, audit des actions et supervision technique de l’application.

Ce projet a été réalisé dans le cadre du projet pédagogique DevOps / DevSecOps ESTIAM 2025/2026.

---

## Membres du Groupe 22

| N° | Nom et Prénom | Rôle dans le projet |
|---:|---|---|
| 1 | Olivier POLYNICE | Chef de projet et lead technique |
| 2 | Yazid EL-BAK | Scrum Master et référent Backend / DevOps |
| 3 | Irina LETSARA | Référente Tests, CI/CD, Qualité et Sécurité |
| 4 | Élodie IPARRAGUIRRE | Responsable UI/UX et documentation fonctionnelle |

---

## Stack technique

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![Vite](https://img.shields.io/badge/Vite-Build-purple)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-orange)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-black)
![Pytest](https://img.shields.io/badge/Pytest-Tests-yellow)
![Flake8](https://img.shields.io/badge/Flake8-Quality-red)
![Gitleaks](https://img.shields.io/badge/Gitleaks-Secrets_Scan-purple)

---

# Concept du projet

AccessGuard répond à un besoin courant dans les entreprises : éviter que les accès sensibles soient attribués sans validation, sans traçabilité ou sans contrôle.

Dans une organisation réelle, un employé ne doit pas pouvoir obtenir directement un accès à un serveur, à un outil d’administration ou à une ressource critique. Une demande doit être créée, validée, attribuée puis auditée.

AccessGuard reproduit ce fonctionnement sous forme d’application web complète.

Le projet couvre :

- une API backend avec FastAPI ;
- une interface frontend avec React ;
- une base de données SQLite ;
- une authentification JWT ;
- une gestion des rôles ;
- une journalisation des actions ;
- des métriques Prometheus ;
- des tableaux de bord Grafana ;
- une chaîne CI/CD GitHub Actions ;
- des tests automatisés ;
- une logique DevSecOps avec contrôles qualité et sécurité.

---

# Contexte initial : de CyberPulse à AccessGuard

Au départ, notre réflexion était orientée autour du projet **CyberPulse**, une idée centrée sur la cybersécurité, l’audit, la surveillance et la sensibilisation aux risques numériques.

CyberPulse nous a permis de poser les premières bases fonctionnelles :

- identification des risques ;
- réflexion autour de la sécurité ;
- besoin de supervision ;
- importance des preuves techniques ;
- logique d’audit ;
- sensibilisation aux accès sensibles.

Cependant, au fil de l’analyse, nous avons décidé de recentrer le projet vers une application plus précise, plus démontrable et plus adaptée aux exigences DevOps.

Ce recentrage a donné naissance à **AccessGuard**.

AccessGuard conserve l’esprit cybersécurité de CyberPulse, mais avec un périmètre plus concret : la gouvernance des accès internes.

Ce choix nous a permis de construire progressivement un projet cohérent, testable, versionné, dockerisé et observable.

---

# Fonctionnalités principales

| Fonctionnalité | Description |
|---|---|
| Authentification | Connexion sécurisée avec JWT |
| Gestion des rôles | Séparation employee, manager, it_admin, security_admin |
| Ressources | Liste des ressources internes disponibles |
| Demandes d’accès | Création d’une demande par un employé |
| Validation manager | Approbation ou refus d’une demande |
| Attribution IT | Attribution d’un accès après validation |
| Révocation | Suppression d’un accès existant |
| Audit | Journalisation des actions importantes |
| Utilisateurs | Gestion des comptes et statuts utilisateurs |
| Monitoring | Exposition des métriques Prometheus |
| Dashboard | Visualisation technique avec Grafana |
| CI/CD | Tests et contrôles automatiques avec GitHub Actions |

---

# Rôles applicatifs

| Rôle | Description | Accès principal |
|---|---|---|
| employee | Employé demandeur | Ressources, demandes d’accès |
| manager | Responsable de validation | Validation ou refus des demandes |
| it_admin | Administrateur IT | Attribution et révocation des accès |
| security_admin | Administrateur sécurité | Audit, utilisateurs, monitoring |

---

# Workflow métier

Le fonctionnement principal d’AccessGuard suit le cycle suivant :

```text
Employé
   ↓
Création d’une demande d’accès
   ↓
Manager
   ↓
Approbation ou refus
   ↓
Administrateur IT
   ↓
Attribution ou révocation
   ↓
Security Admin
   ↓
Audit et supervision

Progression du projet
Version 1 — Socle API et workflow métier

La V1 a permis de poser les bases du projet.

Nous avons mis en place une première API FastAPI permettant de gérer :

les ressources internes ;
les demandes d’accès ;
les décisions manager ;
les attributions ;
les révocations ;
les premiers journaux d’audit.

Cette version fonctionnait principalement en mémoire, mais elle a permis de valider la logique métier principale.

Objectifs de la V1 :

créer un socle backend ;
définir les entités principales ;
valider le cycle demande → décision → attribution ;
préparer les tests ;
structurer le projet.
Version 2 — Authentification et rôles

La V2 a introduit la sécurité applicative.

Nous avons ajouté :

une route de connexion ;
la génération de tokens JWT ;
la vérification des rôles ;
la protection des routes ;
les réponses 401 et 403 ;
les comptes de démonstration.

Cette version a permis de passer d’une API simple à une API protégée par authentification.

Les rôles applicatifs ont été structurés autour de quatre profils :

employee
manager
it_admin
security_admin

Chaque rôle possède des droits différents afin de respecter le principe de séparation des responsabilités.

Version 3 — Persistance et structuration

La V3 a marqué une étape importante avec l’introduction de la persistance.

Nous avons commencé à structurer les données dans une base SQLite afin de ne plus dépendre uniquement de données temporaires en mémoire.

Cette version a permis d’améliorer :

la stabilité des données ;
la structure backend ;
la séparation des responsabilités ;
la fiabilité des tests ;
la préparation du projet pour Docker et CI/CD.

La V3 a aussi renforcé la logique d’audit, car les actions réalisées dans l’application doivent pouvoir être consultées et conservées.

Version 4 — Interface, Docker et monitoring

La V4 a transformé AccessGuard en application complète.

Nous avons ajouté une interface frontend avec React et Vite.

Le frontend permet aux utilisateurs de se connecter et d’accéder à des pages différentes selon leur rôle :

tableau de bord ;
ressources ;
demandes ;
validation manager ;
accès attribués ;
audit ;
utilisateurs ;
monitoring.

La V4 a aussi intégré une logique DevOps plus complète avec :

Docker ;
Docker Compose ;
Prometheus ;
Grafana ;
GitHub Actions ;
tests automatisés ;
build frontend.

Cette version a permis de rendre le projet démontrable de bout en bout.

Version 5 — Stabilisation finale et qualité DevSecOps

La V5 correspond à la phase de professionnalisation du projet.

Nous avons consolidé l’existant pour obtenir une version plus robuste, plus propre et plus proche d’un projet DevSecOps complet.

Travaux réalisés en V5 :

stabilisation du backend ;
amélioration de la gestion des utilisateurs ;
renforcement des tests ;
validation CI/CD ;
contrôle qualité Python ;
build frontend ;
audit des dépendances ;
détection de secrets ;
vérification Docker Compose ;
protection des fichiers sensibles ;
documentation technique ;
captures de validation.

La V5 permet de montrer que le projet ne se limite pas à une démonstration fonctionnelle, mais qu’il respecte également une logique de qualité, de sécurité, d’intégration continue et de traçabilité.

Endpoints principaux de l’API
Authentification
Endpoint	Méthode	Description
/auth/login	POST	Connexion utilisateur et génération du JWT
Ressources
Endpoint	Méthode	Description
/resources	GET	Liste les ressources internes
/resources/{resource_id}	GET	Détail d’une ressource
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
it_admin	ines.itadmin@asteriatech.local	Attribuer ou révoquer des accès
security_admin	paul.security@asteriatech.local	Gérer utilisateurs, audit et monitoring
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
Tests
Lancer les tests backend
python -m pytest -v
Lancer Flake8
flake8 app tests
Vérifier le build frontend
cd frontend
npm ci
npm run build
Qualité et sécurité

Le projet intègre plusieurs contrôles qualité et sécurité.

Contrôle	Objectif
Pytest	Vérifier le comportement backend
Flake8	Contrôler la qualité du code Python
npm run build	Vérifier la compilation frontend
pip-audit	Vérifier les vulnérabilités Python
npm audit	Vérifier les vulnérabilités frontend
Gitleaks	Détecter les secrets exposés
Docker Compose config	Vérifier la configuration des services
GitHub Actions	Automatiser les validations
GitHub Actions

La CI/CD vérifie automatiquement le projet lors des pushs et pull requests.

Contrôles principaux :

installation des dépendances ;
tests backend ;
lint Python ;
build frontend ;
audit de sécurité ;
scan de secrets ;
validation Docker Compose.

L’objectif est d’éviter qu’une modification instable soit fusionnée dans la branche principale.

Monitoring

AccessGuard expose des métriques Prometheus via :

http://localhost:8000/metrics

Exemples de métriques suivies :

nombre de connexions réussies ;
nombre de connexions échouées ;
nombre de demandes créées ;
nombre d’approbations ;
nombre de refus ;
nombre d’attributions ;
nombre de révocations ;
nombre d’actions interdites.

Prometheus collecte ces métriques et Grafana permet de les visualiser sous forme de tableaux de bord.

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
08_access_revocation_confirmation.png	Révocation accès
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
accéder aux pages de monitoring.
Sécurité applicative

AccessGuard applique plusieurs règles de sécurité :

authentification obligatoire sur les routes protégées ;
token JWT ;
contrôle des rôles ;
refus 401 sans authentification ;
refus 403 en cas de rôle insuffisant ;
mots de passe hashés ;
absence de password_hash dans les réponses API ;
audit des actions sensibles ;
fichiers .env ignorés par Git ;
détection de secrets avec Gitleaks.
Limites actuelles

AccessGuard reste un projet pédagogique. Certaines améliorations peuvent être ajoutées dans une future version :

déploiement cloud complet ;
HTTPS avec reverse proxy ;
refresh tokens ;
tests E2E Playwright ;
export CSV des audits ;
alertes Grafana plus avancées ;
gestion plus fine des permissions ;
interface d’administration plus complète.
Perspectives V6

Une V6 pourrait permettre de poursuivre la professionnalisation du projet avec :

déploiement en ligne ;
pipeline CI/CD plus avancé ;
environnement staging ;
tests end-to-end ;
durcissement sécurité ;
alertes Prometheus/Grafana ;
documentation utilisateur complète ;
préparation finale à la soutenance.
Conclusion

AccessGuard est le résultat d’un travail progressif mené par le Groupe 22.

Nous sommes partis d’une réflexion initiale autour de CyberPulse, puis nous avons recentré le projet vers une application plus précise et plus démontrable : la gouvernance des accès internes.

De la V1 à la V5, nous avons construit un projet complet intégrant backend, frontend, base de données, authentification, rôles, audit, monitoring, Docker, tests automatisés et CI/CD.

Cette progression montre notre capacité à organiser un projet DevSecOps, à faire évoluer une application par versions successives et à produire des preuves techniques vérifiables.

Auteurs

Projet réalisé par le Groupe 22 dans le cadre du projet pédagogique DevOps / DevSecOps ESTIAM 2025/2026.