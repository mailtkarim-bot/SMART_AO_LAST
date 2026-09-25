# T10 — Lecture Patron des reçus de consultation

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de relire les reçus de consultation contractuelle afin de
comprendre quels filtres et quelle pagination ont été utilisés, sans réexposer
les données de preuve ni transformer le reçu en décision.

## Contrat

- lecture tenant-scoped et bornée ;
- ordre par date de création décroissante ;
- filtres et ordre conservés tels qu’enregistrés ;
- aucune mutation ou suppression depuis C07 ;
- refus neutre pour une autre Affaire ou un autre tenant ;
- absence de reçu explicitement visible.

## Preuves attendues

Projection API fermée, tests tenant/pagination, test C07, puis gates complètes.

