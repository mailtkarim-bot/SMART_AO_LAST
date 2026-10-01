# T6 — Chronologie C07 des preuves et revues

**Statut :** tranche suivante locale — NO-GO public maintenu

## Objectif

Présenter dans C07 l’ordre des preuves, rectificatifs et actes de revue afin
que le Patron voie le dernier état tout en gardant l’historique vérifiable.

## Contrat

- ordre déterministe par révision puis date d’acte ;
- chaque événement conserve son type, sa source et son état ;
- `SUPERSEDED`, `REJECTED` et `NEEDS_CLARIFICATION` restent visibles ;
- aucune suppression, fusion silencieuse ou conclusion juridique ;
- tenant et Affaire restent les filtres serveur.

## Preuves attendues

Projection backend dédiée, test PostgreSQL d’ordre stable, test API fermé,
test C07 et suite frontend complète.

