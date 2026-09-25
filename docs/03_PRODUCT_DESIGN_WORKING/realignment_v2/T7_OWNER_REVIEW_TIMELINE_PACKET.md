# T7 — Revue propriétaire de la chronologie contractuelle C07

**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet

Faire vérifier par le Patron que la chronologie C07 permet de distinguer la
preuve initiale, le rectificatif, les actes de revue et l’état courant sans
perdre l’historique.

## Ce qui est démontré

- les événements sont ordonnés par révision puis date ;
- `SUPERSEDED`, `REJECTED` et `NEEDS_CLARIFICATION` restent visibles ;
- la projection est tenant-scoped et en lecture seule ;
- aucune action UX ne modifie une preuve ou une revue ;
- les gates backend/frontend sont vertes après réalignement `0094`.

## Décision demandée

Confirmer que cette chronologie est lisible et suffisante pour la revue
propriétaire locale, avant d’ajouter une éventuelle profondeur de filtrage ou
de recherche. Cette décision n’autorise aucune ouverture publique ni avis
juridique automatique.

