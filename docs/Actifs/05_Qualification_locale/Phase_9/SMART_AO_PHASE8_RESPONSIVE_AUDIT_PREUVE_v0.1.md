# SMART AO — Phase 8 : variantes responsive — audit et preuve v0.1

**État :** audit responsive minimal clôturé
**Date :** 20 septembre 2026

Le produit conserve une seule application web et adapte les mêmes surfaces
selon la largeur disponible. Les règles existantes couvrent les paliers
desktop/tablette/mobile sans créer de navigation ou de pouvoir parallèle :

- la coque passe d'une barre latérale à une navigation horizontale sous 780px ;
- les grilles d'affaire, décision, dépôt, bibliothèque et wizard passent en
  une colonne aux paliers prévus ;
- le wizard replie sa barre d'identifiants et ses étapes, puis les listes de
  workflow ;
- les formulaires passent en une colonne à 480–650px ;
- les actions de capture terrain restent dans le flux existant et héritent des
  boutons responsives, sans cache local ni porte sensible hors réseau.

La preuve est statique et comportementale : 168 tests web, typecheck, lint et
build passent. Une recette visuelle sur appareils réels reste une activité de
la phase 9, avec clavier, lecteur d'écran, contraste et focus.
