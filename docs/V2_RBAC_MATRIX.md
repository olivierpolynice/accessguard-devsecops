# AccessGuard — Matrice RBAC V2

## Objectif

Cette matrice définit les droits d’accès aux fonctionnalités principales de l’API AccessGuard.

Les contrôles doivent être appliqués à partir du JWT transmis dans l’en-tête HTTP :

```text
Authorization: Bearer <token>
```

Un utilisateur non authentifié doit recevoir une réponse `401 Unauthorized`.

Un utilisateur authentifié avec un rôle insuffisant doit recevoir une réponse `403 Forbidden`.

---

## Rôles

| Rôle | Description |
|---|---|
| `employee` | Utilisateur standard pouvant consulter les ressources et créer des demandes d’accès |
| `manager` | Responsable pouvant consulter certaines demandes et intervenir dans le workflow de validation |
| `it_admin` | Administrateur informatique pouvant attribuer et révoquer des accès |
| `security_admin` | Administrateur sécurité pouvant consulter les journaux d’audit et surveiller les événements sensibles |

---

## Matrice des permissions

| Endpoint / Action | Employee | Manager | IT Admin | Security Admin | Résultat attendu |
|---|---|---|---|---|---|
| `POST /auth/login` | Oui | Oui | Oui | Oui | JWT retourné si les identifiants sont valides |
| `GET /health` | Oui | Oui | Oui | Oui | API disponible et fonctionnelle |
| `GET /resources` | Oui | Oui | Oui | Oui | Liste des ressources disponibles |
| `POST /access-requests` | Oui | Oui | Oui | Oui | Création d’une demande d’accès |
| `GET /access-requests` | Ses demandes | Périmètre autorisé | Oui | Lecture si nécessaire | Données filtrées selon le rôle |
| `POST /access-requests/{request_id}/grant` | Non | Non | Oui | Non | Attribution d’un accès après contrôle du rôle |
| `GET /access-grants` | Ses accès si prévu | Lecture limitée si prévue | Oui | Lecture si nécessaire | Liste des accès accordés |
| `POST /access-grants/{grant_id}/revoke` | Non | Non | Oui | Oui si la règle est validée | Révocation d’un accès existant |
| `GET /audit-logs` | Non | Non ou accès limité | Oui | Oui | Consultation des événements d’audit |

---

## Règles de sécurité

### Authentification

Toutes les routes sensibles doivent exiger un JWT valide.

| Situation | Réponse HTTP attendue |
|---|---|
| JWT absent | `401 Unauthorized` |
| JWT invalide | `401 Unauthorized` |
| JWT expiré | `401 Unauthorized` |
| JWT valide avec rôle insuffisant | `403 Forbidden` |
| JWT valide avec rôle autorisé | `200`, `201` ou réponse métier attendue |

### Contrôle des rôles

Les contrôles d’accès doivent être appliqués côté serveur.

Le rôle de l’utilisateur doit être extrait du JWT et ne doit jamais être accepté comme une donnée fiable envoyée directement dans le body de la requête.

Exemple attendu :

```text
Authorization: Bearer <token>
```

Le token doit permettre d’identifier :

- l’adresse e-mail de l’utilisateur ;
- son rôle ;
- son identité interne si elle existe ;
- son expiration.

---

## Interdictions

- Le client ne doit pas pouvoir choisir son propre rôle dans le body d’une requête.
- Le client ne doit pas pouvoir envoyer l’identité d’un autre utilisateur afin d’usurper ses droits.
- Les mots de passe ne doivent jamais être retournés dans les réponses API.
- Les mots de passe doivent être stockés sous forme hachée.
- Les tokens JWT complets ne doivent jamais être enregistrés dans les logs d’audit.
- Les routes d’attribution, de révocation et de consultation des audits doivent être protégées par RBAC.
- Aucun secret réel ne doit être envoyé sur GitHub.

---

## Actions critiques à protéger en priorité

### Attribution d’accès

```text
POST /access-requests/{request_id}/grant
```

Rôle autorisé :

```text
it_admin
```

Résultats attendus :

- sans JWT : `401 Unauthorized` ;
- JWT avec rôle `employee` : `403 Forbidden` ;
- JWT avec rôle `manager` : `403 Forbidden` ;
- JWT avec rôle `it_admin` : succès.

### Révocation d’accès

```text
POST /access-grants/{grant_id}/revoke
```

Rôles autorisés :

```text
it_admin
security_admin
```

Résultats attendus :

- sans JWT : `401 Unauthorized` ;
- JWT avec rôle insuffisant : `403 Forbidden` ;
- JWT avec rôle autorisé : succès.

### Consultation des audits

```text
GET /audit-logs
```

Rôles autorisés :

```text
it_admin
security_admin
```

Résultats attendus :

- sans JWT : `401 Unauthorized` ;
- JWT avec rôle `employee` : `403 Forbidden` ;
- JWT avec rôle `manager` : `403 Forbidden` ou accès limité selon la règle retenue ;
- JWT avec rôle `it_admin` ou `security_admin` : succès.

---

## Tests à prévoir

- [ ] Appel d’une route sensible sans JWT : réponse `401`.
- [ ] Appel avec un JWT invalide : réponse `401`.
- [ ] Appel avec un JWT expiré : réponse `401`.
- [ ] Appel avec un rôle non autorisé : réponse `403`.
- [ ] Appel avec un rôle autorisé : succès.
- [ ] Tentative d’attribution d’accès par un `employee` : refusée.
- [ ] Tentative d’attribution d’accès par un `manager` : refusée.
- [ ] Attribution d’accès par un `it_admin` : autorisée.
- [ ] Révocation d’accès par un rôle non autorisé : refusée.
- [ ] Révocation d’accès par un `it_admin` : autorisée.
- [ ] Consultation des audits par un `employee` : refusée.
- [ ] Consultation des audits par un `it_admin` : autorisée.
- [ ] Consultation des audits par un `security_admin` : autorisée.

---

## Validation V2

La matrice RBAC V2 est validée lorsque :

- chaque route sensible possède une règle de rôle claire ;
- les réponses `401` et `403` sont correctement appliquées ;
- les tests couvrent les cas autorisés et refusés ;
- les routes sensibles ne font pas confiance aux rôles fournis directement par le client ;
- les règles sont documentées et cohérentes avec le code.
