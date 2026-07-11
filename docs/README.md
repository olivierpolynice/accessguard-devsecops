# Documentation AccessGuard

Ce dossier centralise les documents produits dans le cadre du projet **AccessGuard**, une API pédagogique de gestion et de gouvernance des accès internes pour l’entreprise fictive AsteriaTech.

## Organisation du dossier

```text
docs/
├── architecture-reseau/   # Schémas réseau, VLAN, plan d’adressage et règles de sécurité
├── diagrammes/            # Diagrammes UML : cas d’utilisation, activité, séquence et classes
├── maquettes/             # Maquettes des interfaces utilisateur
├── rapports/              # Rapports des différents rendus
├── screenshots/           # Captures de tests et démonstrations
│   └── rendu-07/          # Preuves fonctionnelles et de sécurité du V1
└── README.md
```

## Rendu n°02 — Conception

Les documents de conception comprennent notamment :

- le contexte et les objectifs du projet ;
- le périmètre fonctionnel ;
- les acteurs et cas d’utilisation ;
- les scénarios métier ;
- les diagrammes UML ;
- le modèle de données ;
- les maquettes ;
- l’architecture réseau ;
- le plan d’adressage ;
- les règles de sécurité ;
- le backlog, les epics et les sprints.

## Rendu n°07 — Base fonctionnelle V1

Le dossier `screenshots/rendu-07` contient les preuves de fonctionnement de la première version de l’API AccessGuard.

### Parcours testé

1. Authentification réussie d’un employé avec génération d’un jeton JWT.
2. Refus d’authentification avec identifiants invalides (`401 Unauthorized`).
3. Consultation des ressources internes disponibles.
4. Création d’une demande d’accès à une ressource sensible.
5. Validation de la demande par un manager.
6. Attribution d’un accès actif par l’administrateur IT.
7. Consultation des accès attribués.
8. Révocation d’un accès.
9. Consultation des journaux d’audit.

### Captures principales

| Capture | Description |
|---|---|
| `R07_03_security_tests_15_passed.png` | Résultat des tests de sécurité automatisés. |
| `R07_04_auth_login_success_200.png` | Authentification réussie et génération d’un jeton JWT. |
| `R07_05_auth_login_invalid_401.png` | Refus d’authentification avec identifiants invalides. |
| `R07_06_resources_list_200.png` | Consultation des ressources internes disponibles. |
| `R07_07_access_request_create.png` | Création d’une demande d’accès. |
| `R07_08_manager_decision_approved.png` | Validation d’une demande par le manager. |
| `R07_09_access_grant_active_201.png` | Attribution effective d’un accès actif. |
| `R07_10_access_grants_list_200.png` | Consultation des accès attribués. |
| `R07_11_access_revoke_200.png` | Révocation d’un accès existant. |
| `R07_12_audit_logs_200.png` | Consultation des journaux d’audit. |

## Rendus suivants

Les prochaines itérations du projet présenteront progressivement :

- le renforcement des contrôles d’accès ;
- l’infrastructure Docker et réseau ;
- la pipeline DevSecOps ;
- le monitoring ;
- la démonstration finale.
