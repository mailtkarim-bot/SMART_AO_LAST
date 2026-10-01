# T15 — Intégration C07 de l’audit export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Afficher dans C07 l’audit d’un export local sans mélanger la demande, les
transitions et l’état courant.

## Contrat UX

- section lecture seule, accessible au Patron ;
- demande affichée avec ses filtres ;
- transitions affichées dans l’ordre ;
- `UNKNOWN` et `REFUSED` visuellement distincts de `READY` ;
- preuve locale affichée uniquement lorsqu’elle existe ;
- aucune action de relance ou de validation juridique ;
- absence d’export explicitement visible.

## Preuves attendues

Types/API, hook et composant C07, test frontend d’états difficiles, gates
frontend puis suite complète locale.

