# T19 — Affichage C07 de la vérification d’export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Rendre visible le résultat de vérification locale sans confondre intégrité du
fichier local et réception externe.

## Contrat UX

- afficher `MATCH`, `MISMATCH` ou `UNAVAILABLE` distinctement ;
- afficher le hash calculé uniquement dans le contexte Patron autorisé ;
- `MISMATCH` ne devient jamais `READY` ;
- `UNAVAILABLE` reste inconnu et demande une action humaine hors système ;
- aucun bouton de validation juridique, d’envoi ou de relance automatique ;
- lecture seule et tenant-scoped.

## Preuves attendues

Types/API, hook et composant C07, tests frontend d’états difficiles, puis gates
backend/frontend complètes.

