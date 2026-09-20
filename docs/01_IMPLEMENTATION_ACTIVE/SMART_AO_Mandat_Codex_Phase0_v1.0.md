# SMART AO — Mandat Codex Phase 0

**Version : 1.0 — 12 septembre 2026**  
**Autorisation : AUDIT ET MESURE UNIQUEMENT — HOLD SUR LE CŒUR**

## Mission

Auditer le repo `SMART_AO_V8` contre `SMART_AO_Architecture_Logicielle_v3.1_REFERENCE_DIRECTRICE_PHASE0.md`, sans modifier le cœur métier, puis remettre le dossier de décision Gate 0.

## Livrables obligatoires

1. `AUD-00` — checkout, commit et périmètre ;
2. `AUD-01` — carte repo/modules/interfaces/dépendances ;
3. `AUD-02` — runtime, workers, stockages, flux externes ;
4. `AUD-03` — modèles DB, migrations, contraintes, données à migrer ;
5. `AUD-04` — commandes tests autoritatives, suites exécutées, skips, blocages ;
6. `AUD-05` — flux DCE jusqu’à `DceRequirement` et confirmation ;
7. `AUD-06` — Decision, Pricing, Enterprise, Submission, PatronAction, Knowledge, Opportunity, MarketWatch, Membership, Preparation, Optimization ;
8. `MAP-01` — V8 → contextes v3.1, propriétaire d’écriture, lecteurs, dépendances ;
9. `MIG-01` — KEEP / ADAPT / MOVE / CREATE / DEFER / DELETE avec preuve code ;
10. `TRC-01` — exigence normative → objet → contexte → module V8 → tranche/PR → test/preuve ;
11. `QUAL-01` — Golden DCE : état, droits, bancs, métriques, gouvernance ;
12. `SEC-DATA-01` — sécurité, confidentialité, données, exploitation, accès support ;
13. `PLAN-A` — plan PR-A0..A4, migrations, rollback, gates ;
14. `DEC-GATE` — décisions encore ouvertes, propriétaire et date limite.

## Questions Gate 0

1. savons-nous précisément ce qui existe et fonctionne ?
2. chaque objet cible a-t-il un propriétaire d’écriture et une trajectoire ?
3. chaque exigence critique a-t-elle un test/preuve et une tranche ?
4. A0–A4 sont-elles additives, réversibles et compatibles ?
5. l’environnement et le Golden DCE permettent-ils de mesurer les régressions ?

## Autorisé

Lire, rechercher, exécuter commandes existantes, lancer tests, inspecter migrations/schémas, mesurer, produire des rapports et proposer un plan.

## Interdit

Aucun rewrite, changement du cœur, migration destructive, renommage massif, microservice, GraphRAG, nouvel Agent Orchestrator, nouvelle stack retrieval, nouveau provider, suppression de composant, chantier frontend général, PR-A2/A3/A4 ou implémentation fonctionnelle non autorisée.

## Stop

À la fin de Phase 0, **s’arrêter** et remettre le dossier. Ne pas commencer PR-A0 avant décision explicite Gate 0.
