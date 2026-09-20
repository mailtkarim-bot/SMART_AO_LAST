# SMART AO — Liaison des preuves G01–G09 aux actes métier

**Date :** 20 septembre 2026  
**Statut :** preuve de liaison exécutée  
**Autorités :** cahier OWNER produit/métier v0.4, catalogue OWNER UX v0.3, registre `SMART_AO_G01_G52`

## Décision de tranche

Les fixtures G01–G09 ne restent plus de simples refus techniques. Chaque recette porte maintenant un acte métier explicite et deux références de preuve dans `backend/app/platform/quality/data/g01_g09_business.json`. Ces références pointent vers les services, handlers ou projections réellement présents dans le code ; elles ne déclarent pas une acceptation propriétaire globale.

Le choix est volontairement minimal : les actes append-only déjà existants sont réutilisés. Aucun registre parallèle de « validation métier » n’est ajouté, et aucun statut n’est avancé par convention.

## Correspondance exécutée

| Recette | Acte métier relié | Preuve réelle | État obtenu |
|---|---|---|---|
| G01 | décision de gate P3/P5 | `evaluate_submission_gate` + `test_g01_missing_plan_blocks_submission_gate` | `DEPENDENCY_UNPROVEN` |
| G02 | contrôle de version de l’autorisation P5 | `AuthorizeSubmissionPackageHandler` + `test_g02_rectificative_version_refuses_old_package_authorization` | `REVALIDATION_REQUIRED` |
| G03 | résolution humaine d’un conflit DCE | `DceContributionConflictService.resolve` + `test_concurrent_proposals_are_retained_blocked_and_resolvable` | `HUMAN_RESOLUTION_REQUIRED` jusqu’à résolution motivée |
| G04 | revue Patron du gap de capacité | `ReportCapabilityGapHandler` + `test_g04_missing_lifting_cost_is_a_blocking_case_gap` | `COST_HYPOTHESIS_REQUIRED` |
| G05 | création d’une édition technique dérivée | `PreparationReviewHandler._draft` + `test_response_draft_is_versioned_replayed_and_financial_payload_is_rejected` | brouillon versionné, source conservée |
| G06 | revue Patron d’un inconnu d’échéance | `PatronBoampObservationService.read` + `test_patron_read_marks_missing_deadline_as_unknown` | `DEADLINE_UNKNOWN` |
| G07 | revue d’un fichier protégé | `_project_document` + `test_g07_protected_file_is_refused_without_bypass` | processus dépendant bloqué |
| G08 | revue d’un inventaire borné | `_project_document` + `test_g08_archive_limit_leaves_inventory_unprocessed` | `PARTIAL_INVENTORY` |
| G09 | revue d’un contenu hostile | `_project_document` + `test_g09_hostile_content_isolated_for_human_review` | `QUARANTINED_REVIEW_REQUIRED` |

## Vérification

Les références sont chargées par le parseur fermé de `BusinessFixture`. La suite fixture complète passe contre PostgreSQL Docker : **10 tests réussis**. Les tests non base passent séparément : **9 réussis**. Les actes complémentaires rejoués isolément passent également :

- résolution humaine G03 : **2 tests PostgreSQL réussis** ;
- brouillon dérivé G05 : **1 test PostgreSQL réussi** ;
- contrôle P5 G02 : **1 test PostgreSQL réussi** ;
- inconnu d’échéance G06 : **1 test réussi**.

Une exécution parallèle de plusieurs modules a provoqué un deadlock de teardown Alembic ; la preuve G03 a été rejouée isolément et passe. Ce verrou d’environnement ne change aucun résultat métier et n’a pas été contourné par une modification du code.

## Limites conservées

- G01 et G02 restent soumis aux décisions humaines et à la version exacte du paquet ; un refus ne vaut pas autorisation.
- G03 conserve les deux contributions et la raison de résolution ; une résolution n’efface aucune source.
- G04 et G06 rendent le besoin de revue visible ; aucun coût, date ou hypothèse n’est inventé.
- G05 conserve le document source, le hash et la version du brouillon ; le brouillon n’est pas une réponse validée.
- G07–G09 restent des états de revue et de quarantaine, sans exécution, transmission IA ou succès implicite.

## Références

- `backend/app/platform/quality/data/g01_g09_business.json`
- `backend/app/platform/quality/business_fixtures.py`
- `backend/tests/application/test_g01_g09_business_fixtures.py`
- `backend/tests/security/test_dce_contribution_conflicts.py`
- `backend/tests/application/test_preparation_review.py`
- `backend/tests/application/test_submission_package.py`
- `backend/tests/application/test_boamp_qualification.py`
- `docs/03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE9_G01_G09_EXECUTION_PREUVE_v0.1.md`
