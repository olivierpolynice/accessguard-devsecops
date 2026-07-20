# AccessGuard V5 — Bilan du sprint

## 1. Présentation

La V5 d’AccessGuard marque une étape importante dans l’évolution du projet. Elle complète les fonctionnalités précédentes avec une administration sécurisée des utilisateurs, une interface frontend adaptée aux rôles, des métriques métier et une validation technique renforcée.

Cette version a été réalisée dans le cadre du projet pédagogique DevSecOps consacré à l’entreprise fictive AsteriaTech.

## 2. Objectifs de la V5

Les objectifs principaux étaient :

- ajouter la gestion persistante des utilisateurs ;
- sécuriser les routes d’administration ;
- renforcer le contrôle d’accès par rôles ;
- finaliser le workflow des demandes d’accès ;
- améliorer l’interface React ;
- ajouter des métriques métier ;
- intégrer Prometheus et Grafana ;
- renforcer les tests et la CI/CD ;
- produire des preuves et une documentation complète.

## 3. Fonctionnalités réalisées

### 3.1 Gestion des utilisateurs

La V5 introduit une table `users` contenant :

- un identifiant unique ;
- une adresse e-mail unique ;
- une empreinte sécurisée du mot de passe ;
- un rôle ;
- un statut actif ou inactif ;
- les dates de création et de modification.

Les rôles disponibles sont :

- `employee` ;
- `manager` ;
- `it_admin` ;
- `security_admin`.

Le rôle `security_admin` peut :

- consulter les utilisateurs ;
- consulter un utilisateur précis ;
- créer un utilisateur ;
- modifier son rôle ;
- activer ou désactiver son compte.

Les mots de passe et les valeurs `password_hash` ne sont jamais exposés dans les réponses de l’API ni dans l’interface.

### 3.2 Routes utilisateurs

Les routes suivantes ont été ajoutées :

| Méthode | Route | Description |
|---|---|---|
| GET | `/users` | Lister les utilisateurs |
| GET | `/users/{id}` | Consulter un utilisateur |
| POST | `/users` | Créer un utilisateur |
| PATCH | `/users/{id}/role` | Modifier un rôle |
| PATCH | `/users/{id}/status` | Activer ou désactiver un compte |

Ces routes sont réservées au rôle `security_admin`.

### 3.3 Authentification et RBAC

L’authentification repose sur des jetons JWT.

Les autorisations sont réparties ainsi :

| Rôle | Autorisations principales |
|---|---|
| Employé | Consulter les ressources et créer une demande |
| Manager | Approuver ou refuser une demande |
| Administrateur IT | Attribuer ou révoquer un accès |
| Administrateur sécurité | Administrer les utilisateurs, consulter l’audit et le monitoring |

Les accès non autorisés retournent une réponse `403 Forbidden`.

Un utilisateur désactivé ne peut plus se connecter, même s’il possède le bon mot de passe.

### 3.4 Workflow des accès

Le workflow complet a été validé :

```text
PENDING_MANAGER
→ APPROVED ou REJECTED
→ GRANTED
→ REVOKED