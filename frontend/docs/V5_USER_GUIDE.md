# Guide utilisateur AccessGuard V5

> Interface de gouvernance des accès internes — AsteriaTech IAM  
> Prototype statique V5 — HTML/CSS/JS vanilla

---

## Lancer l'interface

Ouvrir le fichier `frontend/index.html` directement dans un navigateur.  
Aucun serveur requis.

---

## Connexion

1. Entrer votre adresse e-mail
2. Entrer le mot de passe `demo1234`
3. Sélectionner votre rôle dans la liste déroulante
4. Cliquer sur **Se connecter**

La sidebar s'adapte automatiquement selon le rôle choisi.

### Comptes de démonstration

| Compte | Rôle | Mot de passe |
|---|---|---|
| alice.employee@asteriatech.local | Employee | demo1234 |
| marc.manager@asteriatech.local | Manager | demo1234 |
| ines.itadmin@asteriatech.local | IT Admin | demo1234 |
| sam.security@asteriatech.local | Security Admin | demo1234 |

---

## Guide par rôle

### Employee

**Pages accessibles :** Dashboard, Ressources, Mes demandes, Accès attribués, Audit logs

| Action | Comment faire |
|---|---|
| Consulter les ressources disponibles | Menu → Ressources |
| Créer une demande d'accès | Menu → Mes demandes → remplir le formulaire → Envoyer la demande |
| Suivre ses demandes | Menu → Mes demandes → tableau en bas |
| Filtrer ses demandes par statut | Cliquer sur un bouton de filtre (En attente, Approuvées, Refusées, Actives) |
| Consulter ses accès actifs | Menu → Accès attribués |

---

### Manager

**Pages accessibles :** Dashboard, Demandes à valider, Accès attribués, Audit logs

| Action | Comment faire |
|---|---|
| Voir les demandes en attente | Menu → Demandes à valider |
| Approuver une demande | Cliquer **Approuver** sur la ligne → le statut passe à APPROUVÉ |
| Refuser une demande | Cliquer **Refuser** → confirmer dans la fenêtre → le statut passe à REFUSÉ |
| Filtrer les demandes | Cliquer sur un bouton de filtre (En attente, Approuvées, Refusées) |

---

### IT Admin

**Pages accessibles :** Dashboard, Mes demandes, Accès attribués, Audit logs

| Action | Comment faire |
|---|---|
| Voir les accès approuvés | Menu → Accès attribués |
| Révoquer un accès actif | Cliquer **Révoquer** → confirmer dans la fenêtre de confirmation → le statut passe à RÉVOQUÉ |
| Filtrer les accès | Cliquer sur un bouton de filtre (Actifs, Révoqués, Approuvés) |

---

### Security Admin

**Pages accessibles :** Dashboard, Utilisateurs, Audit logs, Monitoring

| Action | Comment faire |
|---|---|
| Consulter tous les événements d'audit | Menu → Audit logs |
| Filtrer les événements | Cliquer sur un bouton de filtre (En attente, Approuvés, Révoqués, Actifs) |
| Gérer les utilisateurs | Menu → Utilisateurs |
| Changer le rôle d'un utilisateur | Colonne Actions → liste déroulante → sélectionner le nouveau rôle |
| Désactiver un compte | Colonne Actions → cliquer **Désactiver** → confirmer dans la fenêtre |
| Réactiver un compte | Colonne Actions → cliquer **Activer** (disponible si le compte est INACTIF) |
| Consulter le monitoring | Menu → Monitoring |

---

## Codes d'erreur affichés dans l'interface

| Code | Message affiché | Cause |
|---|---|---|
| 401 | Session expirée. Redirection vers la connexion… | Token absent ou expiré |
| 403 | Vous n'avez pas les droits nécessaires pour cette action. | Rôle insuffisant |
| 404 | Ressource introuvable. | Identifiant inexistant |
| 409 | Conflit : cette action est impossible dans l'état actuel. | Ex. : double grant actif |
| 422 | Données invalides. Vérifiez le formulaire. | Ex. : date de fin < date de début |
| 500 | Erreur serveur. Réessayez dans quelques instants. | Erreur backend |

---

## Comportements UX

- **Spinner de chargement** : affiché pendant les actions simulées
- **Boutons désactivés** : pendant une action en cours, le bouton est grisé
- **Toast de succès** : notification verte en bas à droite pendant 3 secondes
- **Dialog de confirmation** : affiché avant toute action destructrice (révocation, désactivation)
- **Redirection automatique** : si la session est expirée (erreur 401), redirection vers Login en 2 secondes

---

## Structure des fichiers

```
frontend/
├── index.html       — Interface principale (toutes les pages)
├── styles.css       — Styles et composants visuels
├── app.js           — Logique JS : navigation, filtres, interactions
├── README.md        — Documentation technique
└── docs/
    └── V5_USER_GUIDE.md — Ce guide
```