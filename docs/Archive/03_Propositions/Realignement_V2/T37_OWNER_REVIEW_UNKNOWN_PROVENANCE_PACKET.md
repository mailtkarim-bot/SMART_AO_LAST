# T37 — Revue propriétaire de la provenance des inconnus

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier que chaque inconnu ou blocage consolidé reste relié à son
événement source, son acteur, sa date et sa justification.

## Décision attendue

- les sources `TRANSITION`, `HUMAN_RESUMPTION`, `VERIFICATION` sont distinctes ;
- les états et justifications ne sont pas recalculés ;
- la provenance est tenant-scoped et read-only ;
- aucune action automatique ou conclusion juridique n’est déclenchée ;
- NO-GO public maintenu.

## Preuves disponibles

Gates ciblées T36 : **39/39 tests verts** ; provenance persistée sur migration
`20260926_0102`.

