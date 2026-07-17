# AccessGuard V5 — Résumé du sprint

## 1. Objectif du sprint

La V5 a pour objectif d’ajouter une gestion persistante des utilisateurs,
une authentification basée sur SQLite, des contrôles de sécurité renforcés,
des tests automatisés et des métriques métier exploitables dans Grafana.

## 2. Répartition initiale

### Olivier Polynice

- intégration de la table users ;
- authentification SQLite ;
- gestion des utilisateurs actifs et inactifs ;
- intégration backend ;
- documentation et validation.

### Irina

- tests automatisés ;
- CI/CD ;
- contrôles qualité ;
- scans de sécurité ;
- validation GitHub Actions.

### Yazid El-Bak

- suivi Scrum ;
- endpoints users ;
- métriques métier ;
- dashboard Grafana V5 ;
- validation Docker.

### Élodie

- interface utilisateur ;
- amélioration visuelle ;
- expérience utilisateur ;
- documentation frontend.

## 3. Adaptations réalisées

En raison d’un problème matériel rencontré par Yazid, Olivier a repris
les tâches restantes liées aux métriques métier, à Grafana et à la
documentation Scrum.

Les routes users initialement prévues dans le lot Yazid ont également été
intégrées dans la branche Olivier afin de garantir la livraison complète
de la V5.

## 4. Résultats obtenus

- table users persistante dans SQLite ;
- comptes utilisateurs de démonstration ;
- login basé sur la base de données ;
- blocage des utilisateurs inactifs ;
- administration des utilisateurs par security_admin ;
- tests backend validés ;
- frontend compilé ;
- Docker Compose validé ;
- contrôles CI/CD et sécurité validés ;
- métriques métier ajoutées ;
- dashboard Grafana V5 mis à jour.

## 5. Blocages rencontrés

- problème matériel de Yazid ;
- incompatibilité locale entre passlib et bcrypt ;
- erreurs Flake8 W292 ;
- vulnérabilité ecdsa sans version corrigée disponible ;
- règle GitHub imposant une approbation externe.

## 6. Décisions prises

- reprise des tâches critiques par Olivier ;
- ajout d’une exception pip-audit documentée ;
- correction automatique des fichiers Python sans saut de ligne final ;
- validation de la PR après réussite de tous les contrôles CI.

## 7. État final

La V5 est considérée comme terminée lorsque :

- les tests sont validés ;
- les métriques sont exposées ;
- Grafana affiche les métriques métier ;
- Docker Compose fonctionne ;
- la documentation est complète ;
- les preuves sont enregistrées.