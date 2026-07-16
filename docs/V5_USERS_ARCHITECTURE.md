V5 — Architecture de gestion des utilisateurs
1. Objectif

La version V5 introduit une gestion persistante des utilisateurs dans SQLite.

Avant cette évolution, les comptes pouvaient être définis directement dans le code ou dans des structures temporaires. La V5 centralise désormais :

les identités ;
les mots de passe hashés ;
les rôles ;
le statut actif ou inactif ;
les dates de création et de modification.
2. Vue d’ensemble
Client / Swagger / Frontend
            |
            v
       API FastAPI
            |
     +------+------+
     |             |
     v             v
Authentification  Routes /users
     |             |
     +------+------+
            |
            v
    User Repository
            |
            v
       SQLite users
3. Flux d’authentification
1. Le client envoie email + mot de passe
2. L’API recherche l’utilisateur dans SQLite
3. L’API vérifie le hash du mot de passe
4. L’API vérifie que l’utilisateur est actif
5. L’API génère un JWT
6. Le client utilise le JWT pour accéder aux routes protégées

Le JWT contient au minimum :

{
  "sub": "paul.security@asteriatech.local",
  "role": "security_admin"
}

Selon l’implémentation, il peut également contenir :

{
  "exp": 1784220000
}
4. Modèle de données
Table users
Colonne	Description
id	Identifiant unique
email	Adresse email unique
password_hash	Mot de passe hashé
role	Rôle RBAC
is_active	Autorise ou bloque la connexion
created_at	Date de création
updated_at	Date de modification

Exemple logique :

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

Une contrainte applicative doit limiter les rôles à :

employee
manager
it_admin
security_admin
5. Séparation des responsabilités
app/database.py

Responsabilités :

création de la connexion SQLite ;
initialisation de la base ;
création des tables ;
gestion éventuelle des transactions.
app/seed.py

Responsabilités :

création des utilisateurs de démonstration ;
création des ressources initiales ;
prévention des doublons ;
exécution idempotente.
app/auth.py

Responsabilités :

recherche de l’utilisateur ;
vérification du mot de passe ;
contrôle du statut actif ;
génération et validation des JWT ;
récupération de l’utilisateur courant.
app/schemas.py

Responsabilités :

validation des entrées ;
validation des rôles ;
format des réponses ;
exclusion du hash de mot de passe.
app/user_repository.py

Responsabilités :

création d’utilisateur ;
recherche par ID ou email ;
liste des utilisateurs ;
modification du rôle ;
modification du statut.
Routes /users

Responsabilités :

exposition des endpoints HTTP ;
contrôle RBAC ;
conversion des erreurs métier en réponses HTTP ;
codes 401, 403, 404, 409 et 422.
6. Schémas Pydantic
UserCreate

Exemple :

{
  "email": "nouveau.employee@asteriatech.local",
  "password": "AccessGuard123!",
  "role": "employee",
  "is_active": true
}
UserResponse

Exemple :

{
  "id": 5,
  "email": "nouveau.employee@asteriatech.local",
  "role": "employee",
  "is_active": true,
  "created_at": "2026-07-16T12:00:00Z",
  "updated_at": "2026-07-16T12:00:00Z"
}

Le champ suivant ne doit jamais apparaître :

password_hash
UserRoleUpdate
{
  "role": "manager"
}
UserStatusUpdate
{
  "is_active": false
}
7. Routes utilisateurs
Liste des utilisateurs
GET /users

Autorisation :

security_admin

Réponse attendue :

[
  {
    "id": 1,
    "email": "alice.employee@asteriatech.local",
    "role": "employee",
    "is_active": true
  }
]
Consulter un utilisateur
GET /users/{user_id}

Résultats possibles :

Code	Description
200	Utilisateur trouvé
401	Jeton absent ou invalide
403	Rôle non autorisé
404	Utilisateur inexistant
Créer un utilisateur
POST /users

Exemple :

{
  "email": "nouveau.employee@asteriatech.local",
  "password": "AccessGuard123!",
  "role": "employee",
  "is_active": true
}

Résultats possibles :

Code	Description
201	Utilisateur créé
401	Jeton absent ou invalide
403	Rôle non autorisé
409	Adresse email déjà utilisée
422	Requête invalide
Modifier le rôle
PATCH /users/{user_id}/role

Exemple :

{
  "role": "manager"
}

Le champ updated_at doit être actualisé.

Modifier le statut
PATCH /users/{user_id}/status

Exemple de désactivation :

{
  "is_active": false
}

Un utilisateur désactivé :

reste présent dans la base ;
conserve son historique ;
ne peut plus obtenir de nouveau JWT ;
peut être réactivé ultérieurement.
8. Matrice RBAC
Route ou fonction	Employee	Manager	IT Admin	Security Admin
POST /auth/login	Oui	Oui	Oui	Oui
GET /resources	Oui	Oui	Oui	Oui
POST /access-requests	Oui	Non	Non	Non
Décision manager	Non	Oui	Non	Non
Attribution d’accès	Non	Non	Oui	Non
Révocation d’accès	Non	Non	Oui	Non
Lecture des audits	Non	Non	Non	Oui
GET /users	Non	Non	Non	Oui
GET /users/{id}	Non	Non	Non	Oui
POST /users	Non	Non	Non	Oui
Modification du rôle	Non	Non	Non	Oui
Modification du statut	Non	Non	Non	Oui
9. Sécurité
Hashage des mots de passe

Les mots de passe doivent être hashés avant insertion dans SQLite.

La comparaison doit être réalisée avec une fonction de vérification sécurisée.

À éviter :

if password == stored_password:
    ...

Comportement attendu :

verify_password(plain_password, password_hash)
Protection contre l’énumération

Les erreurs de connexion ne doivent pas révéler précisément si :

l’adresse email existe ;
le mot de passe est incorrect.

Une réponse générique est préférable :

Identifiants invalides
Statut des utilisateurs

Le contrôle de is_active doit être réalisé avant la génération du JWT.

Protection des routes

La vérification RBAC doit être centralisée dans une dépendance FastAPI ou une fonction commune afin d’éviter la duplication.

10. Choix techniques
Pourquoi SQLite ?

SQLite est adapté à cette version pédagogique car il est :

simple à initialiser ;
léger ;
compatible avec Docker ;
suffisant pour une démonstration locale ;
facile à sauvegarder.
Limites de SQLite

SQLite devient moins adapté lorsque :

plusieurs instances de l’API écrivent simultanément ;
le volume d’utilisateurs augmente fortement ;
une haute disponibilité est requise ;
des migrations complexes doivent être gérées.

Une évolution vers PostgreSQL pourra être envisagée.

11. Évolutions possibles
migrations Alembic ;
PostgreSQL ;
refresh tokens ;
changement de mot de passe ;
mot de passe oublié ;
authentification multifacteur ;
annuaire LDAP ou Active Directory ;
révocation des sessions ;
journalisation des modifications utilisateur ;
permissions plus fines que les rôles actuels ;
interface graphique Security Admin.
4. docs/V5_USERS_DEMO.md
V5 — Démonstration de la gestion des utilisateurs
1. Objectif

Cette démonstration valide les fonctionnalités suivantes :

authentification depuis SQLite ;
connexion d’un utilisateur actif ;
refus d’un utilisateur inactif ;
protection RBAC des routes /users ;
création d’un utilisateur ;
gestion des conflits ;
modification du rôle ;
désactivation et réactivation ;
absence du hash dans les réponses.
2. Préparer l’environnement

Démarrer le projet :

docker compose up --build

Vérifier les conteneurs :

docker compose ps

Vérifier l’API :

http://localhost:8000/health

Ouvrir Swagger :

http://localhost:8000/docs
3. Comptes de test
Rôle	Email	Mot de passe
Employee	alice.employee@asteriatech.local	AccessGuard123!
Manager	marc.manager@asteriatech.local	AccessGuard123!
IT Admin	ines.itadmin@asteriatech.local	AccessGuard123!
Security Admin	paul.security@asteriatech.local	AccessGuard123!
4. Test 1 — Connexion Security Admin

Appeler :

POST /auth/login

Corps :

{
  "email": "paul.security@asteriatech.local",
  "password": "AccessGuard123!"
}

Résultat attendu :

200 OK

La réponse doit contenir :

{
  "access_token": "<JWT>",
  "token_type": "bearer"
}

Capture :

03_v5_login_sqlite_success.png
5. Ajouter le jeton dans Swagger
Copier le jeton.
Cliquer sur Authorize.
Saisir :
Bearer <JWT>
Valider.
6. Test 2 — Lister les utilisateurs

Avec le jeton Security Admin :

GET /users

Résultat attendu :

200 OK

La réponse doit contenir les quatre comptes de démonstration.

Vérifier que les champs suivants ne sont pas présents :

password
password_hash
7. Test 3 — Vérifier le refus RBAC

Se connecter avec :

alice.employee@asteriatech.local

Appeler ensuite :

GET /users

Résultat attendu :

403 Forbidden

Répéter le test avec les rôles :

manager
it_admin

Résultat attendu :

403 Forbidden

Conclusion attendue :

Seul security_admin peut administrer les utilisateurs.
8. Test 4 — Créer un utilisateur

Avec le jeton Security Admin :

POST /users

Corps :

{
  "email": "demo.employee@asteriatech.local",
  "password": "AccessGuard123!",
  "role": "employee",
  "is_active": true
}

Résultat attendu :

201 Created

Exemple de réponse :

{
  "id": 5,
  "email": "demo.employee@asteriatech.local",
  "role": "employee",
  "is_active": true,
  "created_at": "2026-07-16T12:00:00Z",
  "updated_at": "2026-07-16T12:00:00Z"
}

Le hash du mot de passe ne doit pas apparaître.

9. Test 5 — Tester un email déjà utilisé

Relancer la même requête :

POST /users

avec :

{
  "email": "demo.employee@asteriatech.local",
  "password": "AccessGuard123!",
  "role": "employee",
  "is_active": true
}

Résultat attendu :

409 Conflict
10. Test 6 — Consulter un utilisateur

Appeler :

GET /users/5

Remplacer 5 par l’identifiant réellement retourné.

Résultat attendu :

200 OK

Tester également un identifiant inexistant :

GET /users/99999

Résultat attendu :

404 Not Found
11. Test 7 — Modifier le rôle

Appeler :

PATCH /users/5/role

Corps :

{
  "role": "manager"
}

Résultat attendu :

200 OK

Vérifier que :

{
  "role": "manager"
}

est retourné.

Tester ensuite un rôle invalide :

{
  "role": "super_admin"
}

Résultat attendu :

422 Unprocessable Entity
12. Test 8 — Désactiver l’utilisateur

Appeler :

PATCH /users/5/status

Corps :

{
  "is_active": false
}

Résultat attendu :

200 OK

Vérifier que la réponse contient :

{
  "is_active": false
}
13. Test 9 — Vérifier le refus de connexion

Essayer de se connecter avec :

POST /auth/login

Corps :

{
  "email": "demo.employee@asteriatech.local",
  "password": "AccessGuard123!"
}

Résultat attendu :

401 Unauthorized

ou :

403 Forbidden

selon le choix retenu dans l’implémentation.

Capture :

04_v5_inactive_user_denied.png
14. Test 10 — Réactiver l’utilisateur

Avec le compte Security Admin :

PATCH /users/5/status

Corps :

{
  "is_active": true
}

Résultat attendu :

200 OK

L’utilisateur doit ensuite pouvoir se connecter de nouveau.

15. Tests automatisés

Lancer tous les tests :

pytest -v

Dans Docker :

docker compose exec accessguard-api pytest -v

Lancer uniquement les tests utilisateurs :

pytest -v tests/test_users.py

Résultat de référence observé pendant la V5 :

78 passed, 10 skipped, 1 warning

Les tests ignorés doivent être vérifiés après l’implémentation des routes utilisateurs afin de confirmer qu’ils peuvent être réactivés.

16. Captures disponibles
Fichier	Validation
02_v5_users_table_created.png	Table SQLite users
03_v5_login_sqlite_success.png	Connexion SQLite réussie
04_v5_inactive_user_denied.png	Utilisateur inactif refusé
05_v5_security_users_admin.png	Routes utilisateurs accessibles au Security Admin

Emplacement recommandé :

docs/screenshots/v5/
17. Résultat final attendu

La démonstration est validée lorsque :

les quatre comptes de test existent ;
les mots de passe sont hashés ;
le login utilise SQLite ;
le JWT contient le rôle ;
un utilisateur inactif ne peut pas se connecter ;
seul security_admin accède aux routes /users ;
la création d’un utilisateur retourne 201 ;
un email dupliqué retourne 409 ;
un utilisateur absent retourne 404 ;
un rôle invalide retourne 422 ;
les réponses ne contiennent aucun hash ;
les tests automatisés passent.
18. Limites de la démonstration

Cette démonstration ne couvre pas encore :

la réinitialisation du mot de passe ;
le changement de mot de passe ;
la suppression définitive d’un compte ;
l’authentification multifacteur ;
les refresh tokens ;
la révocation immédiate d’un JWT déjà émis ;
l’administration complète depuis l’interface frontend ;
l’intégration LDAP ou Active Directory.