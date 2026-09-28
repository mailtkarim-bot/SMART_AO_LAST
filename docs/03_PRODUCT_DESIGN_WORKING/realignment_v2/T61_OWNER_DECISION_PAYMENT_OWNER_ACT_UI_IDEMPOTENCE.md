# T61 — Décision propriétaire de la garde d’idempotence UI

**Statut :** approuvé localement — NO-GO public maintenu

Le Patron approuve la garde d’idempotence UI de l’acte Patron :

- le bouton n’est disponible qu’après réception d’un audit serveur valide ;
- le double clic est bloqué pendant l’écriture ;
- C07 ne présume pas le succès avant le retour API ;
- l’idempotence serveur reste obligatoire ;
- aucun paiement ni effet juridique n’est déduit ;
- le NO-GO public est maintenu.

Cette décision valide le comportement d’interface. Elle ne remplace pas les
contrôles serveur et ne constitue pas une preuve de paiement reçu.
