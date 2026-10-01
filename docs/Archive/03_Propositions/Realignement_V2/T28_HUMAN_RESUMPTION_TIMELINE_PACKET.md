# T28 — Chronologie de reprise humaine et export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de voir l’acte de reprise humaine dans le contexte complet
de l’export, de ses transitions et de ses vérifications.

## Contrat

- événements techniques et acte humain séparés ;
- ordre déterministe par date ;
- états `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED`, `BLOCKED` visibles ;
- aucune transition technique déduite de l’acte humain ;
- tenant/export filtrés côté serveur ;
- lecture seule et absence de réception externe présumée.

## Preuves attendues

Projection API/C07, tests d’ordre/tenant/états, puis gates backend/frontend.

