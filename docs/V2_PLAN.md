# AccessGuard — Plan de réalisation V2

## Objectif V2

Renforcer la sécurité de l’API AccessGuard afin que les routes sensibles soient réellement protégées par JWT et RBAC, que les actions importantes soient tracées dans les logs d’audit, et que les tests automatisés soient exécutés à chaque Push ou Pull Request.

## Point de départ

La V1 contient déjà :

- une API FastAPI fonctionnelle ;
- une authentification JWT ;
- des rôles utilisateurs ;
- la gestion des demandes d’accès ;
- l’attribution et la révocation des accès ;
- des logs d’audit ;
- des tests automatisés ;
- une intégration continue GitHub Actions.

## Tâches V2

- [ ] Vérifier les routes sensibles existantes.
- [ ] Définir la matrice RBAC finale.
- [ ] Vérifier les réponses 401 sans JWT.
- [ ] Vérifier les réponses 403 avec un rôle non autorisé.
- [ ] Protéger les routes métier sensibles avec JWT.
- [ ] Centraliser les permissions RBAC.
- [ ] Renforcer les logs d’audit.
- [ ] Ajouter les tests de sécurité V2.
- [ ] Mettre à jour le README.
- [ ] Préparer les captures V2.
- [ ] Vérifier GitHub Actions avant chaque fusion.

## Routes sensibles à contrôler

- `POST /access-requests`
- `GET /access-requests`
- `POST /access-requests/{request_id}/grant`
- `GET /access-grants`
- `POST /access-grants/{grant_id}/revoke`
- `GET /audit-logs`

## Résultats attendus

- Une route sensible appelée sans JWT retourne `401 Unauthorized`.
- Une route appelée avec un JWT valide mais un rôle insuffisant retourne `403 Forbidden`.
- Une route appelée avec le bon rôle retourne une réponse de succès.
- Les actions sensibles sont enregistrées dans les logs d’audit.
- Tous les tests passent localement et dans GitHub Actions.
## Constats de sécurité

- [ ] `GET /audit-logs` retourne actuellement `200 OK` sans JWT.
- [ ] La route doit exiger un JWT valide.
- [ ] La route doit être limitée aux rôles `it_admin` et `security_admin`.

- [ ] `POST /access-requests/{request_id}/grant` retourne actuellement `404` sans JWT.
- [ ] La route doit vérifier le JWT avant de chercher la demande.
- [ ] Sans JWT, la réponse attendue doit être `401 Unauthorized`.
- [ ] Avec un mauvais rôle, la réponse attendue doit être `403 Forbidden`.
- [ ] Seul le rôle `it_admin` doit pouvoir attribuer un accès.

- [ ] `POST /access-grants/{grant_id}/revoke` retourne actuellement `404` sans JWT.
- [ ] La route doit vérifier le JWT avant de chercher l’accès.
- [ ] Sans JWT, la réponse attendue doit être `401 Unauthorized`.
- [ ] Avec un rôle non autorisé, la réponse attendue doit être `403 Forbidden`.
- [ ] Les rôles autorisés doivent être `it_admin` et éventuellement `security_admin`.