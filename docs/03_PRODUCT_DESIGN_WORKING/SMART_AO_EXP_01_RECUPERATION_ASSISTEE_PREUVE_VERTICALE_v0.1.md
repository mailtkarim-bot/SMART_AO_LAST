# SMART AO — EXP-01 — Récupération assistée
## Preuve verticale minimale v0.1

**Date :** 14 septembre 2026  
**Statut :** PREUVE POSTGRESQL ACQUISE  
**Autorités :** cahier Produit/Métier v0.4, R03 et recette G19 ; catalogue UX v0.3, AUTH-05 et C15.

## 1. Constat d'audit

Le socle possède déjà les éléments utiles :

- `TotpService` génère dix codes de secours, conserve uniquement leur SHA-256 et les consomme une fois ;
- `POST /api/v1/auth/mfa/totp/step-up` et `.../disable` exigent une session authentifiée ;
- les tests PostgreSQL existants couvrent l'enrôlement, le rejeu TOTP, la consommation unique d'un code de secours et la désactivation ; 13 tests ciblés passent le 14 septembre 2026.

L'écart a été corrigé : un code de secours présenté sur `.../step-up` renvoie `RECOVERY_REENROLLMENT_REQUIRED` sans être consommé. Il ne peut donc plus élever une session à `MFA_STEP_UP`.

## 2. Périmètre de la première preuve

Cette tranche couvre uniquement la récupération normale par facteur de secours préenregistré. La personne doit d'abord ouvrir une nouvelle session `PASSWORD` avec son adresse et son mot de passe, puis présenter un code de secours à usage unique.

Sont volontairement hors de cette preuve :

- validation par un Propriétaire habilité ;
- récupération du dernier Propriétaire, qui exige la preuve d'autorité organisationnelle, deux intervenants SMART AO et la procédure A02/OWN-01 ;
- émission effective d'une notification externe, car aucun canal de notification sécurité n'est encore qualifié. L'événement d'audit durable est requis maintenant ; il ne remplace pas cette notification future.

## 3. Contrat à coder

### Entrée

`POST /api/v1/auth/mfa/recovery/start`

- session courante active, de force `PASSWORD`, sans MFA ;
- protection CSRF et limitation de débit MFA existantes ;
- corps minimal : `{ "code": "XXXX-XXXX-XXXX" }` ;
- aucun email, nom, tenant, rôle ou contenu métier n'est renvoyé.

### Mutation atomique et audit

Pour l'identité de la session, le service doit sous verrou :

1. valider et consommer le code de secours ;
2. désactiver le facteur TOTP actif ;
3. révoquer toutes les sessions et leurs lignées de renouvellement, y compris la session ayant présenté le code ;
4. terminer la mutation atomique, puis écrire l'événement durable `AUTH_MFA_RECOVERY_COMPLETED` sans secret ;
5. retourner `204` et supprimer les cookies d'authentification.

La personne se reconnecte ensuite par mot de passe, reste en session `PASSWORD`, lance l'enrôlement TOTP existant et le confirme. Aucun accès métier n'est possible avant cette confirmation MFA.

### Interdictions

- aucun endpoint anonyme de récupération par email seul ;
- un code de secours ne doit plus réussir sur `POST /api/v1/auth/mfa/totp/step-up` ; ce route retourne `RECOVERY_REENROLLMENT_REQUIRED` sans consommer le code ;
- pas de conservation en clair du code, de secret TOTP ou d'identité dans une réponse publique ;
- pas de restauration de rôle, de droit ou de session par le support dans cette tranche.

## 4. Critères de preuve

1. mot de passe + code de secours valide consomme le code, désactive le facteur et révoque les sessions ;
2. une tentative avec le même code, un code inconnu ou un code malformé ne change aucun état ;
3. le code de secours ne permet aucun `MFA_STEP_UP` direct ;
4. après reconnexion, seule la confirmation d'un nouveau TOTP rend l'accès métier possible ;
5. l'événement d'audit est présent sans secret ;
6. le flux email seul n'existe pas et une connexion inconnue conserve la réponse neutre existante.

## 5. Preuve exécutée

La route `POST /api/v1/auth/mfa/recovery/start` est implémentée. Elle exige une session `PASSWORD` de moins de cinq minutes, protégée par CSRF et limitée par débit. Elle ne reçoit qu'un code : un corps contenant un email est refusé par le contrat HTTP.

La preuve PostgreSQL du 14 septembre 2026 couvre : refus du code sur le step-up sans consommation ; refus d'un email seul ; consommation unique ; révocation de toutes les sessions, familles et jetons de renouvellement ; désactivation du facteur ; suppression des cookies ; écriture de l'audit ; reconnexion puis enrôlement et confirmation d'un nouveau TOTP. `ruff`, `mypy` et 7 tests ciblés passent.

## 6. Décision de passage

La plus petite preuve verticale réutilise `TotpService`, les sessions, la garde MFA, l'audit et les routes d'authentification déjà présents. Elle n'ajoute ni fournisseur email, ni nouveau rôle, ni procédure support. La récupération du dernier Propriétaire reste une tranche distincte et explicitement accompagnée.
