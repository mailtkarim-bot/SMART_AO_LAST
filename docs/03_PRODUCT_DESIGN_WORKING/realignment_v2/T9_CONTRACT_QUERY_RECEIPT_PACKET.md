# T9 — Reçu de consultation contractuelle

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Conserver un reçu minimal d’une consultation Patron afin de savoir quelles
filtres et quelle projection ont été consultés, sans transformer la lecture en
décision métier.

## Contrat

- reçu tenant-scoped et append-only ;
- Affaire, filtres normalisés, ordre, limite/offset et timestamp conservés ;
- aucun contenu économique ou personnel ajouté au reçu ;
- le reçu ne modifie ni preuve, ni revue, ni état courant ;
- rejeu identique idempotent par clé de commande ;
- une requête d’un autre tenant reste indistinguable d’une absence.

## Preuves attendues

Migration PostgreSQL, commande idempotente, refus tenant, projection Patron
lecture seule, test C07 et gates backend/frontend.

