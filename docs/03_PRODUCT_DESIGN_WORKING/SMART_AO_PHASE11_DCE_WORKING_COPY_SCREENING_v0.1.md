# SMART AO — Screening de la copie de travail DCE v0.1

**Date :** 21 septembre 2026  
**Statut :** `REVIEW_REQUIRED` — aucun index RAG permanent  
**Copie temporaire :** `/tmp/smartao-dce-corpus-work`

## Travail effectué

Le paquet de 10 PDF sélectionné dans `CENTRALE GROUPE ELEC` a été copié hors Git, extrait localement et hashé. La copie contient 30 320 lignes extraites. Un premier filtre a retiré 567 lignes comportant des marqueurs financiers, identitaires ou secrets ; 19 178 lignes techniques restent dans les fichiers `sanitized/`.

## Deuxième passe d’anonymisation

Une copie `redacted/` a été produite par remplacement déterministe des établissements, sites, adresses, contacts et identifiants de consultation. Les motifs évidents email, téléphone, code postal et adresse ne sont plus présents dans cette copie. La copie reste soumise à revue humaine : une regex ne prouve pas l’absence de toute identité implicite.

Un test BGE one-shot a encodé 10 fragments redacted en vecteurs de dimension 1 024 en 18 390,81 ms, sans indexation ni écriture PostgreSQL.

## Pourquoi le paquet reste en revue

La suppression par motifs ne suffit pas à anonymiser ce DCE : les textes conservés contiennent encore des noms d’établissement, sites, codes postaux et marqueurs d’adresse. Le paquet est donc exploitable pour une revue humaine et une préparation de manifeste, mais il n’est pas encore autorisé pour l’indexation BGE/RAG.

## Décision

- originaux inchangés et hors Git ;
- copie de travail temporaire hors Git ;
- aucun index, aucune écriture PostgreSQL et aucun appel externe ;
- revue manuelle des identités, adresses, sites, dates sensibles et mentions financières restantes avant toute activation RAG.

**Manifestes temporaires :** `/tmp/smartao-dce-corpus-work/manifest.json`, `sanitized-manifest.json` et `redacted-manifest.json`.
