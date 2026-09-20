# SMART AO — AUD-03 — PostgreSQL, modèles, migrations et données à migrer

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** TERMINÉ EN STATIQUE — validation live BLOQUÉE  
**Verdict :** schéma riche et migrations linéaires ; évolution A2–A4 faisable en expand/contract, mais non autorisée avant Gate 0

## 1. État mesuré

| Mesure | Résultat |
|---|---:|
| Fichiers de migration Alembic | 67 |
| Révision tête | `20260826_0067` |
| Branches de migration | une chaîne linéaire observée |
| Tables ORM importées | 102 |
| Occurrences statiques `CheckConstraint` | 336 |
| Occurrences statiques de clés étrangères | 245 |
| Occurrences statiques `UniqueConstraint` | 200 |
| Index déclarés dans les migrations | 191 |
| Déclarations de triggers dans les migrations | 57, réparties dans 44 fichiers |
| Déclarations de fonctions SQL | 50, réparties dans 40 fichiers |

Ces comptages sont des indicateurs de densité, pas un catalogue live. Les contraintes réellement installées, leur validité et le volume des tables exigent une connexion PostgreSQL.

## 2. Résultat Alembic

La génération SQL hors ligne de la base vide à la tête passe avec l'environnement `uv` et une URL PostgreSQL syntaxique. `backend/alembic/env.py` importe les modèles des modules et de la sécurité Platform, ce qui permet à la metadata de connaître le schéma actuel.

Non prouvé :

- upgrade sur PostgreSQL vide ;
- upgrade d'une base V8 peuplée ;
- durée, locks et taille des backfills ;
- downgrade/rollback opérationnel ;
- comparaison ORM ↔ catalogue live ;
- sauvegarde/restauration avant migration.

## 3. Groupes de données autoritatives

| Groupe | Exemples de tables | Contexte cible |
|---|---|---|
| Platform/tenancy | tenants, command receipts, domain events, outbox, inbox | Platform |
| Sécurité | identities, credentials, memberships, sessions, MFA, audit | Identity & Access |
| Affaire | cases et projections associées | Case / Affair |
| DCE | consultations, versions, documents, staging, extractions, fragments, classifications, analyses, exigences, confirmations, impacts | DCE + Evidence |
| Décision | décisions, transitions, risques, traitements, liens risque-exigence, contextes figés | Decision & Governance |
| Entreprise | sociétés, documents, versions, capacités, preuves | Enterprise Memory |
| Knowledge | embeddings, benchmarks/lectures | AI/Knowledge baseline |
| Opportunité | profils de veille, avis, qualifications | Opportunity / Radar |
| Travail | affectations, tâches, bloqueurs, collaborations | Collaboration & Work |
| Actions patron | actions et transitions | Decision / Collaboration |
| Préparation | paquets, documents, revues, corrections, transmissions | Response & Artifacts |
| Prix | scénarios, lignes/imports, snapshots, publications | Pricing Intelligence |
| Remise | packages, exports, preuves, signatures | Submission |
| Optimisation | plans et runs de capacité | Collaboration/Optimization différé |

## 4. Données DCE à préserver

### `DceVersion`

La version conserve le hash du corpus, les documents originaux, la provenance, la chaîne de prédécesseurs, le cycle de vie et l'état de préparation d'analyse. Elle est le pivot de toute future preuve. Elle doit être **KEEP + ADAPT**, sans reconstruction silencieuse des historiques.

### Extractions et fragments

Les extractions ont des états terminaux explicites (`COMPLETED`, `REVIEW_REQUIRED`, `UNSUPPORTED`, `REJECTED_LIMIT`, `FAILED_SAFE`) et les fragments conservent un locator JSON, du texte et des hashes. Ces éléments sont **KEEP** et servent de source au backfill des ancres.

### `DceRequirement`

L'objet existe déjà, rattaché à un run de matérialisation et à des observations sources. Il porte type, signal de directive et `PENDING_HUMAN_CONFIRMATION`. Les confirmations sont immuables, chaînées par prédécesseur, avec une projection courante. Il doit être **ADAPT**, pas recréé.

### Evidence locales

`dce_document_classification_evidence` et `submission_evidence` ont aujourd'hui des sémantiques spécifiques. Les champs de preuve présents dans les transitions de risques sont encore un troisième usage. Toute Evidence générique doit être additive et nommée sans collision sémantique.

### Knowledge dérivé

Les embeddings stockent une copie du texte du fragment, un vecteur JSONB, le modèle et le locator. Le cycle d'effacement doit supprimer ou rendre inexploitables toutes les copies dérivées lorsque leur source est retirée.

## 5. Changements de données envisagés après autorisation

| Objet cible | État actuel | Évolution minimale | Backfill | Compatibilité |
|---|---|---|---|---|
| `SourceAnchor` | absent comme objet générique | nouvelle table additive, référence DCE/version/document/fragment + locator typé | depuis fragments/offsets existants, sans inventer page/box | lecteurs actuels conservés |
| `Evidence` générique | absent | nouvelle table additive reliée à anchor et provenance | créer seulement quand la preuve source est déterministe | Evidence locales inchangées |
| lien Requirement→Evidence | absent | table de liaison ou FK additive selon cardinalité mesurée | depuis `DceRequirementSource` | ancien chemin de lecture actif |
| portée/criticité/applicabilité | partielle | colonnes additives ou objets associés | `UNKNOWN`/revue, jamais valeur inventée | API versionnée ou champs optionnels |
| invalidation | limitée aux impacts DCE | registre/événement dépendant des preuves actives | aucun historique réécrit | projection reconstruisible |
| corpus Golden | manifeste vide | métadonnées hors Git + hashes + annotations | aucun document sans droits | séparé de la production |

## 6. Stratégie de migration

1. **Expand** : créer les structures neuves sans supprimer ni rendre obligatoire un champ nouveau.
2. **Backfill idempotent** : travailler par lots, enregistrer version d'algorithme et compteurs, mettre en revue tout cas ambigu.
3. **Dual-read contrôlé** : comparer ancien locator et nouvelle ancre dans les tests Golden ; aucun basculement tant que les écarts critiques ne sont pas nuls.
4. **Switch** : activer le nouveau propriétaire par capacité, avec rollback de configuration.
5. **Contract ultérieur** : supprimer seulement après télémétrie, parité, sauvegarde et décision dédiée ; aucune suppression n'est prévue dans A0–A4.

## 7. Contraintes à exiger dans A2–A4

- tenant présent sur toute ligne et toute référence composée ;
- aucune ancre vers un document d'une autre version/tenant ;
- Evidence immuable ou supersédée, jamais éditée silencieusement ;
- requirement confirmé lié à la version et à la preuve réellement validées ;
- unicité des projections « current » et historique conservé ;
- état d'invalidation explicite après rectificatif ;
- idempotence de tout backfill ;
- aucune valeur de portée, criticité ou page inventée ;
- migration de downgrade limitée à la structure neuve tant qu'aucun writer n'en dépend.

## 8. Gate de données

**Statut : `BLOQUÉ`.** L'offline SQL prouve la cohérence syntaxique de la chaîne, pas sa sûreté sur une base réelle. PR-A0 doit fournir PostgreSQL reproductible, snapshot anonymisé ou généré, upgrade/downgrade, vérification des contraintes et mesure de temps avant toute autorisation A2.

## 9. Preuves

- `backend/alembic/versions/`
- `backend/alembic/env.py`
- `backend/app/modules/dce/infrastructure/models/`
- `backend/app/modules/decision/infrastructure/models/`
- `backend/app/modules/knowledge/infrastructure/models.py`
- [MIG-01](./SMART_AO_PHASE0_MIG-01_MATRICE_MIGRATION.md)
- [PLAN-A](./SMART_AO_PHASE0_PLAN-A_PR-A0_A4.md)
