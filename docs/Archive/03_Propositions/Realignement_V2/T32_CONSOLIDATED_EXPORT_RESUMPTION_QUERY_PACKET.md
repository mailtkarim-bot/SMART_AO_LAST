# T32 — Consultation consolidée export/reprise

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre une consultation unique d’un export et de sa reprise humaine, tout
en conservant les événements et filtres séparés.

## Contrat

- filtres combinés état export/état reprise ;
- ordre serveur déterministe ;
- tenant/export avant projection ;
- pagination bornée ;
- aucune fusion d’événements ni mutation ;
- états `UNKNOWN`, `BLOCKED`, `FOLLOW_UP_REQUIRED` visibles.

