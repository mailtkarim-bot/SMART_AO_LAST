# T14 — Vue d’audit consolidée de l’export local

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Présenter dans C07 une vue unique reliant la demande d’export, ses transitions,
son état courant et sa preuve locale éventuelle, sans fusionner les événements.

## Contrat

- demande et transitions restent des événements distincts ;
- état courant calculé depuis la dernière transition confirmée ;
- `UNKNOWN` et `REFUSED` restent explicites ;
- `READY` n’est affiché que si la preuve locale existe ;
- filtrage tenant/Affaire avant toute projection ;
- aucune réception externe ou réussite implicite ;
- aucune mutation depuis cette vue.

## Preuves attendues

Projection API fermée, tests d’ordre/état/tenant, test C07, puis gates
backend/frontend complètes.

