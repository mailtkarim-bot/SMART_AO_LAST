# T31 — Revue propriétaire de la consultation filtrée de reprise

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier que les filtres de chronologie de reprise permettent une
consultation opérationnelle sans masquer les états difficiles.

## Décision attendue

- les états `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED` et `BLOCKED` sont filtrables ;
- la pagination conserve l’ordre serveur ;
- le filtrage tenant/export est appliqué avant projection ;
- aucune mutation ou transition implicite n’est disponible ;
- les événements techniques et humains restent séparés ;
- NO-GO public maintenu.

## Preuves disponibles

Backend **1 801 tests verts**, frontend **191/191**, typecheck, lint et build
verts ; tests T30 API/PostgreSQL **2/2 verts**.

