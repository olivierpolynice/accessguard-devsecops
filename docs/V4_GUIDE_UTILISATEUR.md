# Guide utilisateur — AccessGuard V4

## 1. Présentation

AccessGuard permet de gérer les demandes d'accès, les accès attribués et la traçabilité des actions au sein d'AsteriaTech.

## 2. Se connecter

1. Ouvrir la page de connexion.
2. Saisir son adresse e-mail (ex. : `alice.employee@asteriatech.local`).
3. Saisir son mot de passe (`demo1234` en démonstration).
4. Sélectionner son rôle dans la liste déroulante.
5. Cliquer sur le bouton **Se connecter**.
6. Vérifier l'apparition du tableau de bord.

En cas d'erreur, vérifier les informations saisies.

**Comptes de démonstration disponibles :**

| Compte | Rôle |
|---|---|
| alice.employee@asteriatech.local | Employee |
| marc.manager@asteriatech.local | Manager |
| ines.itadmin@asteriatech.local | IT Admin |
| sam.security@asteriatech.local | Security Admin |

Mot de passe commun : `demo1234`

## 3. Consulter le tableau de bord

Le tableau de bord présente les principaux indicateurs :

- demandes en attente (validation manager requise) ;
- accès actifs (accès actuellement ouverts) ;
- révocations récentes (actions sécurité) ;
- disponibilité de l'API.

Il affiche également les demandes récentes et le flux de validation en quatre étapes : Employee → Manager → IT Admin → Security.

## 4. Créer une demande d'accès

1. Ouvrir la section **Demandes d'accès**.
2. Choisir la ressource demandée dans la liste.
3. Saisir la date de début.
4. Saisir la date de fin.
5. Rédiger une justification claire.
6. Cliquer sur **Envoyer la demande**.

La demande passe au statut `PENDING_MANAGER` en attente de validation.

## 5. Valider une demande (rôle Manager)

1. Consulter les demandes au statut `PENDING`.
2. Sélectionner une demande.
3. Vérifier l'utilisateur, la ressource et la justification.
4. Cliquer sur **Approuver** ou **Refuser**.

Cette fonction est réservée aux utilisateurs ayant le rôle **Manager**.

## 6. Attribuer un accès (rôle IT Admin)

Une fois la demande approuvée par le Manager, l'IT Admin peut attribuer l'accès :

1. Ouvrir la section **Accès attribués**.
2. Sélectionner la demande approuvée.
3. Confirmer l'attribution.

L'accès passe au statut `ACTIVE`.

## 7. Révoquer un accès

Un accès actif peut être révoqué à tout moment :

1. Localiser l'accès dans la section **Accès attribués**.
2. Cliquer sur **Révoquer**.

L'accès passe au statut `REVOKED`. Cette action est irréversible.

## 8. Lire les logs d'audit

La section **Audit logs** indique pour chaque événement :

- la date et l'heure ;
- l'utilisateur ayant réalisé l'action ;
- l'action réalisée ;
- la ressource concernée ;
- le résultat de l'action.

## 9. Interpréter le monitoring

La section **Monitoring** affiche l'état général des services :

- `/metrics` : endpoint Prometheus exposant les métriques HTTP.
- **UP** : Prometheus interroge l'API toutes les 15 secondes.
- **Grafana** : visualisation des métriques collectées.

Un service disponible fonctionne normalement. Une alerte indique qu'un service doit être vérifié.

## 10. Déconnexion

Cliquer sur le bouton **Déconnexion** dans la barre de navigation pour quitter la session.