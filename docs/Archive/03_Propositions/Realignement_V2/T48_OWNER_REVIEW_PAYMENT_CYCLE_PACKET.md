# T48 — Revue propriétaire du cycle paiement/post-réception

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier que le cycle paiement/post-réception représente des clauses et
hypothèses prudentes sans promettre un encaissement.

## Décision attendue

- sources et événements déclencheurs sont visibles ;
- `SOURCE_SIGNAL_ONLY`, `REVIEW_REQUIRED`, `UNKNOWN` restent distincts ;
- hypothèses de cash et coûts post-réception restent explicitement prudents ;
- données financières `FINANCIAL_PRIVATE` restent tenant-scoped ;
- aucun calcul juridique, paiement externe ou cash certain ;
- NO-GO public maintenu.

## Preuves disponibles

Gates ciblées T47 : **40/40 tests verts** ; migration `20260927_0103` validée.

