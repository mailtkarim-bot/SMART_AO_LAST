# SMART AO — Phase 9 : couverture structurelle des 104 surfaces v0.1

**État :** inventaire catalogue rattaché aux espaces canoniques ; preuve UX comportementale encore à exécuter  
**Date :** 20 septembre 2026

Le registre `web/src/app/canonicalSpaces.ts` rattache désormais chaque surface
non-PUX du catalogue produit à exactement un espace canonique C00–C16. La
constante `CATALOG_SURFACE_IDS` conserve l'inventaire contractuel des 104 IDs et
le test `web/src/app/canonicalSpaces.test.ts` vérifie l'égalité exacte entre le
catalogue et les rattachements : aucun ID manquant, dupliqué ou inventé.

| Espace | Statut | Surfaces rattachées |
|---|---|---:|
| C00 Transversal | PARTIAL | 9 |
| C01 Accueil | MATERIALIZED | 9 |
| C02 Radar | MATERIALIZED | 2 |
| C03 Opportunité | PARTIAL | 2 |
| C04 Portefeuille | MATERIALIZED | 1 |
| C05 Synthèse Affaire | PARTIAL | 12 |
| C06 Documents et preuves | MATERIALIZED | 7 |
| C07 Décision | MATERIALIZED | 2 |
| C08 Prix | MATERIALIZED | 5 |
| C09 Partenaires | BACKLOG | 2 |
| C10 Réponse | MATERIALIZED | 7 |
| C11 Remise | MATERIALIZED | 7 |
| C12 Résultat et passation | BACKLOG | 4 |
| C13 Entreprise | MATERIALIZED | 13 |
| C14 Administration | PARTIAL | 11 |
| C15 Accès | PARTIAL | 7 |
| C16 Paquet tiers | PARTIAL | 4 |
| **Total** |  | **104** |

`MATERIALIZED` décrit une destination web identifiable, `PARTIAL` signale une
surface ou un parcours incomplet, et `BACKLOG` interdit de présenter l'espace
comme disponible. Le registre ne transforme donc pas une preuve backend en
écran fictif et ne prétend pas encore que les 104 surfaces ont chacune passé
la recette PUX/G01–G52.

## Preuve exécutée

- test ciblé du registre : 2 tests passent ;
- le test vérifie les 17 codes C00–C16, les destinations de navigation valides,
  les statuts explicites et l'égalité exacte des 104 IDs ;
- typecheck, lint et build web restent les contrôles de compilation et de
  non-régression ;
- la vérification comportementale individuelle est la tranche suivante,
  surface par surface, puis PUX-01 à PUX-19.

