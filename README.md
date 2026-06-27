# AccessGuard DevSecOps

## Présentation

AccessGuard est une plateforme DevSecOps sécurisée de gestion et de gouvernance des accès internes, conçue pour l’entreprise fictive **AsteriaTech**.

Le projet répond à un besoin de centralisation des demandes d’accès aux ressources internes de l’entreprise. Il permet de soumettre, valider, attribuer, révoquer et tracer les accès accordés aux collaborateurs.

## Objectifs

* Centraliser les demandes d’accès aux ressources internes.
* Mettre en place une gestion des rôles et des permissions.
* Appliquer le principe du moindre privilège.
* Assurer la traçabilité des actions sensibles grâce à un journal d’audit.
* Déployer l’application dans un environnement conteneurisé et sécurisé.
* Automatiser les contrôles de qualité et de sécurité.
* Superviser la disponibilité et l’état des services.

## Fonctionnalités prévues

* Authentification sécurisée des utilisateurs.
* Gestion des rôles : employé, manager, administrateur IT et administrateur sécurité.
* Catalogue des ressources internes.
* Création et suivi des demandes d’accès.
* Validation ou refus des demandes.
* Attribution, révocation et expiration des accès.
* Journalisation des actions sensibles.
* Tableau de bord de supervision.

## Technologies prévues

* Python / FastAPI
* PostgreSQL
* Docker et Docker Compose
* Nginx
* Git et GitHub
* Jenkins
* SonarQube
* Trivy
* Prometheus
* Grafana
* pfSense et VLAN

## Structure du projet

```text
accessguard-devsecops/
├── app/                  # Code de l'application
├── docs/                 # Documentation, diagrammes et rapports
├── infrastructure/       # Docker, Nginx, réseau et pfSense
├── monitoring/           # Prometheus, Grafana et métriques
├── security/             # Politique, scans et éléments de sécurité
├── tests/                # Tests automatisés
├── README.md
└── .gitignore
```

## État du projet

Phase actuelle : conception du projet et préparation du rendu n°02.

## Avertissement

Ce projet est réalisé dans un cadre pédagogique. AsteriaTech est une entreprise fictive. Aucune donnée réelle ni aucun accès réel à des systèmes d’entreprise ne sont utilisés.
