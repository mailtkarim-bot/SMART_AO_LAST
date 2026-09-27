# T42 — Synthèse de clôture locale des inconnus

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Présenter une synthèse finale des inconnus et blocages d’un export, sans les
fermer artificiellement et sans remplacer la revue humaine.

## Contrat

- compteurs par état et provenance ;
- entrées encore ouvertes détaillées ;
- `UNKNOWN`, `MISMATCH`, `BLOCKED`, `FOLLOW_UP_REQUIRED` conservés ;
- aucune transition automatique vers succès ou clôture ;
- tenant/export avant agrégation ;
- lecture Patron uniquement.

## Preuves attendues

Projection de synthèse, tests de comptage/tenant, C07 et gates complètes.

