# SMART AO — DEC-GATE — Décision Gate 0 et registre des arbitrages

**Date de proposition :** 12 septembre 2026  
**Référence auditée :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** À DÉCIDER PAR LE PROPRIÉTAIRE  
**Recommandation Codex :** **HOLD GATE 0 GLOBAL — GO BORNÉ POUR A0 PUIS A1 APRÈS APPROBATION**

## 1. Décision demandée

L'audit sait décrire ce qui existe, attribuer les owners et proposer une trajectoire réversible. Il ne dispose pas encore d'un environnement PostgreSQL reproductible ni d'un Golden DCE réel. Le Gate 0 global ne doit donc pas autoriser A2–A4.

La décision recommandée est :

1. approuver le présent dossier comme sortie de Phase 0 ;
2. figer le corpus normatif et ses empreintes dans Git ;
3. autoriser **PR-A0 uniquement** ;
4. autoriser **PR-A1 seulement après réussite de Gate A0** ;
5. maintenir A2, A3, A4, B–I et tout pilote réel en HOLD ;
6. revenir devant le propriétaire à Gate A1 avant A2.

Codex s'arrête après ce dossier, conformément au mandat. Cette recommandation ne vaut pas autorisation implicite de commencer A0.

## 2. Réponses obligatoires du Gate 0

| Question | Réponse | Preuve | Action bornée |
|---|---|---|---|
| 1. Sait-on précisément ce qui existe et fonctionne ? | **PARTIEL** | AUD-00 à AUD-06 ; code et contrôles ciblés | A0 : baseline globale et PostgreSQL réel |
| 2. Chaque objet cible a-t-il un owner et une trajectoire ? | **OUI DANS LE PLAN, PARTIEL DANS LE CODE** | MAP-01 + MIG-01 | matérialiser progressivement, sans big bang |
| 3. Chaque exigence critique a-t-elle une tranche et une preuve ? | **OUI DANS TRC-01, NON EXÉCUTÉE** | TRC-01 | A1 : Golden puis gates par incrément |
| 4. A0–A4 sont-elles additives, réversibles et compatibles ? | **OUI COMME CONCEPTION, NON PROUVÉES SUR DB** | PLAN-A + AUD-03 | tests migration/rollback par PR |
| 5. Environnement et Golden permettent-ils les régressions ? | **NON** | AUD-04 + QUAL-01 | A0 puis A1 |

Une réponse négative interdit le GO global selon la v3.1. L'action bornée n'est pas une refonte : elle est précisément A0/A1.

## 3. Décisions de Gate 0 à signer

| ID | Décision | Proposition | Propriétaire | Date limite | Bloque |
|---|---|---|---|---|---|
| G0-01 | accepter les 14 rapports comme dossier Phase 0 | OUI, sous corrections éditoriales mineures éventuelles | Propriétaire SMART AO | avant A0 | clôture Phase 0 |
| G0-02 | verdict Gate 0 | HOLD global, GO A0 borné | Propriétaire SMART AO | avant A0 | toute PR A |
| G0-03 | commit normatif | versions listées dans AUD-00 + dossier Gate 0 | Propriétaire + responsable repo | entrée A0 | reproductibilité |
| G0-04 | périmètre A0 | seulement environnement/tests/migrations existantes/docs bootstrap | Architecte/Tech Lead | entrée A0 | scope A0 |
| G0-05 | seuil Gate A0 | toutes suites terminales, statique verte, PostgreSQL réel | Quality Owner | revue A0 | A1 |
| G0-06 | gouvernance Golden | trois bancs, DCE réels hors Git, droits par cas | Corpus Owner + DPO | revue A1 | A2 |
| G0-07 | première sélection Golden | cas représentatifs, droits établis, formats hostiles | Corpus Owner | pendant A1 | baseline |
| G0-08 | schéma SourceAnchor | types, locator, cardinalité, owner Evidence | Architecte + expert documentaire | Gate A1 | A2 |
| G0-09 | sémantique Evidence | nom distinct, validation, révocation, provenance | Architecte + métier | Gate A2 | A3 |
| G0-10 | stratégie Requirement | liaison, portée, criticité, invalidation | Architecte + métier | Gate A3 | A4 |
| G0-11 | politique de rollback schéma | pas de downgrade destructif, switch applicatif | Tech Lead + Ops | avant A2 | A2–A4 |
| G0-12 | propriétaire de l'invalidation | Evidence publie, owners aval réagissent | Architecte | Gate A3 | A4 |

## 4. DEC-01 à DEC-10 métier

Ces décisions restent réversibles pendant A0/A1. Elles ne doivent pas devenir des contraintes irréversibles dans les tables ou l'UX.

| ID | Orientation de travail | Propriétaire | Preuve avant fermeture | Date limite |
|---|---|---|---|---|
| DEC-01 Client initial | PME BTP 10–100, pilotes mono et multi-métiers | Dirigeant SMART AO | entretiens profils + sélection pilotes | avant premier pilote |
| DEC-02 Cycle vendu | DCE→dépôt + GO/NO-GO + passation minimale | Dirigeant | recettes bout-en-bout | Gate A, avant choix B–I |
| DEC-03 Public/privé | reconnaître les deux, garantir public d'abord | Dirigeant + juriste | 15 DCE privés + matrice juridique | avant promesse privée |
| DEC-04 Chiffrage | contrôler/compléter import existant | Dirigeant + experts prix | cas Excel/logiciel et MIRP | avant incrément Pricing |
| DEC-05 Dépôt | préparer/contrôler/autoriser/prouver | Dirigeant + responsable offre | essais multi-plateformes | avant automatisation canal |
| DEC-06 Veille | sources ouvertes ciblées puis fournisseur si gain | Dirigeant produit | rappel/précision/coût | avant connecteur payant |
| DEC-07 Contenus payants | seulement si droit prouvé, sinon référence | Dirigeant + conseil PI | matrice licence | avant ingestion payante |
| DEC-08 Limite juridique | détecter/citer/expliquer, expert décide | Dirigeant + juriste | protocole d'escalade | avant fonctionnalités juridiques |
| DEC-09 Données/IA | niveaux de sensibilité et solution par niveau | Dirigeant + DPO/RSSI | analyse de risques/providers | avant données réelles IA |
| DEC-10 Valeur | temps, erreurs évitées, NO-GO, marge à risque, passation | Dirigeant produit | protocole avant/après | avant pilote puis trimestriel |

## 5. DEC-11 active

| ID | Contrainte | Statut | Owner | Preuve continue |
|---|---|---|---|---|
| DEC-11 | instance dédiée par client, application tenant-aware, un code produit | ACTIVE | Architecture/Platform | tests tenant + même release sur instances |

La décision reste active tant qu'une nouvelle ADR ne démontre pas un besoin économique et une sécurité équivalente pour une autre forme de déploiement.

## 6. Décisions techniques et opérationnelles restantes

| ID | Sujet | Option de travail non irréversible | Propriétaire | Fermeture au plus tard |
|---|---|---|---|---|
| TECH-01 | hébergeur/région | France/EEE à sélectionner | Dirigeant + Ops + DPO | pilote réel |
| TECH-02 | unité de déploiement | compose/VM dédiée comme baseline | Architecte/Ops | deuxième instance |
| TECH-03 | PostgreSQL managé | mesurer coût/ops | Ops | pilote + RPO/RTO |
| TECH-04 | stockage objet | local chiffré vs objet régional | Ops/DPO | ingestion réelle |
| TECH-05 | retrieval final | baseline exacte/vectorielle d'abord | Quality/AI | après A1 et benchmark |
| TECH-06 | fournisseur/région LLM | aucun choix avant data flow | Dirigeant/DPO/AI | avant IA réelle |
| TECH-07 | RPO/RTO | fixer après exercice et besoin client | Ops/Dirigeant | pilote |
| TECH-08 | secrets | gestionnaire, rotation, séparation client | Security/Ops | pilote |
| TECH-09 | support Maroc | JIT borné et contractualisé | DPO/Security/Dirigeant | pilote |
| TECH-10 | DPA/SCC/sous-traitants | registre par provider | DPO/Juriste | contrat pilote |
| TECH-11 | Control Plane | métadonnées seulement, différé | Architecte/Ops | plusieurs instances |
| TECH-12 | quotas/tarification | mesurer avant modèle | Dirigeant | offre commerciale |
| TECH-13 | ERP bidirectionnel | fichiers d'abord | Produit/Architecture | besoin pilote prouvé |
| TECH-14 | dépôt automatisé | canal par canal | Produit/Juriste | recette plateforme |
| TECH-15 | multi-tenant mutualisé | différé | Dirigeant/Architecture | besoin économique démontré |

## 7. RACI des gates

| Gate | Accountable | Responsible | Consultés | Preuve à signer |
|---|---|---|---|---|
| Gate 0 | Propriétaire SMART AO | Codex/Architecture pour le dossier | métier, qualité, sécurité | ce document + 13 annexes |
| Gate A0 | Tech Lead | développeur/Ops | Quality/Security | rapport commandes/DB/migrations |
| Gate A1 | Quality Owner | Corpus Owner + développeur | experts métiers/DPO | baseline Golden gelée |
| Gate A2 | Architecte | développeur DCE/Evidence | experts formats/Quality | anchors et backfill |
| Gate A3 | Architecte métier | développeur Evidence | DCE/Decision/Pricing | Evidence et compatibilité |
| Gate A / A4 | Propriétaire SMART AO | Architecture + équipes contextes | métier/Quality/Security/Ops | recettes C1 et rollback |
| Pilote réel | Propriétaire + DPO | Ops/Product/Security | juriste/clients pilotes | dossiers §17 v3.1 |

## 8. Formulaire de décision

À consigner dans une ADR ou un compte rendu daté :

```text
Décision Gate 0 : APPROUVÉ / REFUSÉ / À REPRENDRE
PR-A0 autorisée : OUI / NON
Conditions :
Owner PR-A0 :
Date de revue Gate A0 :
PR-A1 préautorisée sous réussite Gate A0 : OUI / NON
Signataire et date :
```

L'absence de décision explicite maintient le HOLD.

## 9. Références du dossier

- [AUD-00 — checkout et périmètre](./SMART_AO_PHASE0_AUD-00_CHECKOUT_PERIMETRE.md)
- [AUD-01 — carte repo](./SMART_AO_PHASE0_AUD-01_CARTE_REPO.md)
- [AUD-02 — runtime](./SMART_AO_PHASE0_AUD-02_RUNTIME_FLUX.md)
- [AUD-03 — DB](./SMART_AO_PHASE0_AUD-03_DB_MIGRATIONS.md)
- [AUD-04 — tests](./SMART_AO_PHASE0_AUD-04_TESTS_ENVIRONNEMENT.md)
- [AUD-05 — flux DCE](./SMART_AO_PHASE0_AUD-05_FLUX_DCE.md)
- [AUD-06 — modules métier](./SMART_AO_PHASE0_AUD-06_MODULES_METIER.md)
- [MAP-01 — owners et contextes](./SMART_AO_PHASE0_MAP-01_CONTEXT_MAP.md)
- [MIG-01 — migration](./SMART_AO_PHASE0_MIG-01_MATRICE_MIGRATION.md)
- [TRC-01 — traçabilité](./SMART_AO_PHASE0_TRC-01_TRACABILITE_NORMATIVE.md)
- [QUAL-01 — Golden DCE](./SMART_AO_PHASE0_QUAL-01_GOLDEN_DCE.md)
- [SEC-DATA-01 — sécurité et données](./SMART_AO_PHASE0_SEC-DATA-01_SECURITE_DONNEES_OPS.md)
- [PLAN-A — PR-A0 à A4](./SMART_AO_PHASE0_PLAN-A_PR-A0_A4.md)
