# SMART AO — AUD-00 — Checkout, référence et périmètre audité

**Date d'observation :** 12 septembre 2026  
**Statut :** TERMINÉ — preuve de Phase 0  
**Verdict :** checkout identifié, périmètre audité, corpus directeur non encore figé dans Git

## 1. Décision en une page

L'audit porte sur le checkout local `SMART_AO_V8`, branche `feat/ccap-cctp-risk-register-20260831`, au commit `b6b05b80434c7fa407c1351598d364624062373e`. Le dépôt contient un produit substantiel, mais son état de travail est très sale : de nombreuses suppressions suivies et de nombreux fichiers non suivis préexistaient à la Phase 0. Aucun de ces changements n'a été nettoyé, restauré ou attribué à l'audit.

La référence v3.1 et le mandat Phase 0 sont exploitables, mais ils sont eux-mêmes non suivis. Le corpus normatif est donc identifiable par ses empreintes, sans être encore rattaché à un commit documentaire stable. Cette faiblesse empêche de répondre entièrement « oui » à la première question du Gate 0.

Le mandat est respecté : seules des lectures, mesures, exécutions de commandes existantes et créations de rapports ont été réalisées. Aucun modèle, service, migration, worker, route, composant frontend ou comportement métier n'a été modifié.

## 2. Référence Git observée

| Élément | Valeur | Qualification |
|---|---|---|
| Racine | `/home/noor/PROJECTS/BTP/SMART_AO_V8` | observée par `git rev-parse --show-toplevel` |
| Branche | `feat/ccap-cctp-risk-register-20260831` | observée |
| Commit | `b6b05b80434c7fa407c1351598d364624062373e` | observé |
| État | très sale | suppressions suivies et fichiers non suivis sans rapport avec l'audit |
| Pull request | non établie | CLI GitHub absente ; aucune déduction faite |
| Référentiel déclaré | `mailtkarim-bot/SMART_AO_V8` | configuration projet ; URL distante non revalidée |

La référence technique de ce dossier est le triplet **racine + branche + SHA**. Le contenu non suivi exige en plus les empreintes ci-dessous.

## 3. Corpus directeur et empreintes SHA-256

| Document | SHA-256 observé | Statut Git |
|---|---|---|
| `SMART_AO_Cahier_des_charges_Metier_v1.0.md` | `0d29febbcf6b74f1975c2e93960c91eb3d250d25866d79710a28a28392642f63` | non suivi |
| `SMART_AO_Univers_documentaire_metier_v1.0.md` | `6798bd6409de0339fa288fee2951df2b7aed27f6516609aa9a983512c5ba20fe` | non suivi |
| `SMART_AO_Benchmark_Concurrentiel_UX_Parcours_v1.0.md` | `add3bb2e472f4057f1e064b76c3983184cdf8d3549dbef8933684befc04d78cd` | non suivi |
| `SMART_AO_CCF_UX_Product_Blueprint_v1.1.md` | `c93ba2e792ba57e1f8ee791e404e4b17bdf7de184a9ff2bfc0694a0c0814450f` | non suivi |
| `SMART_AO_Registre_Decisions_Architecture_Preliminaires_v0.1.md` | `58d732d7168c212f8fcb1f424a4c8e9aec9faa6de4da06ce985989275f77a7f7` | non suivi |
| `SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md` | `b11a264f72c550780fdcb76b043d84bf6473b3ed2c8460d8748afeb142640c64` | non suivi |
| `SMART_AO_Mandat_Codex_Phase0_v1.0.md` | `bbdd46fbd5043c2485099ca524a544d76f42e9f18b45e9a93f3d483bef719862` | non suivi |
| `SMART_AO_Cahier_des_charges_Architecture_Metier_v2.3.docx` | `2e8dbd7785ea7cd88e6c5d2ad9c1baaf681a67a5f71a801511cf2c86cbd0664e` | non suivi, héritage |
| `SMART_AO_Architecture_Logicielle_v3.0_PLAN_DIRECTEUR_FINAL.md` | `fb616536c3eecc0ec5fc51743fbe39994e58942e0587ba32d436b207cc2716bb` | non suivi, supersédé |
| `SMART_AO_Revue_Croisee_Plan_Directeur_Architecture_v3.0.md` | `2081e04e8c6356966aebe81f49d5c5e218cd11083d5ee239cf2a7c9ed65f6479` | non suivi, justification de v3.1 |

## 4. Périmètre effectivement audité

### Inclus

- corpus directeur v3.1 et documents métier, documentaire, UX et ADR associés ;
- code Python de `backend/app`, ses modules, couches publiques et dépendances ;
- routes HTTP, composition runtime et workers ;
- modèles SQLAlchemy et chaîne Alembic ;
- stockage des documents, quarantaine et flux externes configurés ;
- tests backend, tests d'architecture, contrôles statiques et frontend ;
- flux DCE depuis l'entrée jusqu'à `DceRequirement` et sa confirmation ;
- modules métier exigés par le mandat ;
- squelette Golden DCE et corpus DCE externe fourni, seulement sous forme d'inventaire ;
- sécurité, confidentialité, données, exploitation et support à partir du code et des configurations présentes.

### Exclus par mandat

- toute modification du cœur ;
- migrations ou données réelles ;
- déploiement sur VPS ou branchement de fournisseurs ;
- ingestion ou copie des DCE externes dans Git ;
- création de `SourceAnchor`, `Evidence`, agents, providers ou nouvelle pile de recherche ;
- refonte frontend et suppression de composants.

## 5. Méthode et niveau de preuve

| Niveau | Sens dans les rapports |
|---|---|
| `COUVERT` | preuve reproductible dans le code ou par un contrôle réussi |
| `PARTIEL` | capacité existante, mais portée incomplète ou preuve non bout-en-bout |
| `ABSENT` | aucun propriétaire ou mécanisme probant trouvé |
| `DIFFÉRÉ` | cible volontairement reportée par la référence v3.1 |
| `BLOQUÉ` | contrôle pertinent impossible dans l'environnement observé |

Le code et les tests ont priorité sur les descriptions. Les documents définissent la cible et les invariants. Les comptages statiques de contraintes et de dépendances ne remplacent pas l'inspection d'un PostgreSQL actif.

## 6. Limites matérielles

1. Le démon Docker n'est pas accessible depuis l'environnement d'audit ; PostgreSQL réel, restauration, ClamAV/EICAR et composition active ne sont pas qualifiés.
2. Le manifeste Golden DCE contient zéro document ; aucune régression métier représentative ne peut être mesurée.
3. La suite backend non-DB se bloque sur un test de route précis ; la campagne complète n'a donc pas de résultat terminal.
4. Le corpus DCE externe a été inventorié sans ouverture exhaustive, copie, anonymisation ni validation des droits.
5. Aucun fournisseur externe ni VPS réel n'a été sollicité.

## 7. Errata de la référence v3.1

Deux reliquats éditoriaux sont présents dans la section 1.2 :

- ligne observée 56 : v2.3 est dite « absorbée par v3.0 » ; la référence active est v3.1 ;
- ligne observée 68 : « v3.0 tranche » ; la décision doit être attribuée à v3.1.

Ils n'altèrent pas le mandat, mais doivent être corrigés dans une révision documentaire contrôlée afin d'éviter une ambiguïté future.

## 8. Réponse Gate 0 portée par AUD-00

**Question 1 — savons-nous précisément ce qui existe et fonctionne ? `PARTIEL`.** La cartographie du checkout est précise ; l'état réel PostgreSQL et le corpus normatif commité ne le sont pas. Action bornée proposée : décider Gate 0, figer le corpus, puis exécuter PR-A0.

## 9. Preuves principales

- `rapports/SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`
- `rapports/SMART_AO_Mandat_Codex_Phase0_v1.0.md`
- `AGENTS.md`
- `.codex/basic-memory.json`
- [AUD-04 — Tests et environnement](./SMART_AO_PHASE0_AUD-04_TESTS_ENVIRONNEMENT.md)
- [DEC-GATE — Décision proposée](./SMART_AO_PHASE0_DEC-GATE_DECISIONS.md)

