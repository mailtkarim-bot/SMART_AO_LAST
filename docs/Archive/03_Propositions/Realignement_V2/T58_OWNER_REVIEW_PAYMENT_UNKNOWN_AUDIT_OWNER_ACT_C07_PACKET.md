# T58 — Revue propriétaire de l’écriture et lecture C07 de l’acte Patron

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier que le Patron peut enregistrer puis consulter son acte de validation
de l’audit des inconnus paiement depuis C07, sans modifier les preuves
techniques, les cycles paiement ou leurs états.

## Parcours couvert

1. C07 affiche l’audit des inconnus en lecture seule ;
2. le Patron déclenche l’écriture de l’acte append-only ;
3. l’API persiste l’acte tenant-scoped avec idempotence ;
4. C07 relit l’acte persistant et affiche sa décision et sa justification ;
5. les états techniques restent inchangés.

## Contrôles

- écriture réservée au Patron avec MFA/session autorisée ;
- refus d’Affaire étrangère et rejeu du même identifiant ;
- lecture filtrée par tenant et réservée au Patron ;
- acte distinct de l’audit technique et des cycles paiement ;
- aucune action automatique de paiement, de clôture ou de calcul juridique.

## Preuves locales

- backend API/DB/domain/architecture/ops : **46/46 tests verts** ;
- frontend : **195/195 tests verts** ;
- typecheck, lint et build verts ;
- migration `20260928_0105` validée ;
- aucun push GitHub.

## Décision attendue du Patron

- l’écriture et la lecture C07 de l’acte sont approuvées ;
- l’acte reste append-only, tenant-scoped et Patron-only ;
- la justification reste visible sans effet juridique ou financier implicite ;
- les inconnus `UNKNOWN`, `REVIEW_REQUIRED` et `SOURCE_SIGNAL_ONLY` restent
  inchangés ;
- le NO-GO public est maintenu.

## Limites explicites

- l’acte confirme une revue humaine, pas un paiement reçu ;
- aucun montant de cash ou coût n’est calculé ;
- aucune fermeture automatique d’un inconnu n’est permise.
