# Checklist qualité V5 — Irina Letsara

## Informations

- Projet : AccessGuard
- Version : V5
- Responsable : Irina Letsara
- Rôle : tests, CI/CD, qualité et sécurité
- Branche : `feature/v5-irina`

## Lot I1 — Plan de tests

- [ ] `docs/V5_TEST_PLAN.md` créé
- [ ] `tests/conftest.py` créé
- [ ] `tests/test_users.py` créé
- [ ] `tests/test_v5_security.py` créé
- [ ] `tests/test_v5_workflow.py` créé
- [ ] `pytest.ini` créé
- [ ] tests classés par catégories
- [ ] tests d’authentification validés
- [ ] mauvais mot de passe testé
- [ ] utilisateur inconnu testé
- [ ] utilisateur inactif testé ou attente backend documentée
- [ ] token expiré testé
- [ ] tests utilisateurs validés ou attente backend documentée
- [ ] tests RBAC validés
- [ ] tests workflow validés
- [ ] tests audit validés
- [ ] tests monitoring validés
- [ ] tests V1 à V4 toujours passants
- [ ] tests V5 passants

## Lot I2 — Backend CI

- [ ] installation Python réussie
- [ ] installation des requirements réussie
- [ ] tous les tests Pytest réussis
- [ ] rapport JUnit généré
- [ ] Flake8 réussi
- [ ] job backend vert

## Lot I2 — Frontend CI

- [ ] `frontend/package.json` présent
- [ ] `frontend/package-lock.json` présent
- [ ] `npm ci` réussi
- [ ] `npm run build` réussi
- [ ] job frontend vert

## Lot I2 — Sécurité

- [ ] Gitleaks réussi
- [ ] pip-audit exécuté
- [ ] vulnérabilités Python corrigées ou documentées
- [ ] npm audit exécuté
- [ ] vulnérabilités npm corrigées ou documentées
- [ ] `.env` non versionné
- [ ] `.venv` non versionné
- [ ] `accessguard.db` non versionné
- [ ] volumes Docker non versionnés
- [ ] fichiers Azurite non versionnés
- [ ] aucun secret réel dans le dépôt

## Lot I2 — Docker

- [ ] `docker compose config --quiet` réussi
- [ ] variables Docker documentées
- [ ] aucun secret écrit directement dans Docker Compose

## Lot I2 — Protection des branches

- [ ] Pull Request obligatoire
- [ ] branche principale protégée
- [ ] job backend obligatoire
- [ ] job frontend obligatoire
- [ ] Gitleaks obligatoire
- [ ] pip-audit obligatoire
- [ ] npm audit obligatoire
- [ ] Docker Compose obligatoire
- [ ] Quality Gate obligatoire
- [ ] fusion impossible si un check échoue

## Lot I3 — Qualité API

- [ ] erreurs API lisibles
- [ ] réponses d’erreur contiennent `detail`
- [ ] codes 401 cohérents
- [ ] codes 403 cohérents
- [ ] codes 404 cohérents
- [ ] codes 409 cohérents
- [ ] codes 422 cohérents
- [ ] nouvelles routes présentes dans Swagger
- [ ] nouvelles routes documentées
- [ ] aucun `404` accepté comme réussite d’un test RBAC

## Lot I3 — Documentation

- [ ] noms des documents conformes
- [ ] noms des captures cohérents
- [ ] toutes les captures ont une légende
- [ ] nombre final de tests indiqué
- [ ] résultat des tests indiqué
- [ ] état de chaque workflow indiqué
- [ ] vulnérabilités éventuelles documentées
- [ ] rapport de validation présent

## Preuves

- [ ] capture création branche
- [ ] capture arborescence V5
- [ ] capture Pytest
- [ ] capture Flake8
- [ ] capture npm ci
- [ ] capture npm build
- [ ] capture Gitleaks
- [ ] capture pip-audit
- [ ] capture npm audit
- [ ] capture Docker Compose
- [ ] capture GitHub Actions verte
- [ ] capture Quality Gate
- [ ] capture Pull Request
- [ ] capture `git status`
- [ ] capture absence de fichiers sensibles

## Validation finale

- [ ] dépôt propre
- [ ] branche poussée
- [ ] Pull Request créée
- [ ] CI totalement verte
- [ ] rapport terminé
- [ ] livrable prêt à intégrer