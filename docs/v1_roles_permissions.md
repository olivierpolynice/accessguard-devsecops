# AccessGuard V1 — Rôles et permissions

## Objectif

La V1 ajoute une authentification JWT et un contrôle des accès par rôle.

Chaque utilisateur doit se connecter avec son compte, recevoir un Bearer token, puis accéder uniquement aux routes autorisées par son rôle.

## Comptes de démonstration

| Rôle           | E-mail                                                                      | Mot de passe de démonstration |
| -------------- | --------------------------------------------------------------------------- | ----------------------------- |
| employee       | [alice.employee@asteriatech.local](mailto:alice.employee@asteriatech.local) | Employee123!                  |
| manager        | [marc.manager@asteriatech.local](mailto:marc.manager@asteriatech.local)     | Manager123!                   |
| it_admin       | [ines.itadmin@asteriatech.local](mailto:ines.itadmin@asteriatech.local)     | Admin123!                     |
| security_admin | [sam.security@asteriatech.local](mailto:sam.security@asteriatech.local)     | Security123!                  |

Ces mots de passe sont uniquement destinés à la démonstration locale. Ils ne doivent jamais être utilisés dans un environnement réel.

## Matrice des permissions

| Route                                               |                employee | manager | it_admin | security_admin |
| --------------------------------------------------- | ----------------------: | ------: | -------: | -------------: |
| GET /health                                         |                     Oui |     Oui |      Oui |            Oui |
| GET /resources                                      |                     Oui |     Oui |      Oui |            Oui |
| POST /auth/login                                    |                     Oui |     Oui |      Oui |            Oui |
| POST /access-requests                               |                     Oui |     Non |      Non |            Non |
| GET /access-requests                                | Ses demandes uniquement |     Oui |      Oui |            Non |
| GET /access-requests/{request_id}                   |   Sa demande uniquement |     Oui |      Oui |            Non |
| POST /access-requests/{request_id}/manager-decision |                     Non |     Oui |      Non |            Non |
| POST /access-requests/{request_id}/grant            |                     Non |     Non |      Oui |            Non |
| GET /access-grants                                  |                     Non |     Non |      Oui |            Non |
| POST /access-grants/{grant_id}/revoke               |                     Non |     Non |      Oui |            Non |
| GET /audit-logs                                     |                     Non |     Non |      Non |            Oui |

## Réponses de sécurité attendues

* Sans token Bearer sur une route protégée : `401 Unauthorized`.
* Token invalide, expiré ou mal formé : `401 Unauthorized`.
* Token valide mais rôle insuffisant : `403 Forbidden`.
* Token valide avec le bon rôle : la route applique ensuite les règles métier P0.

## Règles importantes

* Un employee peut créer une demande d’accès.
* Un manager peut approuver ou refuser une demande.
* Un it_admin peut attribuer ou révoquer un accès.
* Un security_admin peut consulter les journaux d’audit.
* Les routes `/health`, `/resources` et `/auth/login` restent publiques.
* Les règles métier P0 restent obligatoires, même avec un bon rôle.
