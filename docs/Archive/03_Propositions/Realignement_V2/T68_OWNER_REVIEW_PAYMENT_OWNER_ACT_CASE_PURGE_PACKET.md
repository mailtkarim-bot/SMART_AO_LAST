# T68 — Revue propriétaire de la purge inter-Affaires C07

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier qu’un changement d’Affaire purge immédiatement la projection de l’acte
Patron précédent avant la lecture de la nouvelle Affaire.

## Comportement couvert

- l’ancien acte Patron est retiré de l’état C07 dès changement de `case_id` ;
- la nouvelle lecture est tenant-scoped et liée à la nouvelle Affaire ;
- aucune justification, approbation ou erreur de l’Affaire précédente n’est
  affichée transitoirement ;
- les identifiants de rejeu restent isolés par Affaire ;
- les contrôles backend restent la source d’autorité.

## Preuves locales

- backend paiement/API/DB/domain/architecture/ops : **46/46 tests verts** ;
- frontend : **200/200 tests verts** ;
- typecheck, lint et build verts ;
- aucun push GitHub.

## Décision attendue du Patron

- la purge inter-Affaires est approuvée ;
- aucune donnée ou preuve de l’Affaire précédente ne doit rester visible ;
- aucun paiement ni effet juridique n’est déduit ;
- le NO-GO public est maintenu.

## Limites explicites

- la purge UI complète les contrôles d’autorisation et de tenant côté serveur ;
- elle ne confirme ni paiement reçu ni cash disponible.
