5 — Plan de travail d’Olivier
1. Objectif général

L’objectif de la version V5 est de remplacer progressivement les comptes définis directement dans le code par une véritable gestion des utilisateurs stockés dans SQLite.

Cette évolution doit permettre :

de centraliser les utilisateurs dans la base de données ;
de sécuriser les mots de passe ;
d’utiliser les utilisateurs SQLite lors de la connexion ;
d’administrer les utilisateurs avec des routes protégées ;
de renforcer les règles RBAC ;
de documenter et tester toutes les fonctionnalités.
2. Périmètre du travail d’Olivier

Olivier est responsable de l’intégration backend de la gestion des utilisateurs.

Son périmètre comprend :

la création de la table users ;
la création des comptes de démonstration ;
l’adaptation de l’authentification ;
la création des schémas Pydantic ;
la création du repository utilisateur ;
la création des routes /users ;
la protection RBAC des routes ;
la vérification des tests ;
la production des captures ;
la mise à jour de la documentation finale.
3. Étapes de réalisation
Étape 1 — Créer la table users

Créer une table SQLite avec les colonnes suivantes :

Colonne	Type	Contraintes
id	INTEGER	Clé primaire
email	TEXT	Unique, obligatoire
password_hash	TEXT	Obligatoire
role	TEXT	Rôle autorisé
is_active	BOOLEAN	Actif par défaut
created_at	DATETIME	Date de création
updated_at	DATETIME	Date de dernière modification

Rôles autorisés :

employee
manager
it_admin
security_admin

Critères de validation :

la table est créée automatiquement ;
l’adresse email est unique ;
aucun mot de passe en clair n’est stocké ;
les dates sont enregistrées.

Capture associée :

02_v5_users_table_created.png
Étape 2 — Créer les comptes de démonstration

Créer un seed idempotent contenant quatre utilisateurs :

Email	Rôle
alice.employee@asteriatech.local	employee
marc.manager@asteriatech.local	manager
ines.itadmin@asteriatech.local	it_admin
paul.security@asteriatech.local	security_admin

Mot de passe pédagogique commun :

AccessGuard123!

Le script de seed doit être idempotent : plusieurs exécutions ne doivent pas créer de doublons.

Étape 3 — Adapter l’authentification SQLite

Modifier la route :

POST /auth/login

Le système doit :

rechercher l’utilisateur par email ;
vérifier le hash du mot de passe ;
vérifier que is_active vaut true ;
générer un JWT ;
placer l’email et le rôle dans le jeton.

Cas attendus :

Situation	Résultat
Identifiants corrects	200
Email inconnu	401
Mot de passe incorrect	401
Utilisateur désactivé	401 ou 403 selon l’implémentation

Captures associées :

03_v5_login_sqlite_success.png
04_v5_inactive_user_denied.png
Étape 4 — Créer les schémas Pydantic

Créer les schémas suivants :

UserCreate
UserResponse
UserRoleUpdate
UserStatusUpdate

Règles :

UserCreate accepte l’email, le mot de passe, le rôle et éventuellement le statut ;
UserResponse ne retourne jamais password_hash ;
UserRoleUpdate vérifie que le rôle est autorisé ;
UserStatusUpdate accepte uniquement un booléen.
Étape 5 — Créer le repository utilisateur

Créer les fonctions suivantes :

create_user()
get_user_by_email()
get_user_by_id()
list_users()
update_user_role()
update_user_status()

Le repository doit centraliser les accès à SQLite.

Il ne doit pas contenir les règles HTTP. Les erreurs HTTP restent gérées dans les routes ou services.

Étape 6 — Créer les routes /users

Routes attendues :

GET /users
GET /users/{user_id}
POST /users
PATCH /users/{user_id}/role
PATCH /users/{user_id}/status

Toutes ces routes doivent être réservées au rôle :

security_admin

Cas de validation :

Cas	Code attendu
Aucun jeton	401
Jeton employee	403
Jeton manager	403
Jeton it_admin	403
Jeton security_admin	200 ou 201
Utilisateur inexistant	404
Email déjà utilisé	409
Rôle invalide	422
Données invalides	422

Capture associée :

05_v5_security_users_admin.png
Étape 7 — Vérifier les règles RBAC

La matrice cible est la suivante :

Fonction	Employee	Manager	IT Admin	Security Admin
Créer une demande	Oui	Non	Non	Non
Décider une demande	Non	Oui	Non	Non
Attribuer un accès	Non	Non	Oui	Non
Révoquer un accès	Non	Non	Oui	Non
Lire les audits	Non	Non	Non	Oui
Administrer les utilisateurs	Non	Non	Non	Oui
Étape 8 — Exécuter les tests

Commande principale :

pytest -v

Commande Docker :

docker compose exec accessguard-api pytest -v

Points à vérifier :

tests d’authentification ;
tests utilisateur actif et inactif ;
tests des permissions RBAC ;
création d’un utilisateur ;
conflit d’email ;
modification du rôle ;
activation et désactivation ;
absence du hash dans les réponses ;
non-régression sur les anciennes routes.

Résultat de référence observé après intégration :

78 passed, 10 skipped, 1 warning

Les tests ignorés concernaient les routes CRUD utilisateurs avant leur implémentation complète. Ils doivent être réexécutés et activés lorsque les routes sont disponibles.

4. Fichiers principaux concernés
app/auth.py
app/database.py
app/schemas.py
app/seed.py
app/user_repository.py
app/main.py
tests/fixtures.py
tests/test_users.py
README.md
docs/V5_OLIVIER_PLAN.md
docs/V5_USERS_ARCHITECTURE.md
docs/V5_USERS_DEMO.md

Le nom exact des fichiers de routes peut varier selon l’architecture du dépôt.

5. Critères de validation finale

La partie d’Olivier est terminée lorsque :

la table users existe ;
les comptes de test sont créés ;
/auth/login utilise SQLite ;
un utilisateur inactif ne peut pas se connecter ;
les routes /users fonctionnent ;
seul security_admin peut utiliser ces routes ;
les mots de passe sont hashés ;
aucun hash n’est retourné dans les réponses ;
les tests passent ;
les captures sont enregistrées ;
les quatre fichiers de documentation sont complétés.
6. Limites restantes

Les éléments suivants ne font pas partie du périmètre immédiat de la V5 :

changement de mot de passe par l’utilisateur ;
mot de passe oublié ;
authentification multifacteur ;
refresh token ;
révocation centralisée des JWT ;
suppression définitive d’un utilisateur ;
gestion avancée des permissions individuelles ;
interface graphique complète d’administration ;
migrations Alembic ;
intégration avec un annuaire LDAP ou Active Directory.