# SMART AO — C15 Owner Experience Freeze v0.1

**Statut :** preuve verticale C15 gelée pour revue propriétaire  
**Autorités :** cahier OWNER v0.4, OWN-03/04 et R03 ; catalogue UX OWNER v0.3, AUTH-03 à AUTH-07 et G19/G20.

## Parcours couvert

Le parcours distingue quatre niveaux : session `PASSWORD` limitée, MFA initiale, step-up MFA récent pour les opérations sensibles et récupération exceptionnelle. Une session expirée, révoquée, inactive ou suspendue ne peut pas reconstituer l’acteur par le navigateur.

Les opérations sensibles passent par la même politique serveur : décision finale, autorisation P5, signature et preuve de réception exigent `mfa_required=True` et une vérification âgée de quinze minutes au plus. Une date MFA future est refusée comme incohérente.

La récupération exige une session `PASSWORD` fraîche et un code de secours. Elle révoque toutes les sessions et lignées de rafraîchissement, désactive l’ancien facteur et impose un nouvel enrôlement. Le code de secours est refusé dans le step-up et ne peut pas désactiver directement le facteur.

La désactivation volontaire d’un facteur exige désormais une session active avec MFA récente et un TOTP courant. La session est ramenée à `PASSWORD`, de sorte que l’accès métier reste bloqué jusqu’au nouvel enrôlement.

## États difficiles et refus

| Situation | Résultat |
|---|---|
| Session sans MFA sur une route métier | `403 STEP_UP_REQUIRED` |
| Step-up absent, expiré ou horodaté dans le futur | `STEP_UP_REQUIRED` |
| Code de secours envoyé au step-up | `RECOVERY_REENROLLMENT_REQUIRED` |
| Récupération sans mot de passe récent | `PASSWORD_REAUTH_REQUIRED` |
| Désactivation avec session PASSWORD ou code de secours | refus `MFA_REAUTH_REQUIRED` ou `TOTP_CODE_INVALID` |
| Session ou refresh révoqué après récupération | refus d’authentification, sans restauration implicite |

## Preuve exécutée

- 19 tests PostgreSQL/authentification passent pour enrôlement, confirmation, step-up, récupération, révocation et désactivation ;
- 12 tests de politique passent pour les actions sensibles, la fraîcheur MFA et les horodatages incohérents ;
- Ruff, compilation Python et `git diff --check` passent ;
- les limites d’interface AUTH-03 à AUTH-07 restent documentées, sans secret de facteur dans les projections ou l’audit.

## Limites gelées

Le SSO, les notifications aux contacts de sécurité, la purge des pièces de récupération et les écrans visuels ADM-05 restent à construire. Aucune dépendance externe n’est ajoutée pour cette preuve.

**Prochaine étape :** ouvrir C16 sur les partages, destinataires, durée, révocation et limites après téléchargement.
