# SMART AO — Index des références actives

**Date : 21 septembre 2026**
**Statut : INDEX DE PRÉCÉDENCE DOCUMENTAIRE**

Cet index indique quel document fait foi pour chaque type de décision. Il ne crée aucune règle produit supplémentaire.

## 1 — Autorité produit et métier

[`SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`](SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md)

Répond à : **« Quel SMART AO voulons-nous construire, pour qui, avec quelles règles, autorités et limites ? »**

En cas de contradiction produit ou métier, le Product Freeze v1.0 prévaut. Le cahier v0.4 est archivé dans `../_ARCHIVE/produit_metier/`.

## 2 — Autorité de couverture UX et des parcours

[`SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`](SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md)

Répond à : **« Quelles expériences, surfaces, états et parcours doivent exister pour matérialiser le produit ? »**

Il garantit la couverture des 104 identifiants, de C00, C01–C16, N01–N05 et PUX-01–PUX-19.

## 3 — Autorité des fondations UX

[`SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md`](SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md)

Répond à : **« Quelles règles visuelles et interactionnelles communes chaque expérience doit-elle respecter ? »**

Il définit le shell, le langage métier, les états, la preuve, la confidentialité, l’IA contextuelle, le responsive et la méthode de conception par expériences.

## 4 — Expériences, preuves et qualification

[`../03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`](../03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md)

Répond à : **« Quelle preuve reste active, quel parcours est en cours et quelle est la prochaine sortie ? »**

Les anciens documents `WORK_PROPOSAL` sont historiques et se trouvent dans `_ARCHIVE/`. Les preuves et `OWNER EXPERIENCE FREEZE` encore utiles restent dans `03_PRODUCT_DESIGN_WORKING/`.

Le référentiel des dépendances de travail est [`DEPENDENCIES_WORKING/SMART_AO_V8_DEPENDANCES_ARCHITECTURE_WORK_PROPOSAL.md`](DEPENDENCIES_WORKING/SMART_AO_V8_DEPENDANCES_ARCHITECTURE_WORK_PROPOSAL.md). Il décrit l’existant et les options candidates ; il ne constitue pas un Architecture Freeze.

## 5 — Références d’implémentation existante

[`../01_IMPLEMENTATION_ACTIVE/`](../01_IMPLEMENTATION_ACTIVE/)

Répond à : **« Quel est l’état technique réel, quelles migrations sont engagées et quelles preuves existent ? »**

Ces références ne redéfinissent pas le produit. Le code et les tests restent les premières preuves de l’état effectivement implémenté.

## Règle de changement

- une amélioration locale conforme aux trois autorités peut progresser dans le document d’expériences ;
- une modification des fondations UX exige une nouvelle version de la référence UX ;
- une modification du catalogue ou du cahier métier exige une proposition explicite de réouverture propriétaire ;
- une maquette, une spécification technique ou du code ne peut jamais créer silencieusement un droit, une promesse ou une capacité.
