# Revue propriétaire locale — baseline → dérogation → impact

**Date :** 24 septembre 2026  
**Statut :** prêt pour revue locale — NO-GO public maintenu

## Objet de la revue

Valider que SmartAO représente une clause contractuelle comme une chaîne
traçable, sans transformer un signal documentaire en avis juridique :

`source → baseline → dérogation éventuelle → impact opérationnel → revue humaine`

## Ce qui est démontré

- La source est obligatoire et conservée avec l'observation d'origine.
- La baseline, la dérogation et l'impact sont des éléments séparés.
- Une dérogation ne remplace pas la baseline.
- Une confirmation est refusée si dérogation ou impact manque.
- Les états `SOURCE_SIGNAL_ONLY`, `HUMAN_REVIEW_REQUIRED`, `CONFIRMED` et
  `UNKNOWN` restent fermés et explicites.
- La persistance est tenant-scoped, append-only et versionnée.
- Le rejeu de commande est idempotent.
- Un autre tenant reçoit un refus neutre.
- C07 expose la preuve en lecture seule, avec sources et état inchangés.

## Preuves exécutées

- Domaine : 5 tests de validation de chaîne.
- API Patron : projection fermée et tenant-scoped.
- PostgreSQL : migration `20260924_0092`, upgrade → downgrade → upgrade.
- Gates après UX : backend ciblé 34/34 ; frontend 188/188 ; typecheck et lint
  verts.

## Limites à conserver

- Aucun moteur juridique, assurantiel ou HSE.
- Aucun calcul automatique de délai, pénalité, couverture ou droit.
- Aucun index RAG persistant requis par cette preuve.
- Validation externe et Golden DCE réel toujours hors périmètre local.
- NO-GO public inchangé.

## Décision propriétaire demandée

Confirmer localement que la chaîne est la bonne représentation produit pour la
prochaine tranche de persistance et d'UX, avec maintien des limites ci-dessus.
Cette revue n'autorise ni ouverture publique ni conclusion juridique
automatique.

