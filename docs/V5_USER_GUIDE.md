# AccessGuard V5 — Guide utilisateur

## 1. Présentation

AccessGuard est une application de gestion des demandes et des autorisations d'accès aux ressources de l'entreprise fictive AsteriaTech.

Le parcours principal est le suivant :

1. un employé crée une demande d'accès ;
2. un manager approuve ou refuse la demande avec une justification ;
3. un administrateur IT attribue l'accès après approbation ;
4. l'administrateur IT peut ensuite révoquer cet accès ;
5. l'administrateur sécurité gère les utilisateurs, consulte l'audit et accède au monitoring.

## 2. Prérequis

Avant de démarrer AccessGuard, vérifier la présence des outils suivants :

- Git ;
- Docker Desktop et Docker Compose ;
- Node.js et npm pour lancer le frontend en développement ;
- un navigateur récent ;
- Visual Studio Code, recommandé pour travailler sur le projet.

## 3. Démarrer AccessGuard

### 3.1. Ouvrir le projet

Dans PowerShell :

```powershell
cd C:\Users\Olivi\OneDrive\Documents\DevOps\accessguard-devsecops
```

### 3.2. Démarrer les services Docker

```powershell
docker compose up --build -d
```

Vérifier leur état :

```powershell
docker compose ps
```

Les services attendus sont notamment :

- API AccessGuard : `http://localhost:8000` ;
- documentation Swagger : `http://localhost:8000/docs` ;
- endpoint de santé : `http://localhost:8000/health` ;
- Prometheus : `http://localhost:9090` ;
- Grafana : `http://localhost:3000`.

### 3.3. Démarrer le frontend

Ouvrir un second terminal :

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir ensuite :

```text
http://localhost:5173
```

Pour arrêter les services Docker :

```powershell
docker compose down
```

## 4. Se connecter

1. ouvrir `http://localhost:5173` ;
2. saisir l'adresse e-mail du compte ;
3. saisir le mot de passe correspondant ;
4. cliquer sur **Se connecter** ;
5. vérifier l'e-mail et le rôle affichés dans l'en-tête.

La session utilise un token JWT. Si la session expire, AccessGuard demande une nouvelle connexion.

## 5. Comptes de démonstration

| Utilisateur | Adresse e-mail | Rôle | Utilisation |
|---|---|---|---|
| Alice | `alice.employee@asteriatech.local` | `employee` | Créer et suivre ses demandes |
| Marc | `marc.manager@asteriatech.local` | `manager` | Approuver ou refuser les demandes |
| Inès | `ines.itadmin@asteriatech.local` | `it_admin` | Attribuer et révoquer les accès |
| Paul | `paul.security@asteriatech.local` | `security_admin` | Administrer les utilisateurs, l'audit et le monitoring |

Les mots de passe de démonstration sont ceux configurés dans `app/seed.py` ou dans la configuration locale du projet. Ne jamais publier de mot de passe de production dans ce guide.

## 6. Droits de chaque rôle

| Fonction | Employee | Manager | IT Admin | Security Admin |
|---|:---:|:---:|:---:|:---:|
| Consulter les ressources | Oui | Non | Non | Non |
| Créer une demande | Oui | Non | Non | Non |
| Consulter ses demandes | Oui | Non | Non | Non |
| Approuver ou refuser une demande | Non | Oui | Non | Non |
| Attribuer un accès | Non | Non | Oui | Non |
| Révoquer un accès | Non | Non | Oui | Non |
| Administrer les utilisateurs | Non | Non | Non | Oui |
| Consulter l'audit | Non | Non | Non | Oui |
| Accéder au monitoring | Non | Non | Non | Oui |

Le backend contrôle réellement ces autorisations. Masquer un menu dans le frontend ne remplace pas le contrôle RBAC de l'API.

## 7. Utiliser le tableau de bord

Le contenu du tableau de bord dépend du rôle connecté.

### Employee

- nombre de ressources disponibles ;
- demandes en attente ;
- accès actifs ;
- bouton de création d'une demande ;
- demandes récentes.

### Manager

- demandes en attente ;
- nombre total de demandes ;
- accès à la page de validation ;
- résumé des demandes à examiner.

### IT Admin

- demandes approuvées ;
- accès à attribuer ;
- accès actifs ;
- accès révoqués ;
- accès à la gestion des autorisations.

### Security Admin

- nombre total d'utilisateurs ;
- utilisateurs actifs et inactifs ;
- derniers événements d'audit ;
- accès à la supervision.

## 8. Créer une demande d'accès

Cette action est réalisée avec Alice ou un autre compte `employee`.

1. se connecter avec le compte employé ;
2. ouvrir **Mes demandes** ;
3. cliquer sur **Nouvelle demande** ;
4. sélectionner une ressource ;
5. saisir une justification professionnelle ;
6. renseigner les dates de début et de fin ;
7. vérifier que la date de fin est postérieure ou égale à la date de début ;
8. cliquer sur **Valider la demande**.

Le message **Demande envoyée avec succès.** doit apparaître. Le statut initial est **En attente** (`PENDING_MANAGER`).

## 9. Approuver ou refuser une demande

Cette action est réalisée avec Marc ou un autre compte `manager`.

1. se connecter avec le compte manager ;
2. ouvrir **Demandes à valider** ;
3. consulter l'employé, la ressource, les dates et la justification ;
4. saisir une justification de manager d'au moins cinq caractères ;
5. cliquer sur **Approuver** ou **Refuser** ;
6. confirmer l'action si une confirmation est affichée.

États utilisés par le backend V5 :

- `APPROVED` : demande approuvée ;
- `REFUSED` : demande refusée.

L'ancienne valeur `REJECTED` peut être reconnue pour l'affichage, mais la décision envoyée au backend doit utiliser `REFUSED`.

## 10. Attribuer un accès

Cette action est réalisée avec Inès ou un autre compte `it_admin`.

1. se connecter avec le compte administrateur IT ;
2. ouvrir **Gestion des accès** ;
3. cliquer sur **Attribuer un accès** ;
4. sélectionner une demande approuvée ;
5. saisir une justification d'attribution d'au moins cinq caractères ;
6. cliquer sur **Confirmer l'attribution**.

Le message **Accès attribué avec succès.** doit apparaître. L'accès prend le statut **Actif** ou `GRANTED`.

## 11. Révoquer un accès

1. rester connecté avec le compte `it_admin` ;
2. repérer un accès actif dans **Gestion des accès** ;
3. saisir un motif de révocation d'au moins cinq caractères ;
4. cliquer sur **Révoquer** ;
5. lire la fenêtre de confirmation ;
6. cliquer sur **Annuler** pour abandonner ou sur **Confirmer la révocation** pour continuer.

La confirmation indique que l'action prendra effet immédiatement. Après confirmation, le statut devient **Révoqué** (`REVOKED`) et le message **Accès révoqué.** apparaît.

## 12. Gérer les utilisateurs

Cette fonctionnalité est réservée à Paul ou à un autre compte `security_admin`.

### 12.1. Créer un utilisateur

1. ouvrir **Utilisateurs** ;
2. cliquer sur **Ajouter un utilisateur** ;
3. saisir l'adresse e-mail ;
4. saisir un mot de passe conforme aux règles du backend ;
5. sélectionner le rôle ;
6. valider la création.

Le message **Utilisateur créé.** doit apparaître.

Le tableau ne doit jamais afficher le mot de passe ni le champ `password_hash`.

### 12.2. Modifier un rôle

1. cliquer sur **Modifier** ;
2. sélectionner le nouveau rôle ;
3. confirmer si le rôle est sensible ;
4. enregistrer la modification.

Le message **Rôle mis à jour.** doit apparaître.

### 12.3. Désactiver ou réactiver un utilisateur

1. cliquer sur **Désactiver** ;
2. vérifier l'utilisateur concerné ;
3. confirmer la désactivation ;
4. vérifier que le badge devient **Inactif**.

Un utilisateur désactivé ne peut plus se connecter. Il peut ensuite être réactivé avec le bouton **Activer**.

## 13. Consulter le journal d'audit

1. se connecter avec Paul ;
2. ouvrir **Audit** ;
3. consulter la date, l'utilisateur, l'action, la ressource et le résultat ;
4. cliquer sur **Actualiser** pour recharger les événements ;
5. utiliser **Exporter le journal** si l'export est disponible.

Le journal contient notamment :

- les demandes créées ;
- les décisions des managers ;
- les accès attribués ;
- les accès révoqués ;
- les opérations d'administration des utilisateurs.

Utiliser des justifications professionnelles lors des démonstrations afin que les captures et les événements d'audit soient lisibles.

## 14. Consulter le monitoring

1. se connecter avec Paul ;
2. ouvrir **Monitoring** ;
3. accéder à Prometheus pour consulter les métriques ;
4. accéder à Grafana pour consulter le dashboard AccessGuard V5.

Métriques métier principales :

- `accessguard_login_success_total` ;
- `accessguard_login_failure_total` ;
- `accessguard_access_requests_total` ;
- `accessguard_manager_approvals_total` ;
- `accessguard_manager_refusals_total` ;
- `accessguard_access_grants_total` ;
- `accessguard_access_revocations_total` ;
- `accessguard_forbidden_actions_total`.

## 15. Signification des badges

| État backend | Affichage | Couleur |
|---|---|---|
| `PENDING_MANAGER` | En attente | Orange |
| `APPROVED` | Approuvée | Bleu |
| `REFUSED` / `REJECTED` | Refusée | Rouge |
| `ACTIVE` | Actif | Vert |
| `GRANTED` | Accès attribué | Vert |
| `REVOKED` | Révoqué | Rouge foncé ou gris |
| `INACTIVE` | Inactif | Gris |

## 16. Erreurs fréquentes

### Impossible de contacter le serveur

Vérifier Docker :

```powershell
docker compose ps
docker compose logs accessguard-api --tail=100
```

Tester ensuite :

```text
http://localhost:8000/health
```

### Erreur 400

La demande envoyée est incorrecte. Vérifier les champs et le format du corps JSON.

### Erreur 401

La session est absente, invalide ou expirée. Se déconnecter puis se reconnecter.

### Erreur 403

Le compte connecté ne possède pas le rôle nécessaire. Utiliser le compte adapté à l'action.

### Erreur 404

L'élément demandé n'existe pas ou a été supprimé.

### Erreur 409

L'élément existe déjà. Cette erreur apparaît notamment lors de la création d'un utilisateur avec une adresse e-mail déjà enregistrée.

### Erreur 422

Une ou plusieurs informations sont invalides. Vérifier les champs obligatoires, les dates, le rôle et la longueur des justifications.

### Erreur 500

Une erreur interne est survenue. Consulter les logs de l'API :

```powershell
docker compose logs accessguard-api --tail=100
```

### Token JWT visible mais requêtes en 401

Vérifier que le frontend envoie l'en-tête :

```text
Authorization: Bearer <token>
```

Ne jamais publier un token JWT dans une capture ou un rapport.

### Le conteneur API est unhealthy

Reconstruire les services :

```powershell
docker compose down
docker compose up --build -d
docker compose ps
```

### Une modification frontend n'apparaît pas

Enregistrer les fichiers puis recharger avec `Ctrl + F5`. Vérifier également que Vite est toujours démarré.

## 17. Vérifications avant démonstration

Dans `frontend` :

```powershell
npm run lint
npm run build
```

À la racine du projet :

```powershell
pytest
docker compose ps
```

Avant la présentation, vérifier le parcours complet :

```text
Employé crée → Manager décide → IT Admin attribue → IT Admin révoque → Security Admin consulte l'audit
```

## 18. Captures recommandées

Enregistrer les captures dans `docs/screenshots/v5/` avec des noms explicites :

```text
01_login_employee.png
02_employee_dashboard.png
03_access_request_created.png
04_manager_pending_requests.png
05_manager_decision.png
06_access_granted.png
07_revoke_confirmation.png
08_access_revoked.png
09_users_administration.png
10_user_status_confirmation.png
11_audit_log.png
12_security_dashboard.png
13_monitoring.png
14_frontend_lint.png
15_frontend_build.png
```

Ne pas inclure de mot de passe, de token JWT ou d'autre secret dans les captures.