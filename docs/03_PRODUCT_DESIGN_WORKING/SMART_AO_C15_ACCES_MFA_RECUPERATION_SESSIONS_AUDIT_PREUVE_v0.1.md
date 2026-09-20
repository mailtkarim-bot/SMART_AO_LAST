# SMART AO — C15 : accès, MFA, récupération et sessions sensibles

**Statut :** audit exécuté ; première correction de sécurité implémentée et testée  
**Autorités :** cahier OWNER v0.4, OWN-03/04, R03 ; catalogue UX OWNER v0.3, AUTH-03 à AUTH-07 et G19/G20.

## Contrat retenu

1. Une session `PASSWORD` permet seulement de terminer l'enrôlement ou la récupération contrôlée ; elle n'ouvre aucun accès métier.
2. Une opération sensible demande une MFA récente, évaluée côté serveur au moment de l'action. L'heure de connexion initiale ne suffit pas.
3. Un code de récupération ne valide jamais un step-up. Il lance uniquement la récupération dédiée après une session `PASSWORD` fraîche.
4. La récupération révoque toutes les sessions et lignées de rafraîchissement, désactive l'ancien facteur et impose un nouvel enrôlement MFA.
5. La désactivation volontaire d'un facteur exige une session active avec MFA récente et un code TOTP courant ; un code de récupération ne peut pas désactiver le facteur.
6. Les événements d'audit conservent le résultat et le motif sans secret TOTP, URI d'enrôlement ou code de secours.

## Audit du code vivant

Les briques existantes couvrent déjà :

- la garde HTTP commune `STEP_UP_REQUIRED` avant les routes métier ;
- le calcul serveur de `mfa_verified_at` et le contrôle de fraîcheur de quinze minutes pour les actions sensibles ;
- l'enrôlement TOTP avec secret chiffré, codes de secours hachés et consommation à usage unique ;
- le refus explicite d'un code de secours dans `verify_step_up` ;
- la récupération par mot de passe frais + code de secours avec révocation des sessions, refresh tokens et ancien facteur ;
- l'audit des réussites et refus MFA sans exposition de facteur.

L'écart corrigé concernait `/mfa/totp/disable` : le service acceptait auparavant un code de récupération depuis une session seulement authentifiée. Cette action pouvait donc désactiver le facteur sans preuve MFA récente. Le contrat est désormais borné par `session_id`, MFA récente et TOTP courant.

## Preuve exécutée

- `TotpService.disable()` verrouille la session, refuse une session absente, inactive ou MFA trop ancienne, puis refuse explicitement les codes de récupération ;
- la route d'administration transmet la session résolue au service ;
- le test PostgreSQL couvre enrôlement, confirmation, step-up, rejeu, refus du code de récupération en step-up, refus du code de récupération pour désactivation, désactivation TOTP et récupération complète ;
- 19 tests ciblés MFA/authentification passent sur PostgreSQL dédié, avec Ruff et compilation Python.

## Limites et suite

Les écrans AUTH-03 à AUTH-07 et ADM-05 restent à assembler visuellement. Le SSO, les notifications aux contacts de sécurité et la purge des pièces de récupération restent hors de cette preuve. La suite doit parcourir les routes sensibles une par une et vérifier qu'elles utilisent toutes la même politique de step-up, sans nouvelle dépendance.

**Prochaine étape :** assembler la preuve verticale C15 sur les routes sensibles, la reprise après expiration et les refus de récupération.
