# T34 — Audit consolidé et visibilité des inconnus

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Rendre visibles dans la consultation consolidée les inconnus et états bloquants
sans les convertir en succès implicites.

## Contrat

- `UNKNOWN`, `MISMATCH`, `BLOCKED` et `FOLLOW_UP_REQUIRED` restent distincts ;
- chaque état conserve son événement source ;
- aucun état courant n’est recalculé par déduction silencieuse ;
- tenant/export avant projection ;
- lecture seule et absence de réception externe présumée.

