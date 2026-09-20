# SMART AO — C16 Owner Experience Freeze v0.1

**Statut :** preuve verticale backend gelée pour revue propriétaire  
**Autorités :** cahier OWNER v0.4 §38 ; catalogue UX OWNER v0.3, SHR-01/N03, ADM-06 et ADM-10.

## Comportement prouvé

Un partage est lié à un objet et une empreinte de version exacte. Il porte un destinataire normalisé, une finalité, une classification, une date de début et une expiration obligatoire. Le jeton retourné à la création est opaque et seul son hash est conservé.

La lecture exige le destinataire et le jeton exacts. Une expiration ou une révocation rend la lecture indisponible ; l’expiration est conservée comme état et événement séparé. Le rejeu de création avec la même idempotence retourne le même partage sans réexposer le jeton.

La révocation exige un acteur Patron ou Délégué actif, la capacité de partage sensible et une MFA récente. La preuve ne prétend pas supprimer une copie déjà téléchargée et ne transforme jamais une réponse réseau inconnue en réception confirmée.

## Preuve exécutée

- migration `20260920_0089` : projection `tenant_resource_shares` et événements append-only `tenant_resource_share_events` ;
- `ResourceSharingService` : création, lecture bornée, expiration, révocation et idempotence ;
- 3 tests PostgreSQL C16 ciblés passent, dont tête Alembic ; la suite consolidée C14/C15/C16 compte 56 tests passants ;
- Ruff, compilation Python et `git diff --check` passent.

## Limites gelées

Les routes HTTP publiques, notifications, prévisualisation N03 et mesure des copies après téléchargement restent hors de cette preuve. Le prochain incrément doit exposer ce contrat derrière une route authentifiée et vérifier les réponses neutres sans divulguer l’existence d’un partage.

**Prochaine étape :** ouvrir N01 sur les conflits de contributions et leurs résolutions append-only.
