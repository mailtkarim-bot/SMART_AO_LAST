# SMART AO — N05 : disponibilité terrain — audit et preuve v0.1

**État :** preuve verticale minimale implémentée côté web
**Date :** 20 septembre 2026

## Contrat retenu

Le parcours terrain distingue ce qui est déjà chargé dans le wizard d'une
capture locale. Une capture peut être `LOCAL`, `PENDING` ou `CONFIRMED` ; elle
ne devient confirmée qu'après retour positif de l'enregistrement serveur.

Le navigateur n'annonce pas un dossier complet hors connexion. Une capture
locale reste une intention de travail et affiche le risque de perte avant
synchronisation. Aucune capture locale n'est écrite dans `localStorage` ou
`sessionStorage`, afin de ne pas transformer un stockage non chiffré en dépôt
de données métier.

## Preuve

Dans `CollaboratorWizardPanel`, l'utilisateur peut conserver le résultat
visible localement, puis demander sa synchronisation via le chemin métier déjà
existant `recordCollaboratorTaskResult`. Une erreur laisse l'état `PENDING` ;
une réponse réussie seule produit `CONFIRMED`. Hors ligne, l'action de
synchronisation est refusée et l'avertissement de perte reste visible.

Preuve exécutée : 7 tests ciblés du panneau terrain, 21 tests API web, le
typecheck, le lint et le build web passent.

## Limites gelées

La preuve ne précharge pas de dossier, ne stocke pas de pièce brute en cache,
ne partage pas une capture et n'autorise aucune porte sensible hors réseau.
Une file locale durable, chiffrée et réconciliée nécessitera une décision
séparée sur le modèle de menace et la politique de révocation.
