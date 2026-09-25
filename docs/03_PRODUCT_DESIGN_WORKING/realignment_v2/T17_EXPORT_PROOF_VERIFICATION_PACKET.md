# T17 — Vérification locale de la preuve d’export

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Vérifier localement qu’un hash enregistré correspond au contenu exporté, sans
affirmer une réception ou une acceptation externe.

## Contrat

- recalcul local déterministe du SHA-256 ;
- résultat fermé : `MATCH`, `MISMATCH`, `UNAVAILABLE` ;
- un `MISMATCH` ne modifie jamais l’historique ;
- `READY` n’est affiché que si la preuve locale et le hash correspondent ;
- tenant/Affaire/export vérifiés côté serveur ;
- résultat de vérification append-only et horodaté.

## Preuves attendues

Contrat de vérification, test hash match/mismatch, persistence PostgreSQL,
projection C07 et gates backend/frontend.

