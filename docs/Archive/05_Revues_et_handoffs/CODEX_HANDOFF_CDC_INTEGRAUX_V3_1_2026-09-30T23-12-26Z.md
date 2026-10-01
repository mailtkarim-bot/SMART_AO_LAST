# Handoff — cahiers de charges intégraux V3.1

Date UTC : 2026-09-30T23:12:26.352796+00:00
Session Codex : 01a0dd50-89f0-7e32-80f6-0596c9518fca.

Le propriétaire a corrigé explicitement la condensation V3.1 : les CDC actifs doivent contenir tout le périmètre métier et technique, pas seulement des références aux archives. Les trois cahiers actifs existants ont donc été enrichis en place, sans toucher au code de production : intégralité Freeze v2, Master métier v2 (y compris métier v1, univers documentaire et arbitrages), technique v2.1 et les deux deltas V3 complets. La personnalisation et le cadrage V3.1 restent en tête, avec une table explicite des arbitrages de compatibilité.

La matrice de décisions D31-07 explique ce changement. Le manifest `SMART_AO_CDC_INTEGRAL_V3_1_COVERAGE_2026-09-30.json` et le test dans `backend/tests/ops/test_product_freeze_authority_contract.py` vérifient cinq sources : 9 241 lignes et 854 chapitres, conservation de chaque ligne/titre avec changement purement structurel des titres pour ancres uniques. Aucun détail métier supprimé parce qu'il est différé. Les anciennes mentions d'autorité/de priorité/ownership sont soumises à la table de consolidation active ; un conflit supplémentaire doit être documenté, pas effacé silencieusement. Tous les paragraphes substantiels longs du candidat Owner Freeze V3 sont également présents dans le Master V3 transmis et intégré.

Preuves du bloc : test documentaire 3/3, Ruff ciblé, git diff --check ; 549 liens locaux des trois CDC vérifiés (y compris ancres intégrées), zéro lien invalide. Les archives n'ont pas été modifiées. Aucun full backend/frontend, migration, commit ou push. Aucun comportement produit déclaré livré par l'ajout de texte.

Lire index → Freeze v3.1 intégral → Master métier v3.1 intégral → technique v3.1 intégral → plan global. L'ancien checkpoint documentaire court est antérieur et ne décrit plus la complétude actuelle. HEAD `1c8ac62`, checkout sale préexistant, WIP C08 migration0121 non qualifié à préserver ; baseline backend récente toujours partielle. NO-GO public et interdiction de push maintenus.

Basic Memory MCP indisponible : ce handoff est local, pas une note mémoire synchronisée. À synchroniser avec le plan quand le connecteur sera accessible. Ne pas inventer d'identifiant bm-orient.

Prochaine action : identifier le snapshot local et le WIP à qualifier, rétablir la baseline backend/frontend appropriée, puis livrer le bloc A1 source/version → applicabilité et impact déclaré → condition Patron → projection C07, avec preuve HTTP/PostgreSQL et sans ouverture publique.
