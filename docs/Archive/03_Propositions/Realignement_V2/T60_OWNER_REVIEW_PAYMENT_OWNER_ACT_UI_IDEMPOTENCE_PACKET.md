# T60 — Revue propriétaire de la garde d’idempotence UI de l’acte Patron

**Statut :** prêt pour revue locale Patron — NO-GO public maintenu

## Objet

Vérifier que C07 empêche un double clic ou une soumission concurrente lors de
l’écriture de l’acte Patron, sans masquer l’état serveur ni modifier l’audit
technique.

## Comportement couvert

- le bouton de validation Patron est disponible seulement après réception d’un
  audit serveur valide ;
- le premier clic démarre l’écriture append-only ;
- le bouton est désactivé pendant la requête ;
- un second clic ne déclenche pas un second acte ;
- après retour, C07 relit l’acte persisté ;
- les états `UNKNOWN`, `REVIEW_REQUIRED` et `SOURCE_SIGNAL_ONLY` restent
  inchangés.

## Preuves locales

- backend paiement/API/DB/domain/architecture/ops : **46/46 tests verts** ;
- frontend : **197/197 tests verts** ;
- typecheck, lint et build verts ;
- test UI de double clic ajouté ;
- aucun push GitHub.

## Décision attendue du Patron

- la garde de double clic est approuvée ;
- l’écriture reste append-only et idempotente côté serveur ;
- C07 ne présume aucun succès avant le retour de l’API ;
- aucune action automatique de paiement, clôture ou conclusion juridique ;
- le NO-GO public est maintenu.

## Limites explicites

- la garde UI ne remplace pas l’idempotence serveur ;
- elle ne confirme ni paiement reçu ni cash disponible ;
- les interruptions réseau restent traitées comme résultat non confirmé.
