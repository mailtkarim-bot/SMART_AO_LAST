# SMART AO — Preuve d’exécution G01–G09

**Date :** 20 septembre 2026  
**Autorités :** cahier OWNER produit/métier v0.4, catalogue OWNER UX v0.3, registre `SMART_AO_G01_G52`  
**Périmètre :** flux réels DCE, de la réception/quarantaine à la lecture et à la qualification des exigences  
**Verdict :** preuves techniques reliées aux actes métier ciblés, aucune acceptation métier globale déclarée

## 1. Objectif et règle de preuve

Cette passe joue G01 à G09 sur les services, la persistance PostgreSQL et les routes HTTP déjà disponibles. Un test vert prouve le comportement couvert par ce test ; il ne transforme pas à lui seul une recette métier, une validation externe ou une revue humaine en acceptation.

La commande exécutée contre PostgreSQL Docker est :

```text
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao' ./.venv/bin/pytest -q \
  backend/tests/application/test_dce_document_extraction.py \
  backend/tests/application/test_dce_document_classification.py \
  backend/tests/application/test_dce_upload.py \
  backend/tests/application/test_dce_staging.py \
  backend/tests/application/test_dce_analysis_worker.py \
  backend/tests/application/test_dce_rc_analysis.py \
  backend/tests/application/test_dce_requirements.py \
  backend/tests/application/test_dce_requirements_worker.py \
  backend/tests/application/test_dce_requirement_confirmation.py \
  backend/tests/application/test_case_dce_reading_projection.py \
  backend/tests/api/test_dce_staging_routes.py \
  backend/tests/api/test_dce_authenticated_api.py \
  backend/tests/api/test_case_dce_reading_routes.py --tb=short
```

Résultat réel : **105 tests réussis, 5 avertissements, 115,20 s**. Les avertissements sont des dépréciations Starlette/httpx et 422 ; aucun échec fonctionnel n’est observé.

Une seconde passe de fixtures métier a ensuite été ajoutée dans `backend/app/platform/quality/data/g01_g09_business.json` et rejouée par `backend/tests/application/test_g01_g09_business_fixtures.py` : **10 tests réussis** (9 unitaires, 1 PostgreSQL). Chaque fixture porte maintenant un acte métier et deux références de preuve contrôlées par le parseur fermé. Le détail de la liaison se trouve dans `SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md`.

## 2. Résultat par scénario

| Scénario | Flux réellement prouvé | État de cette passe | Limite restante |
|---|---|---|---|
| **G01** | Projection/extraction sourcée, absence de signal sans prétendre à une absence, exigences atomiques et gate P3/P5 bloqué quand les exigences ne sont pas confirmées. | **PREUVE RELIÉE — décision de gate** | La décision Patron complète et l’autorisation effective restent séparées. |
| **G02** | Versions non admises/non vérifiées refusées, consultation obsolète refusée, admission rejouée sans doublon et autorisation d’une ancienne version refusée par conflit de version. | **PREUVE RELIÉE — contrôle P5** | Un nouveau paquet doit recevoir une nouvelle autorisation ; aucun héritage automatique. |
| **G03** | Analyse RC/CCAP sourcée, taxonomie CCAP/CCTP déterministe, deux sources conservées sans priorité automatique, conflit résolu par un acte humain motivé. | **PREUVE RELIÉE — résolution humaine** | La résolution choisit une contribution sans effacer l’autre. |
| **G04** | Besoin de levage sans ligne dédiée projeté comme `CAPABILITY_GAP` bloquant, avec source CCTP, action de revue et événement `CapabilityGapReported` append-only. | **PREUVE RELIÉE — revue Patron** | Aucun coût ni hypothèse n’est accepté automatiquement. |
| **G05** | Projections DOCX/XLSX avec ancres de paragraphe/cellule, hash et extraction immuable ; un brouillon dérivé versionné conserve la source et reste soumis à revue. | **PREUVE RELIÉE — édition dérivée** | Le brouillon n’est ni une validation ni un dépôt. |
| **G06** | Page illisible, OCR sous revue, limites de taille et échéance absente projetée en `DEADLINE_MISSING` sans invention de date ; l’inconnu reste lisible côté Patron. | **PREUVE RELIÉE — revue Patron** | La date doit être confirmée par une source, jamais déduite. |
| **G07** | PDF protégé détecté et déclaré sans tentative de contournement ni extraction fabriquée. | **PREUVE TECHNIQUE** | La revue métier doit confirmer le blocage du processus dépendant du fichier protégé. |
| **G08** | Archive au-delà de la limite refusée, inventaire borné et éléments non traités rendus visibles ; reprise possible après rejet. | **PARTIEL — preuve technique** | Il reste à jouer le parcours d’inventaire partiel et de reprise avec un manifeste d’archive métier complet. |
| **G09** | Instruction hostile classée `REVIEW_REQUIRED`, contenu mis en quarantaine/fail-closed, aucune exécution ni transmission IA. | **PREUVE VERTICALE TECHNIQUE** | La décision de revue et son événement append-only doivent être reliés à la recette métier G09 complète. |

## 3. Correspondance des preuves

Les preuves les plus directement reliées aux scénarios sont :

- extraction : provenance PDF/DOCX/XLSX/texte, extraction protégée, limites, OCR sous revue et rejeu immuable (`test_text_extraction_is_sourced_immutable_and_replayed_without_outbox_leak`, `test_protected_pdf_is_reported_without_attempting_extraction`, `test_ocr_projection_is_persisted_under_review_and_replayed`) ;
- classification : classification sourcée, absence de signal, refus d’un acteur non système, projection immuable et rejeu (`test_dce_document_classification_is_sourced_immutable_and_replayed`, `test_classification_is_safe_for_absence_of_signal_or_competing_families`) ;
- réception et quarantaine : intention privée tenant-scoped, antivirus fail-closed, limites incrémentales, suppression des partiels et reprise (`test_prepare_dce_staging_creates_private_tenant_scoped_intent_and_durable_event`, `test_scan_error_is_fail_closed_and_marks_staged_object_rejected`, `test_recovery_prepares_a_new_intention_after_rejected_upload`) ;
- analyse et exigences : règles sourcées, taxonomie reproductible, limite terminale, exigences atomiques, confirmation historique et rejeu (`test_rc_analysis_is_sourced_immutable_and_replayed_without_text_leak`, `test_ccap_cctp_taxonomy_is_classification_scoped_and_reproducible`, `test_requirements_are_atomic_sourced_immutable_and_replayed`) ;
- exposition HTTP : bearer obligatoire, tenant résolu côté serveur, refus neutre des autres tenants, absence de faits de stockage et lecture fermée (`test_dce_upload_requires_bearer_streams_to_quarantine_and_returns_no_storage_facts`, `test_dce_read_is_neutral_and_audited_for_other_tenant`, `test_case_dce_reading_returns_closed_projection_and_uses_server_tenant`).

## 4. Décision de tranche

G01–G09 restent **non clôturés** dans le registre G01–G52. Cette passe établit une base technique robuste et reproductible, mais elle ne prétend pas couvrir les décisions humaines, les intégrations externes, la recette UI manuelle ou l’acceptation propriétaire. Aucun scénario n’est donc marqué `ACCEPTÉ MÉTIER`.

La liaison des preuves aux actes ciblés est maintenant matérialisée dans le catalogue et vérifiée par les tests réels. Les fixtures restent versionnées et rejouables ; aucun statut d’acceptation métier globale n’est avancé. La prochaine tranche porte sur les contrôles d’accessibilité, de responsive et de fuite de données avant le gel UX.

## Références

- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G52_EXECUTION_MATRIX_v0.1.md`
- `backend/app/platform/quality/data/g01_g52.json`
- `backend/app/platform/quality/data/g01_g09_business.json`
- `backend/app/platform/quality/business_fixtures.py`
- `backend/tests/application/test_g01_g09_business_fixtures.py`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G09_ACTES_METIER_PREUVE_v0.1.md`
- `backend/app/platform/quality/recipe_catalog.py`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`
- `docs/00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`
