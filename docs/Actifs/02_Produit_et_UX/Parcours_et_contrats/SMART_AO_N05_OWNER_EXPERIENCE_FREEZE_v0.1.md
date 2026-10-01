# SMART AO — N05 Owner Experience Freeze v0.1

**État :** disponibilité terrain minimale gelée
**Date :** 20 septembre 2026

| Situation | Affichage et action |
|---|---|
| pièce déjà chargée dans le wizard | disponible dans le périmètre affiché |
| note ou preuve saisie sans synchronisation | `LOCAL`, risque de perte explicitement visible |
| synchronisation lancée | `PENDING`, aucun succès présumé |
| enregistrement serveur confirmé | `CONFIRMED` |
| réseau absent ou requête refusée | capture conservée comme locale/en attente, sans validation métier |

Le parcours ne promet pas de dossier complet hors connexion, n'écrit pas de
secret dans le stockage navigateur et ne transforme pas une capture en partage
à l'équipe. La révocation ou les portes sensibles restent évaluées côté
serveur.

**Preuve :** 7 tests du panneau, 21 tests API web, typecheck, lint et build.

**Prochaine tranche de phase :** matérialiser les variantes responsive utiles
sans créer une application parallèle.
