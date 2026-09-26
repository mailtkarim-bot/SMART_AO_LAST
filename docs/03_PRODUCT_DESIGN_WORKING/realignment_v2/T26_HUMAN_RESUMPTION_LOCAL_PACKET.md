# T26 — Reprise humaine locale après relève

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de consigner une reprise humaine locale après consultation
de la relève, sans modifier rétroactivement les actes techniques.

## Contrat

- acte humain distinct, append-only et tenant-scoped ;
- justification obligatoire ;
- états fermés `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED`, `BLOCKED` ;
- aucune transition automatique de l’export ;
- aucune réception externe présumée ;
- C07 reste lisible et les événements antérieurs restent inchangés.

