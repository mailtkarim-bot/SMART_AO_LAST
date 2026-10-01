# T29 — Revue propriétaire de la chronologie de reprise humaine

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier que la chronologie T28 permet de distinguer les transitions
techniques d’export et l’acte de reprise humaine.

## Décision attendue

- `TRANSITION` et `HUMAN_RESUMPTION` restent des événements différents ;
- l’acte humain n’est pas une transition technique ;
- `ACKNOWLEDGED`, `FOLLOW_UP_REQUIRED` et `BLOCKED` restent visibles ;
- aucune réception externe n’est présumée ;
- la vue reste en lecture seule et tenant-scoped.

## Preuves disponibles

Backend **1 799 tests verts**, frontend **191/191**, typecheck, lint et build
verts ; NO-GO public maintenu.

