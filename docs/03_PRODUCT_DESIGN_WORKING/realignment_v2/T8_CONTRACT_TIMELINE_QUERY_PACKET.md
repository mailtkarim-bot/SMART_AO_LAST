# T8 — Consultation filtrée de la chronologie contractuelle

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de consulter une chronologie contractuelle volumineuse
avec des filtres déterministes, sans changer les preuves ni masquer les états.

## Filtres autorisés

- révision de preuve ;
- état (`SOURCE_SIGNAL_ONLY`, `HUMAN_REVIEW_REQUIRED`, `CONFIRMED`, `UNKNOWN`,
  `SUPERSEDED`) ;
- type d’acte (`REVIEW`) ;
- référence source exacte ;
- pagination bornée et ordre serveur stable.

## Invariants

- filtrage tenant-scoped avant pagination ;
- aucun résultat d’un autre tenant observable, y compris par compteur ;
- les états `REJECTED`, `NEEDS_CLARIFICATION` et `SUPERSEDED` restent
  recherchables ;
- aucune mutation, fusion ou conclusion juridique ;
- une requête inconnue ou invalide est refusée explicitement.

## Preuves attendues

Contrat API fermé, tests de filtres/tenant/pagination PostgreSQL, test C07,
typecheck, lint et suite complète locale.

