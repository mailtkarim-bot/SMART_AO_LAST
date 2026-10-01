# T49 — Lecture C07 du cycle paiement/post-réception

**Statut :** prêt à implémenter localement — NO-GO public maintenu

## Objectif

Afficher au Patron les sources, états et hypothèses du cycle paiement/post-
réception sans exposer les données financières privées à un autre rôle.

## Contrat

- tenant/Affaire et classification financière filtrés côté serveur ;
- états `SOURCE_SIGNAL_ONLY`, `REVIEW_REQUIRED`, `UNKNOWN` visibles ;
- hypothèses cash et coûts post-réception affichés comme hypothèses ;
- lecture seule, aucun paiement ou calcul juridique ;
- absence de cycle explicitement visible.

