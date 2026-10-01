# T25 — Revue propriétaire de la relève opérationnelle

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Vérifier que la vue de relève permet au Patron de comprendre l’état courant
d’un export local et les actes qui le composent.

## Décision attendue

- la demande, les transitions, les vérifications et l’acte propriétaire restent
  distingués ;
- `UNKNOWN` et les incohérences restent visibles ;
- aucune mutation n’est disponible depuis la relève ;
- aucune réception externe n’est présumée ;
- la vue est suffisante pour une reprise humaine locale.

## Preuves disponibles

Backend **1 790 tests verts**, frontend **191/191**, typecheck, lint et build
verts ; NO-GO public maintenu.

