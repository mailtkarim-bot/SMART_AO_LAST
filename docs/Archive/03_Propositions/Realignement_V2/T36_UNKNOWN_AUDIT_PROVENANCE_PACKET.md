# T36 — Provenance détaillée des inconnus consolidés

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Associer chaque inconnu ou blocage consolidé à son événement source, son
export, son acteur et sa date, sans recalcul silencieux.

## Contrat

- provenance obligatoire pour chaque état difficile ;
- source `TRANSITION`, `HUMAN_RESUMPTION` ou `VERIFICATION` explicite ;
- état et justification conservés tels quels ;
- tenant/export vérifiés avant projection ;
- lecture seule, aucune action automatique.

