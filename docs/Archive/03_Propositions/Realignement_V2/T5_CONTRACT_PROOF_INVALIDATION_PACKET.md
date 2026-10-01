# T5 — Invalidation contrôlée après rectificatif contractuel

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Représenter un rectificatif ou une nouvelle source qui invalide la projection
opérationnelle d’une preuve, sans supprimer ni modifier les preuves et revues
antérieures.

## Contrat attendu

- l’ancienne preuve reste append-only et consultable ;
- une nouvelle révision porte une source/observation distincte ;
- le lien de supersession est explicite ;
- l’ancienne projection devient `SUPERSEDED` ou `REVIEW_REQUIRED`, jamais
  silencieusement supprimée ;
- la nouvelle révision exige un nouvel acte de revue humaine ;
- un rectificatif étranger au tenant est indistinguable d’une absence ;
- C07 affiche l’ancienne preuve, la nouvelle source et l’état courant.

## Preuves attendues

Migration/contrainte additive, tests PostgreSQL d’invalidation et tenant,
projection Patron, test C07 et rejeu complet backend/frontend.

## Limites

Pas de déduction juridique, de recalcul automatique de pénalité/délai, de
scoring, de signature électronique, de pilote public ou d’index persistant.

