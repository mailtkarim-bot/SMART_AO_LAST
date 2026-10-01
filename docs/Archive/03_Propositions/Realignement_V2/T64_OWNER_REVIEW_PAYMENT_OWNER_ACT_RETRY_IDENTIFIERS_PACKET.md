# T64 — Revue propriétaire des identifiants de rejeu de l’acte Patron

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier qu’un retry après interruption de l’écriture Patron reprend la même
intention métier au lieu de créer un second acte.

## Comportement couvert

- `command_id`, `idempotency_key` et `owner_act_id` sont générés une seule fois
  pour l’intention C07 ;
- une interruption laisse l’état non confirmé ;
- le retry réutilise exactement les trois identifiants ;
- l’idempotence serveur reste le contrôle final ;
- aucun succès local n’est affiché avant la relecture serveur.

## Preuves locales

- backend paiement/API/DB/domain/architecture/ops : **46/46 tests verts** ;
- frontend : **199/199 tests verts** ;
- typecheck, lint et build verts ;
- test UI de stabilité des trois identifiants ajouté ;
- aucun push GitHub.

## Décision attendue du Patron

- la stabilisation des identifiants de rejeu est approuvée ;
- le retry ne crée pas une nouvelle intention métier ;
- les états techniques et inconnus restent inchangés ;
- aucune action automatique de paiement, clôture ou conclusion juridique ;
- le NO-GO public est maintenu.

## Limites explicites

- la stabilité UI ne remplace pas la contrainte serveur ;
- une confirmation définitive exige la relecture tenant-scoped ;
- aucun paiement reçu ou cash disponible n’est déduit.
