# AccessGuard — Plateforme DevSecOps de gouvernance des accès

## Présentation

AccessGuard est une application pédagogique développée pour l’entreprise fictive **AsteriaTech**.

Le projet répond à un besoin de gouvernance des accès internes : permettre à un employé de demander un accès à une ressource, faire valider cette demande par un manager, attribuer l’accès par un administrateur IT, puis le révoquer lorsque cela est nécessaire.

L’objectif est de construire progressivement une plateforme intégrant les dimensions :

* développement d’API ;
* cybersécurité ;
* traçabilité et audit ;
* gestion des accès ;
* tests automatisés ;
* DevSecOps ;
* infrastructure, réseau et supervision.

## Fonctionnalités actuellement disponibles

* Vérification de disponibilité de l’API avec `GET /health`
* Consultation du catalogue de ressources avec `GET /resources`
* Création d’une demande d’accès avec `POST /access-requests`
* Validation ou refus d’une demande par un manager
* Attribution d’un accès par un administrateur IT
* Révocation d’un accès attribué
* Journalisation des actions sensibles dans un journal d’audit
* Tests automatisés avec pytest

## Workflow métier

```text
Employé
  ↓
Création d’une demande d’accès
  ↓
Validation ou refus par le manager
  ↓
Attribution de l’accès par l’administrateur IT
  ↓
Accès actif
  ↓
Révocation éventuelle
  ↓
Journalisation de chaque action sensible
```

## Ressources internes simulées

L’environnement AsteriaTech contient actuellement les ressources suivantes :

* VPN Entreprise
* Serveur de fichiers Finance
* Environnement de développement
* Portail d’administration
* Plateforme Grafana

Chaque ressource possède un niveau de sensibilité afin de représenter un contexte d’entreprise réaliste.

## Architecture actuelle du projet

```text
accessguard-devsecops/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── database.py
│   ├── models.py
│   ├── seed.py
│   └── requirements.txt
├── docs/
│   ├── diagrammes/
│   ├── rapports/
│   └── screenshots/
├── infrastructure/
├── monitoring/
├── security/
└── tests/
    └── test_accessguard.py
```

## Technologies utilisées

* Python
* FastAPI
* Uvicorn
* Pydantic
* pytest
* httpx
* Swagger / OpenAPI
* Git et GitHub
* Visual Studio Code

## Installation locale

Depuis le dossier `app` :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lancer l’application

Depuis le dossier `app` :

```powershell
uvicorn main:app --reload
```

L’API est ensuite disponible à cette adresse :

```text
http://127.0.0.1:8000
```

La documentation Swagger est disponible ici :

```text
http://127.0.0.1:8000/docs
```

## Lancer les tests

Depuis la racine du projet :

```powershell
python -m pytest -v
```

Résultat actuel attendu :

```text
5 passed
```

Les tests vérifient notamment :

* la disponibilité de l’API ;
* le catalogue de ressources ;
* la création d’une demande ;
* le rejet de dates incohérentes ;
* le workflow complet : demande, approbation, attribution et révocation.

## Captures de démonstration

Les captures utilisées pour le rendu n°06 sont disponibles dans :

```text
docs/screenshots/rendu-06/
```

Elles couvrent :

* le health check ;
* les ressources ;
* la création de demande ;
* le contrôle des dates ;
* la validation manager ;
* le journal d’audit ;
* l’attribution d’accès ;
* la révocation ;
* les tests pytest.

## Évolutions prévues

Les prochaines étapes prévues sont :

* persistance des données avec SQLite puis PostgreSQL ;
* authentification JWT ;
* gestion des rôles et permissions ;
* conteneurisation Docker ;
* contrôles de sécurité DevSecOps ;
* intégration de l’architecture réseau et de la segmentation VLAN ;
* supervision avec Prometheus et Grafana ;
* pipeline CI/CD.

## Statut du projet

Le socle fonctionnel de gestion des accès est opérationnel en environnement local. Le projet est en phase de consolidation avant intégration progressive des composants DevSecOps, sécurité et infrastructure.
## Statut du socle P0

Le socle fonctionnel P0 d’AccessGuard est terminé et validé en environnement local.

Fonctionnalités réalisées :

- endpoint `GET /health` avec état, version et date de contrôle ;
- catalogue de 5 ressources internes chargées depuis `seed.py` ;
- création, liste et consultation détaillée des demandes d’accès ;
- workflow métier avec les statuts :
  `PENDING_MANAGER`, `APPROVED`, `REFUSED`, `GRANTED`, `REVOKED` ;
- attribution et révocation d’un accès simulé ;
- journal d’audit des actions métier ;
- contrôles d’erreurs :
  - dates incohérentes : `422` ;
  - statut manager invalide : `422` ;
  - demande inexistante : `404` ;
  - ressource inexistante : `404` ;
  - attribution avant approbation : `409` ;
  - double grant actif : `409` ;
- tests automatisés pytest couvrant le socle P0.

Résultat de validation attendu :

```text
13 passed

## Intégration continue — GitHub Actions

Un workflow GitHub Actions a été ajouté afin d’automatiser l’exécution des tests du projet.

### Déclenchement

Le workflow se lance automatiquement :

- à chaque push sur `main` ou sur une branche `feature/**` ;
- à chaque Pull Request vers `main`.

### Étapes exécutées

Le pipeline réalise les actions suivantes :

1. récupération du code source ;
2. installation de Python 3.12 ;
3. installation des dépendances depuis `app/requirements.txt` ;
4. exécution des tests avec pytest.

### Commande exécutée

```bash
python -m pytest -v