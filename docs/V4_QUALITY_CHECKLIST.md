# Checklist Qualité V4 — Irina

## Tests

- [x] Tests du endpoint `/me`
- [x] Tests du dashboard summary
- [x] Tests des métriques métier
- [x] Tests 401/403 sur les routes protégées
- [x] Tests de non-régression

## Sécurité

- [x] `.env` non poussé
- [x] `accessguard.db` non poussé
- [x] Volumes Docker non poussés
- [x] Fichiers Azurite ignorés
- [x] `.venv` ignoré

## CI/CD

- [x] Checkout du dépôt
- [x] Setup Python
- [x] Installation des requirements
- [x] Lancement de pytest
- [x] Vérification optionnelle de `docker compose config`

## Qualité dépôt

- [x] CI verte
- [x] Docker valide
- [x] Documentation présente
- [x] Captures présentes