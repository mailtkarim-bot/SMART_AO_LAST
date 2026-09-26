# T33 — Revue propriétaire de la consultation consolidée export/reprise

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Vérifier que la consultation consolidée T32 reste compréhensible pour le
Patron lorsque les filtres export et reprise sont utilisés ensemble.

## Décision attendue

- les événements `TRANSITION` et `HUMAN_RESUMPTION` restent séparés ;
- les filtres combinés ne masquent pas les états difficiles ;
- la pagination conserve l’ordre serveur ;
- tenant/export sont appliqués avant projection ;
- aucune mutation ou conclusion automatique n’est disponible ;
- NO-GO public maintenu.

## Preuves disponibles

Backend **1 803 tests verts**, frontend **191/191**, typecheck, lint et build
verts ; tests T32 API/PostgreSQL **2/2 verts**.

