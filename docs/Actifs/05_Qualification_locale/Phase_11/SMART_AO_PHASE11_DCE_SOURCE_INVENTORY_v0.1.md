# SMART AO — Inventaire source DCE et premier corpus non financier v0.1

**Date :** 21 septembre 2026  
**Source inspectée :** `/home/noor/PROJECTS/BTP/DOCUMENTATION/SMART_AO DOCUMENTATION/DCE Type`  
**Règle :** inventaire de noms, types, tailles et hashes ; aucun original copié, modifié ou indexé

## Inventaire

Le dossier contient **379 fichiers** : 83 candidats techniques selon leur nom, 35 fichiers explicitement financiers, 16 fichiers sensibles à revoir, 236 fichiers non classés automatiquement et 9 fichiers système `Thumbs.db` ignorés.

Cette classification est un filtre de préparation, pas une validation de droits ou d’anonymisation. Les fichiers non classés restent hors corpus.

## Premier paquet retenu

Le premier paquet est limité au dossier `CENTRALE GROUPE ELEC` et contient 10 PDF techniques : RC, CCAP, CCTC, six CCTP de lots et planning. Taille totale : environ 5,2 Mo. Les hashes servent à détecter une modification avant ingestion.

| Type | Fichier | SHA-256 abrégé |
|---|---|---|
| RC | `01- RC/26NOVO17- RC VF.pdf` | `42f26e45b871…350cd84` |
| CCAP | `02- CCAP/26NOVO17 - CCAP VF.pdf` | `757118b5e330…3a7b3a1` |
| CCTC | `04- CCTC + CCTP/CCTC Lot no00 Prescriptions communes.pdf` | `bad52eaaedb2…ffc4a820` |
| CCTP lot 1 | `04- CCTC + CCTP/CCTP Lot No1 ELEC.pdf` | `82e6d8bf4614…e6b8c0c` |
| CCTP lot 2 | `04- CCTC + CCTP/CCTP Lot No2 GE.pdf` | `5da2766563e1…49d63f75` |
| CCTP lot 3 | `04- CCTC + CCTP/CCTP Lot No3 GO - VRD.pdf` | `1b611ee23661…32d516e1` |
| CCTP lot 4 | `04- CCTC + CCTP/CCTP Lot No4 ETANCHEITE.pdf` | `4d873d89ee64…49de573` |
| CCTP lot 5 | `04- CCTC + CCTP/CCTP Lot No5 BARDAGE SERRURERIE.pdf` | `66ce91caeaef…554dd5ae9` |
| CCTP lot 6 | `04- CCTC + CCTP/CCTP Lot No6 PEINTURE.pdf` | `119c33854cf4…46eb23b8` |
| Planning | `09- PLANNING PREVISIONNEL/Planning .pdf` | `a7da3f402402…5a9d66d` |

## Exclusions immédiates

- BPU, DPGF, données financières, montants estimatifs et facturation ;
- actes d’engagement et pièces DC1/DC2 contenant des identités ou coordonnées ;
- rapports amiante, RICT, G2PRO et pièces graphiques tant que les droits et la confidentialité ne sont pas attestés ;
- archives et fichiers non classés automatiquement.

Avant toute indexation, ce paquet doit recevoir une revue de droits/anonymisation et une extraction de contrôle. Les fragments financiers restent exclus par classification, même si un document technique contient une mention de montant.

