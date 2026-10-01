# T35 — Revue propriétaire de l’audit des inconnus consolidés

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier que les inconnus et blocages de la consultation consolidée sont
visibles et ne sont jamais transformés en succès implicites.

## Décision attendue

- `UNKNOWN`, `UNAVAILABLE`, `MISMATCH` restent distincts ;
- `BLOCKED` et `FOLLOW_UP_REQUIRED` restent des blocages humains ;
- chaque état garde son événement source ;
- aucune action automatique n’est déclenchée ;
- lecture seule et tenant scope maintenus ;
- NO-GO public maintenu.

## Preuves disponibles

Gates ciblées T34 : **38/38 tests verts** ; backend et frontend précédents
validés ; synchronisation GitHub confirmée.

