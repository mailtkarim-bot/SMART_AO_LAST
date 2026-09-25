# T11 — Export local des reçus de consultation

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Permettre au Patron de demander un export borné des reçus de consultation afin
de conserver une trace opérable des filtres utilisés, sans exporter les
preuves, les revues ou les données économiques.

## Contrat

- export tenant-scoped et lié à l’Affaire ;
- contenu limité aux reçus, filtres normalisés, ordre, pagination et dates ;
- demande append-only avec état `REQUESTED`, `READY`, `UNKNOWN` ou `REFUSED` ;
- aucune réception externe présumée ;
- rejeu idempotent par clé de commande ;
- refus neutre pour un autre tenant ;
- aucun accès public ni lien permanent non autorisé.

## Preuves attendues

Migration/commande, tests PostgreSQL d’idempotence et tenant, projection Patron
de l’état, test C07 et gates complètes.

