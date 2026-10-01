# T22 — Lecture C07 de l’acte propriétaire

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Afficher l’acte propriétaire de validation de la vérification d’export sans le
confondre avec le hash technique ou l’état externe.

## Contrat

- owner, approbation, justification et date affichés séparément ;
- export et résultats techniques restent référencés mais inchangés ;
- tenant/Affaire/export filtrés côté serveur ;
- lecture seule, aucun bouton de modification ou d’envoi ;
- absence d’acte explicitement visible.

## Preuves attendues

Projection API fermée, tests tenant/pagination, composant C07, puis gates
backend/frontend complètes.

