# SMART AO — PACKAGE DE RÉALIGNEMENT V3
## Ordre de lecture et d’exécution pour Codex

**Date : 30 septembre 2026**

Ce paquet matérialise le changement de centre de gravité décidé après :

- réévaluation concurrentielle ;
- audit du repo vivant ;
- constat de banalisation des features IA classiques ;
- apparition de concurrents sur les dérogations, OS, paiement, réception et DGD ;
- constat d’un décalage entre certaines autorités documentaires et l’avancement réel du code.

---

# 1. FICHIERS

Lire dans cet ordre :

1. `SMART_AO_DIRECTIVE_CODEX_REALIGNEMENT_STRATEGIQUE_V3_2026-09-30.md`
2. `SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_CANDIDATE_v3.0_2026-09-30.md`
3. `SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.0_CANDIDATE_2026-09-30.md`
4. `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_MASTER_CANDIDATE_v3.0_2026-09-30.md`

Les versions plus courtes `SMART_AO_CAHIER_DIRECTEUR_PRODUIT_METIER_V3_CANDIDATE_2026-09-30.md` et `SMART_AO_CAHIER_TECHNIQUE_EXECUTION_V3_CANDIDATE_2026-09-30.md` servent de delta lisible ; les deux fichiers `MASTER` conservent la profondeur V2 absorbée.

Puis relire dans le repo :

4. index des références actives ;
5. Product Freeze actuellement actif ;
6. architecture v3.1 ;
7. catalogue UX + fondations UX ;
8. plan global de conception/réalisation ;
9. cahier technique actuel ;
10. code/tests/migrations.

---

# 2. IMPORTANT : V3 N’EST PAS ENCORE PROMU

Codex doit distinguer :

- **autorité active GitHub** ;
- **candidat V3** ;
- **état réel du code**.

Aucune modification du fichier d’index ne doit déclarer V3 autorité sans validation propriétaire explicite.

Préparer le patch, puis demander/attendre l’acte propriétaire dans le workflow normal.

---

# 3. PREMIÈRE MISSION

Ne pas coder une nouvelle feature.

Exécuter T0 :

1. baseline HEAD ;
2. audit autorité documentaire ;
3. Deep Core code map ;
4. KEEP/ADAPT/MOVE/REPLACE/ABSENT ;
5. data/auth/API/UX/test deltas ;
6. PR plan ;
7. rollback.

---

# 4. CHANGEMENT DE PRIORITÉ

Avant V3 :

> compléter progressivement l’ensemble des expériences/surfaces.

À partir de V3 :

> construire en priorité trois verticales Deep Core et utiliser le reste comme couverture/parité.

Priorités :

A. Avant de signer  
B. Si nous gagnons  
C. Quelque chose change

---

# 5. NON-RÉGRESSION

Tout travail V3 conserve :

- P0–P7 ;
- P5 exact package ;
- dépôt humain ;
- `UNKNOWN/PARTIAL/REVIEW_REQUIRED/NOT_PERFORMED` ;
- Patron/Collaborateur ;
- MFA ;
- tenant ;
- provenance ;
- idempotence ;
- append-only ;
- REX contrôlé ;
- voie manuelle sans IA.

---

# 6. DOCUMENTS À SYNCHRONISER APRÈS VALIDATION

Cible :

```text
docs/Actifs/02_Produit_et_UX/
  00_INDEX_REFERENCE_ACTIVE.md
  SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.0.md

docs/Actifs/01_Cahiers_des_charges/
  SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.0.md
  SMART_AO_PRODUCT_V3_TRACEABILITY_MATRIX.md

docs/03_PRODUCT_DESIGN_WORKING/
  SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md
```

Archiver/superséder selon les conventions existantes, sans supprimer l’histoire.

---

# 7. RÈGLE D’ARBITRAGE

Si V3 semble contredire le code :

- ne pas forcer le code ;
- documenter l’écart.

Si V3 semble contredire l’autorité active :

- ne pas réécrire l’autorité silencieusement ;
- signaler `OWNER_REOPEN_REQUIRED`.

Si le code contient une meilleure abstraction compatible :

- proposer `KEEP/ADAPT`.

Si un objet V3 n’existe pas :

- `ABSENT`, pas invention immédiate.

---

# 8. LIVRABLE ATTENDU DE CODEX

La première réponse de Codex doit être un **rapport**, pas une PR fonctionnelle.

Elle doit finir par :

```text
CURRENT HEAD:
DOC AUTHORITY:
DEEP CORE COVERAGE:
TOP DUPLICATION RISKS:
TOP DATA MIGRATION RISKS:
TOP SECURITY RISKS:
RECOMMENDED OWNERSHIP MODEL:
RECOMMENDED FIRST PR:
ROLLBACK:
OWNER DECISIONS REQUIRED:
```

---

# 9. OBJECTIF

La réussite de ce réalignement n’est pas de “moderniser” SMART AO.

Elle est d’éviter de terminer un produit déjà banalisé.

SMART AO V3 doit gagner par sa profondeur :

> **relier ce que le marché disait avant signature à ce que l’entreprise vit après attribution — avec preuve, impact, autorité et temporalité.**
