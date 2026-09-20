# SMART AO — UX Freeze global v0.1

**Statut :** UX FREEZE GLOBAL — périmètre consolidé, Product Freeze non déclaré  
**Date :** 20 septembre 2026  
**Autorité :** cahier OWNER produit/métier v0.4, catalogue UX OWNER v0.3 et validations OWNER EXPERIENCE existantes

## Objet

Ce document rassemble les règles d’expérience désormais communes aux surfaces validées. Il fixe l’expérience observable et ses limites ; il ne remplace pas le cahier technique d’exécution et ne constitue pas le Product Freeze v1.0.

## Périmètre consolidé

- les 17 espaces canoniques C00–C16 applicables et les 104 surfaces rattachées ;
- les OWNER EXPERIENCE FREEZE EXP-01 à EXP-07, C14–C16 et N01–N05 déjà produits ;
- le gel G01–G09 validé par le propriétaire ;
- les parcours PUX-01 à PUX-19, avec leurs preuves complètes ou leur statut `PARTIAL` conservé ;
- les variantes desktop, tablette et mobile utiles sans application parallèle.

## Règles UX globales

| Règle | Comportement obligatoire |
|---|---|
| Source avant conclusion | Toute décision expose source, version, état et inconnue applicable. |
| Inconnu honnête | `UNKNOWN`, `REVIEW_REQUIRED`, `PARTIAL` et `DEPENDENCY_UNPROVEN` restent visibles et actionnables. |
| Actes séparés | Signature, P5, export, dépôt humain, réception, résultat, P6, P7 et REX restent des actes distincts. |
| Autorité serveur | Tenant, rôle, affectation, périmètre, MFA et délégation sont résolus côté serveur. |
| Confidentialité | Marge, coûts, trésorerie, prix, société et pouvoir Patron restent hors des contrats Collaborateur. |
| Aucune déduction | Un score, une absence de donnée, une capacité ou un extrait ne devient jamais une acceptation automatique. |
| Append-only | Les corrections, résolutions, suspensions, reprises et preuves ajoutent un fait ; ils n’effacent pas l’historique. |
| Résultat inconnu | Une réponse réseau ambiguë conserve le dernier état confirmé et propose une vérification. |
| Accessibilité | HTML natif, clavier, focus visible, erreurs annoncées, contrastes contrôlés et reflow responsive. |
| Mobile compagnon | Le mobile capture et consulte les états utiles ; il ne devient pas une voie P5 hors ligne ou un dépôt autonome. |

## États et langage à préserver

Les libellés « À vérifier », « À résoudre », « Inconnu », « Revue requise », « Résultat non confirmé » et « Dépôt externe non effectué » sont contractuels. Ils ne doivent pas être remplacés par « prêt », « envoyé », « validé » ou « conforme » sans preuve correspondante.

## Limites qui restent ouvertes

- les PUX marqués `PARTIAL` doivent être fermés avant un gel produit complet ;
- la recette manuelle avec lecteur d’écran réel et zoom navigateur reste à exécuter ;
- le Product Freeze v1.0, le cahier technique d’exécution et la validation de production restent à produire ;
- aucun connecteur externe, dépôt autonome ou rapprochement de réception n’est ajouté par ce document.

## Effet du gel

Toute nouvelle expérience doit respecter ce vocabulaire, ces rôles, ces états et ces séparations d’actes. Une modification qui change une de ces règles exige une nouvelle version du gel, un motif, l’impact sur les preuves et un arbitrage propriétaire.

## Références

- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_G01_G09_OWNER_EXPERIENCE_FREEZE_v0.1.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G09_OWNER_REVIEW_PACKET_v0.1.md`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`
