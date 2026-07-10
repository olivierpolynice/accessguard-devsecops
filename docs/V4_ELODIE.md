# V4 — Contribution UI/UX d'Élodie

## 1. Objectif

L'objectif de cette contribution est d'améliorer la lisibilité, l'ergonomie et la cohérence visuelle du frontend AccessGuard sans modifier le backend.

## 2. Branche de travail

`feature/v4-elodie`

## 3. Fichiers modifiés

- `frontend/index.html`
- `frontend/styles.css`
- `frontend/README.md`
- `docs/V4_GUIDE_UTILISATEUR.md`
- `docs/V4_ELODIE.md`

## 4. Améliorations réalisées

- ajout de la section Login manquante ;
- amélioration de la palette de couleurs et des variables CSS ;
- harmonisation de la typographie (hiérarchie h1/h2/h3/h4) ;
- amélioration des espacements et des marges ;
- amélioration des boutons (`min-height: 44px` pour l'accessibilité) ;
- amélioration des formulaires (focus visible, hauteur minimale) ;
- amélioration des tableaux (hover, en-têtes, débordement horizontal) ;
- unification des badges de statuts (`.pill` et `.status`) ;
- amélioration du responsive design (breakpoints 1050px et 768px) ;
- amélioration de la lisibilité générale.

## 5. Pages concernées

- Login ;
- Dashboard ;
- Demandes d'accès ;
- Accès attribués ;
- Audit logs ;
- Monitoring.

## 6. Éléments clairs après amélioration

- navigation principale visible et structurée ;
- indicateurs du dashboard regroupés et lisibles ;
- statuts identifiables par couleur et libellé ;
- actions principales accessibles depuis chaque section ;
- formulaire de demande d'accès complet.

## 7. Suggestions UI/UX restantes

- ajouter des icônes cohérentes dans la sidebar ;
- ajouter des messages de confirmation après chaque action ;
- améliorer les messages d'erreur (champs obligatoires, dates invalides) ;
- ajouter des filtres sur les tableaux d'audit et de demandes ;
- renforcer l'accessibilité (attributs ARIA, contrastes) ;
- ajouter un menu mobile avec hamburger ;
- améliorer les états de chargement (skeleton screens).

## 8. Captures de l'interface

### Page de connexion
![Page de connexion](screenshots/v4-elodie/Capture-V4-Frontend-Login.png)

### Tableau de bord
![Tableau de bord](screenshots/v4-elodie/Capture-V4-Frontend-Dashboard.png)

### Demandes d'accès
![Demandes d'accès](screenshots/v4-elodie/Capture-V4-Frontend-Demandes.png)

### Logs d'audit
![Logs d'audit](screenshots/v4-elodie/Capture-V4-Frontend-Audit.png)

### Monitoring
![Monitoring](screenshots/v4-elodie/Capture-V4-Frontend-Monitoring.png)

## 9. Vérifications

- [x] affichage testé sur ordinateur ;
- [x] affichage testé en format mobile ;
- [x] liens vérifiés ;
- [x] textes vérifiés ;
- [x] aucun fichier backend modifié ;
- [x] aucun fichier sensible ajouté.

## 10. Conclusion

La V4 améliore la présentation et l'expérience utilisateur du prototype AccessGuard tout en conservant le fonctionnement existant du backend. Les améliorations portent sur la lisibilité, l'ergonomie, la cohérence visuelle et l'accessibilité mobile.