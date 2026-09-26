# T30 — Consultation filtrée de la chronologie de reprise

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de filtrer la chronologie de reprise humaine par état et
date, sans fusionner les événements ni modifier les actes.

## Contrat

- filtres `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED`, `BLOCKED` ;
- bornes temporelles et pagination côté serveur ;
- tenant/export vérifiés avant filtrage ;
- ordre stable par date ;
- lecture seule et absence de réception externe présumée.

