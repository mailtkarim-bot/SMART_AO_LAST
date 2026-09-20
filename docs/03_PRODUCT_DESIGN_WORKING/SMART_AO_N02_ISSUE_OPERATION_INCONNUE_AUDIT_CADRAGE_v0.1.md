# SMART AO — N02 : issue d'opération inconnue

**Statut :** audit et preuve verticale réalisés
**Objet retenu :** export ZIP d'un paquet de remise autorisé
**Date :** 20 septembre 2026

## Audit du code vivant

Le backend distingue déjà l'autorisation P5, l'export déterministe et la
preuve de dépôt externe. Une erreur HTTP explicite est connue ; une rupture de
réseau après l'envoi peut toutefois laisser l'effet serveur inconnu côté
navigateur. Le paquet et sa version restent les identifiants de vérification.

Le front possédait déjà ce contrat pour la création d'Affaire et l'import prix,
mais l'export affichait seulement une erreur générique. N02 est donc traité sur
la plus petite surface risquée : l'export Patron d'un paquet autorisé.

## Contrat minimal

Après une réponse réseau absente ou ambiguë :

- l'interface conserve l'identifiant du paquet et l'autorisation P5 ;
- elle affiche `Résultat de l’export non confirmé` et le dernier état confirmé
  (« paquet autorisé ») ;
- elle remplace l'action par `Vérifier l’export` ;
- elle ne marque pas l'export comme réussi et ne prétend pas connaître le
  résultat externe ;
- une erreur HTTP connue reste une erreur explicite et ne devient pas N02.

La vérification réutilise l'intention et l'identifiant existants. Aucun dépôt
tiers n'est supposé et `external_submission: NOT_PERFORMED` reste affiché.

## Preuve exécutée

`useSubmissionActions` conserve désormais `submissionExportState` (`IDLE`,
`EXPORTED`, `UNKNOWN`). Le scénario de rupture réseau est couvert par un test
Vitest : l'état devient `UNKNOWN`, `submissionExported` reste faux et le
message demande une vérification. Les tests SubmissionPanel couvrent aussi le
contrat de présentation.

Vérifications : 166 tests front, typecheck et ESLint passent. Les tests backend
consolidés C15/C16/N01 restent à `58 passed`.

## Limite assumée

Le backend conserve l'audit de chaque export réellement servi. Une lecture
Patron dédiée de l'historique d'export pourra être ajoutée si la vérification
doit distinguer un ZIP servi d'une réponse interrompue ; cette extension n'est
pas nécessaire pour garder un état honnête et éviter un succès présumé.
