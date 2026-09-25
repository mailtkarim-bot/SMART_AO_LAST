# T13 — Transitions explicites de l’export local

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Tracer les changements d’état d’une demande d’export sans modifier sa demande
initiale et sans déduire qu’un système externe a reçu le contenu.

## Contrat

- chaque transition est append-only et liée à l’export ;
- états fermés : `REQUESTED`, `READY`, `UNKNOWN`, `REFUSED` ;
- une transition vers `READY` exige une preuve locale de génération ;
- `UNKNOWN` reste inconnu et ne devient pas un succès ;
- une transition étrangère au tenant est refusée ;
- les transitions invalides ou réordonnées sont refusées ;
- C07 expose l’historique et le dernier état séparément.

## Preuves attendues

Migration/commande de transition, tests PostgreSQL d’ordre/idempotence/tenant,
projection API/C07 et gates complètes.

