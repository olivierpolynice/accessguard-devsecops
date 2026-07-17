# Livrable Irina V4 — Tests, CI/CD, Qualité et Sécurité

## Objectif

La V4 d’AccessGuard doit rester stable et éviter les régressions.
Le travail Irina V4 renforce les tests automatisés, la CI/CD, la sécurité du dépôt et la qualité documentaire.

## Tests ajoutés

Les tests V4 couvrent :

- le endpoint `/me` ;
- le dashboard summary ;
- les métriques métier ;
- les erreurs 401/403 sur les nouvelles routes protégées ;
- la non-régression sur `/health` ;
- la non-régression sur `/resources`.

Fichier ajouté :

```text
tests/test_v4_irina.py