# T27 — Lecture C07 de la reprise humaine

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Afficher dans C07 l’acte de reprise humaine locale afin que le Patron voie son
état, sa justification et son auteur, sans modifier les actes techniques.

## Contrat

- lecture tenant-scoped liée à l’export ;
- états `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED`, `BLOCKED` visibles ;
- justification et acteur affichés séparément ;
- absence d’acte explicitement visible ;
- aucun bouton de transition ou de modification ;
- aucune réception externe présumée.

## Preuves attendues

Projection API fermée, tests tenant/états, composant C07, puis gates complètes.

