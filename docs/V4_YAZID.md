# V4 — Yazid — Backend / API / Intégration

Branche : `feature/v4-yazid` (basée sur `main` à jour, après merge V3).

## Contexte

Avant de commencer, un audit de l'état réel de `main` a révélé deux problèmes hérités
de la résolution de conflit V3, tous deux signalés à l'équipe :

1. **Bug fonctionnel mineur** : `Instrumentator().instrument(app)` (middleware Prometheus)
   était appelé deux fois dans `app/main.py` — l'ancien appel d'un merge V3 mal résolu
   était resté à côté du bon appel. Corrigé dans ce lot, car le fichier était de toute
   façon modifié pour ajouter les nouvelles routes.
2. **Régression de configuration** (traitée séparément, hors de ce lot) : le port hôte
   Prometheus était repassé de `9091` à `9090` pendant le merge V3, recréant un conflit
   avec un autre projet local. Correction sur la branche dédiée `fix/v4-prometheus-port-conflict`.

## Objectif V4 (Yazid)

Ajouter des routes utiles au frontend pour préparer sa connexion au backend, sans casser
le RBAC existant, avec tests associés.

## Routes ajoutées

### 1. `GET /me`

Retourne l'identité de l'utilisateur authentifié à partir du JWT.

**Réponse (200)** :
```json
{
  "email": "alice.employee@asteriatech.local",
  "role": "employee"
}
```

**Sans token** : `401 Unauthorized`.

**Usage frontend** : le frontend appelle cette route après le login pour savoir qui est
connecté et quel dashboard afficher, sans décoder le JWT côté client.

### 2. `GET /dashboard/summary`

Retourne des compteurs agrégés pour alimenter les cartes du dashboard.

**Réponse (200)** :
```json
{
  "pending_requests": 8,
  "active_grants": 24,
  "revoked_grants": 3,
  "audit_logs": 42
}
```

**Règles RBAC appliquées** :
- `employee` : compteurs limités à ses propres demandes et accès.
- `manager`, `it_admin`, `security_admin` : compteurs sur l'ensemble du système.
- `audit_logs` : total global pour tout rôle authentifié (aucun détail sensible n'est
  exposé par un simple nombre — le détail des logs reste réservé à `it_admin`/
  `security_admin` via `/audit-logs`, inchangé).

**Sans token** : `401 Unauthorized`.

### 3. `GET /access-requests/status/{status}`

Retourne les demandes d'accès filtrées par statut.

**Statuts valides** : `PENDING_MANAGER`, `APPROVED`, `REFUSED`, `GRANTED`.

**Comportement** :
- Statut inconnu → `422 Unprocessable Entity` (pas une liste vide silencieuse).
- `employee` → uniquement ses propres demandes filtrées.
- Autres rôles → toutes les demandes filtrées.
- Sans token → `401`.

### 4. `GET /access-grants/active`

Retourne uniquement les accès dont `status == "ACTIVE"` (exclut les révoqués).

**Comportement** : reprend exactement les règles de `GET /access-grants` existant :
- `manager` → `403 Forbidden` (ne consulte pas les accès attribués).
- `employee` → uniquement ses propres accès actifs.
- `it_admin` / `security_admin` → tous les accès actifs.
- Sans token → `401`.

## Tests ajoutés (`tests/test_v4_routes.py`)

11 tests, dont les 4 explicitement demandés par le plan V4 :

| Test | Vérifie |
|---|---|
| `test_get_me_with_valid_token` | /me retourne email + rôle corrects |
| `test_get_me_without_token_401` | /me exige un JWT |
| `test_dashboard_summary_employee` | compteurs scopés à l'employee, audit_logs global |
| `test_dashboard_summary_it_admin` | compteurs globaux pour it_admin |
| `test_dashboard_summary_requires_jwt` | /dashboard/summary exige un JWT |
| `test_list_access_requests_by_status_employee_scoped` | filtrage + scoping employee |
| `test_list_access_requests_by_status_invalid_status_422` | statut invalide → 422 |
| `test_list_access_requests_by_status_requires_jwt` | route exige un JWT |
| `test_list_active_access_grants_it_admin` | seuls les ACTIVE sont retournés |
| `test_list_active_access_grants_manager_forbidden` | manager reçoit 403 |
| `test_list_active_access_grants_requires_jwt` | route exige un JWT |

**Résultat** : 42/42 tests passent (31 existants + 11 nouveaux), aucune régression.

## Commandes de vérification locale

```powershell
python -m pytest -q
# 42 passed
```

## Captures à réaliser

Voir section dédiée dans le livrable Word `AccessGuard_V4_Yazid_Backend.docx` et la
checklist ci-dessous. Toutes les captures Swagger (`/docs`) doivent être prises avec un
token valide collé dans "Authorize", pour chacun des 4 rôles pertinents.

- [ ] `GET /me` — réponse 200 avec un token employee.
- [ ] `GET /dashboard/summary` — réponse 200, une fois avec un token employee, une fois
      avec un token it_admin (pour montrer la différence de scope).
- [ ] `GET /access-requests/status/PENDING_MANAGER` — réponse 200.
- [ ] `GET /access-grants/active` — réponse 200 (avec it_admin) et réponse 403 (avec manager).
- [ ] Terminal `python -m pytest -q` montrant "42 passed".

## Limites connues / points ouverts

- Le plan V4 mentionne "security_admin voit audit/sécurité" sans préciser si ce rôle doit
  avoir un comportement différent d'`it_admin` sur les nouvelles routes. Actuellement les
  deux rôles sont traités de façon identique (accès large) sur `/dashboard/summary` et
  `/access-grants/active`. À confirmer avec l'équipe si une distinction plus fine est
  attendue.
- Pull Request : la branche `feature/v4-yazid` est poussée sur origin, le lien de création
  de PR a été généré par GitHub mais la PR n'a pas encore été ouverte formellement.
