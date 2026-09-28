# T65 — Décision propriétaire des identifiants de rejeu

**Statut :** approuvé localement — NO-GO public maintenu

Le Patron approuve la stabilisation des identifiants de rejeu :

- après interruption, C07 réutilise le même `command_id`, `idempotency_key` et
  `owner_act_id` ;
- le retry ne crée pas une seconde intention métier ;
- aucun succès n’est affiché avant relecture serveur ;
- aucun paiement ni effet juridique n’est déduit ;
- le NO-GO public est maintenu.

Cette décision valide le comportement de rejeu de l’interface. Elle ne remplace
pas l’idempotence serveur et ne constitue pas une preuve de paiement reçu.
