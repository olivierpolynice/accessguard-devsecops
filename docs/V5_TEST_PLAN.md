# Plan de tests V5 — AccessGuard

## 1. Informations générales

- Projet : AccessGuard
- Version : V5
- Responsable validation : Irina Letsara
- Périmètre : tests, CI/CD, qualité et sécurité
- Branche : `feature/v5-irina`

## 2. Objectif

Ce plan définit les contrôles nécessaires pour valider AccessGuard V5.

La validation doit couvrir :

- les fonctionnalités V5 ;
- l’authentification ;
- la gestion des utilisateurs ;
- le RBAC ;
- le workflow des demandes d’accès ;
- les journaux d’audit ;
- le monitoring ;
- la sécurité des dépendances ;
- la non-régression des versions V1 à V4.

## 3. Stratégie de test

Les tests sont automatisés avec Pytest et FastAPI TestClient.

Chaque test doit :

- être indépendant ;
- réinitialiser les données nécessaires ;
- utiliser un token correspondant au rôle attendu ;
- vérifier le code HTTP ;
- vérifier le contenu de la réponse ;
- vérifier les messages d’erreur importants ;
- ne pas accepter un `404` comme preuve d’une protection `401` ou `403`.

## 4. Catégories

| Catégorie | Marqueur Pytest | Fichiers principaux |
|---|---|---|
| Authentification | `auth` | `test_auth.py`, `test_v5_security.py` |
| Utilisateurs | `users` | `test_users.py` |
| RBAC | `rbac` | `test_accessguard.py`, `test_v5_security.py` |
| Workflow | `workflow` | `test_v5_workflow.py` |
| Audit | `audit` | `test_v5_workflow.py` |
| Monitoring | `monitoring` | `test_v4_routes.py`, `test_v5_security.py` |
| Non-régression | `regression` | tests V1 à V4 |

## 5. Scénarios d’authentification

| ID | Scénario | Résultat attendu |
|---|---|---|
| AUTH-01 | Connexion valide | HTTP 200 et JWT |
| AUTH-02 | Mauvais mot de passe | HTTP 401 |
| AUTH-03 | Utilisateur inconnu | HTTP 401 |
| AUTH-04 | Utilisateur inactif | HTTP 401 ou 403 |
| AUTH-05 | Token expiré | HTTP 401 |
| AUTH-06 | Token invalide | HTTP 401 |
| AUTH-07 | Route protégée sans JWT | HTTP 401 |

## 6. Scénarios utilisateurs

| ID | Scénario | Résultat attendu |
|---|---|---|
| USER-01 | Création par un administrateur | HTTP 201 |
| USER-02 | Création d’un doublon | HTTP 409 |
| USER-03 | Création par un employé | HTTP 403 |
| USER-04 | Modification d’un rôle | HTTP 200 |
| USER-05 | Attribution d’un rôle invalide | HTTP 422 |
| USER-06 | Désactivation d’un utilisateur | HTTP 200 |
| USER-07 | Connexion d’un compte désactivé | HTTP 401 ou 403 |
| USER-08 | Consultation sans JWT | HTTP 401 |

## 7. Scénarios RBAC

| Route | Sans JWT | Employee | Manager | IT admin | Security admin |
|---|---:|---:|---:|---:|---:|
| `/me` | 401 | 200 | 200 | 200 | 200 |
| `/dashboard/summary` | 401 | 200 | 200 | 200 | 200 |
| `/access-requests` | 401 | 200 | 200 | 200 | 200 |
| Manager decision | 401 | 403 | 200 | 403 | 403 |
| Grant | 401 | 403 | 403 | 201 | 403 |
| Revoke | 401 | 403 | 403 | 200 | 200 |
| `/access-grants` | 401 | 200 | 403 | 200 | 200 |
| `/audit-logs` | 401 | 403 | 403 | 200 | 200 |
| `/users` | 401 | 403 | 403 | attendu selon V5 | attendu selon V5 |

## 8. Scénarios du workflow

Le scénario principal est :

```text
Demande
  ↓
Approbation du manager
  ↓
Attribution par l’administrateur IT
  ↓
Révocation
  ↓
Contrôle des journaux d’audit