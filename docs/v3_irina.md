# V3 — Partie Irina : Tests, CI/CD et sécurité applicative

## 1. Objectif

Cette partie vise à sécuriser la qualité du projet AccessGuard V3.

L’objectif est de vérifier que les évolutions V3 n’ont pas cassé les fonctionnalités déjà validées en V2 :

- authentification JWT ;
- contrôle RBAC ;
- workflow des demandes d’accès ;
- persistance SQLite ;
- logs d’audit ;
- Docker Compose ;
- monitoring Prometheus et Grafana ;
- prototype frontend statique.

## 2. Tests automatisés

Les tests automatisés sont exécutés avec Pytest.

Commande utilisée :

```powershell
python -m pytest -v
```

Résultat obtenu :

```text
31 passed, 1 warning
```

Le warning observé concerne `TestClient` et n’est pas bloquant pour le projet.

Les tests couvrent notamment :

- disponibilité de l’API avec `/health` ;
- création d’une demande d’accès ;
- refus des accès sans JWT ;
- refus des accès avec mauvais rôle ;
- validation manager ;
- attribution d’accès par IT Admin ;
- révocation d’accès ;
- consultation des audit logs ;
- génération et validation des tokens JWT.

## 3. Sécurité applicative vérifiée

Les contrôles suivants ont été vérifiés :

| Contrôle | Résultat attendu |
|---|---|
| Route protégée sans JWT | 401 Unauthorized |
| Route avec mauvais rôle | 403 Forbidden |
| Ressource inexistante avec JWT valide | 404 Not Found |
| État métier incohérent | 409 Conflict |
| Données invalides | 422 Unprocessable Entity |

Ces contrôles confirment que l’API ne donne pas accès aux actions sensibles sans authentification ou sans rôle autorisé.

## 4. Vérification des secrets

Les fichiers sensibles ne doivent pas être versionnés dans Git.

Éléments à exclure :

```text
.env
accessguard.db
*.db-journal
*.db-wal
*.db-shm
.venv
__pycache__
```

Le fichier `.gitignore` protège la base SQLite locale, les fichiers d’environnement et les caches Python.

## 5. CI/CD GitHub Actions

Le projet utilise GitHub Actions pour exécuter automatiquement les tests lors des push et pull requests.

Le workflow CI doit :

1. récupérer le code ;
2. installer Python ;
3. installer les dépendances ;
4. lancer les tests avec Pytest ;
5. retourner un statut vert si les tests passent.

Un workflow vert confirme que le projet peut être validé sans casser les tests existants.

## 6. Risques identifiés

| Risque | Correction ou contrôle |
|---|---|
| Secrets exposés dans Git | Utilisation de `.gitignore` et `.env.example` |
| Base SQLite locale poussée par erreur | Exclusion de `accessguard.db` |
| Régression après ajout V3 | Exécution de `python -m pytest -v` |
| Mauvais rôle sur route sensible | Tests 401/403 |
| Mauvaise configuration Docker | Vérification avec `docker compose ps` |
| Mauvaise configuration monitoring | Vérification Prometheus/Grafana |

## 7. Captures de preuve

Captures prévues pour cette partie :

```text
Capture-V3-Irina-01-Tests-31-passed.png
Capture-V3-Irina-02-Gitignore-secrets-proteges.png
Capture-V3-Irina-03-GitHub-Actions-green.png
```

## 8. Conclusion

La partie tests, CI/CD et sécurité applicative confirme que la V3 reste stable après l’ajout du monitoring, de Docker Compose, de Prometheus, de Grafana et du prototype frontend.

Les tests automatisés passent, les routes sensibles restent protégées et les fichiers secrets sont exclus du versionnement.
