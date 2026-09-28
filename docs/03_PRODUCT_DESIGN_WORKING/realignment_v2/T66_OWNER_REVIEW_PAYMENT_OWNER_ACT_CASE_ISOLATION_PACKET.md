# T66 — Revue propriétaire de l’isolation inter-Affaires

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier que les identifiants de rejeu d’un acte Patron restent liés à une
seule Affaire et ne peuvent pas être réutilisés silencieusement lors d’un
changement de contexte C07.

## Comportement couvert

- une intention C07 conserve ses identifiants pendant ses retries ;
- un changement de `case_id` génère une nouvelle intention ;
- `command_id`, `idempotency_key` et `owner_act_id` ne traversent pas les
  Affaires ;
- l’acte serveur reste tenant-scoped et append-only ;
- aucun état de l’Affaire précédente n’est affiché dans la nouvelle Affaire.

## Preuves locales

- backend paiement/API/DB/domain/architecture/ops : **46/46 tests verts** ;
- frontend : **200/200 tests verts** ;
- typecheck, lint et build verts ;
- test UI de changement d’Affaire ajouté ;
- aucun push GitHub.

## Décision attendue du Patron

- l’isolation inter-Affaires est approuvée ;
- les retries restent idempotents dans leur seule Affaire ;
- aucune donnée, preuve ou intention d’une autre Affaire n’est observée ;
- aucune action automatique de paiement, clôture ou conclusion juridique ;
- le NO-GO public est maintenu.

## Limites explicites

- l’isolation UI complète les contraintes tenant et serveur ;
- elle ne remplace pas les contrôles d’autorisation backend ;
- aucun paiement reçu ou cash disponible n’est déduit.
