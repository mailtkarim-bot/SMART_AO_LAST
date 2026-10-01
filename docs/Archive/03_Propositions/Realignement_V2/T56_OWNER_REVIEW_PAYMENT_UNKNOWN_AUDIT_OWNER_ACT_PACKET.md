# T56 — Revue propriétaire de l’acte Patron de l’audit des inconnus paiement

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier que la validation Patron de l’audit des inconnus paiement est
persistée comme un acte humain séparé, append-only et tenant-scoped, sans
modifier les cycles techniques ni fermer automatiquement un inconnu.

## Surface implémentée

- migration PostgreSQL `20260928_0105` ;
- commande et handler `RecordPaymentUnknownAuditOwnerActCommand` ;
- écriture Patron tenant-scoped avec refus d’Affaire étrangère ;
- rejeu du même `owner_act_id` refusé ;
- lecture Patron C07 tenant-scoped ;
- affichage en lecture seule de l’acte dans le panneau paiement.

## Preuves locales

- idempotence et handler : **1/1 test vert** ;
- schéma PostgreSQL : **1/1 test vert** ;
- lecture API Patron : **1/1 test vert** ;
- gates ciblées paiement/API/DB/domain : **12/12 tests verts** ;
- architecture/ops/schema : **34/34 tests verts** ;
- frontend : **194/194 tests verts**, typecheck/lint/build verts ;
- tête Alembic : `20260928_0105` ;
- aucun push GitHub.

## Décision attendue du Patron

- l’acte Patron reste distinct de l’audit technique et des cycles paiement ;
- `approved` et la justification sont conservés sans réécriture de l’historique ;
- l’acte reste tenant-scoped et réservé au Patron ;
- aucune action automatique de paiement, de clôture ou de calcul juridique ;
- C07 reste en lecture seule pour cet acte ;
- le NO-GO public est maintenu.

## Limites explicites

- l’acte valide la revue humaine de l’audit, pas la réception d’un paiement ;
- aucun montant de cash ou coût n’est calculé ;
- aucune fermeture automatique des états `UNKNOWN`, `REVIEW_REQUIRED` ou
  `SOURCE_SIGNAL_ONLY` n’est autorisée.
