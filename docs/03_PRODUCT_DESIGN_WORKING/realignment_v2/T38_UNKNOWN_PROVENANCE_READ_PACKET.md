# T38 — Lecture C07 de la provenance des inconnus

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Afficher dans C07 la provenance complète d’un inconnu ou blocage consolidé,
sans modifier l’événement source.

## Contrat

- source, événement, acteur, date, état et justification affichés séparément ;
- tenant/export filtrés côté serveur ;
- absence de provenance explicitement visible ;
- lecture seule et aucun déclenchement automatique ;
- `UNKNOWN`, `MISMATCH`, `BLOCKED` et `FOLLOW_UP_REQUIRED` conservés.

