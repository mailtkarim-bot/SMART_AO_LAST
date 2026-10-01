# T23 — Chronologie de validation propriétaire et vérification

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Présenter dans C07 la chronologie complète d’un export : vérifications
techniques, transitions, puis acte propriétaire, sans les fusionner.

## Contrat

- ordre déterministe par date et type d’acte ;
- vérifications `MATCH/MISMATCH/UNAVAILABLE` séparées ;
- acte propriétaire séparé et identifiable ;
- aucune approbation humaine déduite d’un hash ;
- tenant/export filtrés avant projection ;
- lecture seule et absence de réception externe présumée.

## Preuves attendues

Projection API/C07, tests d’ordre et tenant, puis gates backend/frontend.

