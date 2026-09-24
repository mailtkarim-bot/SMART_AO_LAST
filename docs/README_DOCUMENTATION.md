# Documentation SMART AO

Ce répertoire distingue les autorités produit, l’implémentation vérifiée, les contrats techniques candidats et les preuves de qualification.

## Autorités actives

- [`00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md`](00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md) — seule autorité produit/métier actuelle.
- [`00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md`](00_REFERENCE_ACTIVE/SMART_AO_Catalogue_Ecrans_Parcours_Produit_OWNER_CONSOLIDATED_v0.3.md) — surfaces et parcours UX.
- [`00_REFERENCE_ACTIVE/SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md`](00_REFERENCE_ACTIVE/SMART_AO_Prototype_UX_V0_Fondations_OWNER_CONSOLIDATED_v0.3.md) — règles UX communes.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) — feuille de route opérationnelle.

## État technique vérifié

- [`01_IMPLEMENTATION_ACTIVE/`](01_IMPLEMENTATION_ACTIVE/) — architecture v3.1, Phase 0/Gate 0, migrations et preuves d’implémentation.
- [`02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md`](02_FUTURE_TECHNICAL/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v2.1.md) — architecture d’exécution candidate FastAPI/React/PostgreSQL.
- [`03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md`](03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md) — traçabilité PF2/code et blockers T0.
- [`02_FUTURE_TECHNICAL/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md`](02_FUTURE_TECHNICAL/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md) — runbook VPS, encore non exécuté faute de fournisseur.
- [`00_REFERENCE_ACTIVE/DEPENDENCIES_WORKING/`](00_REFERENCE_ACTIVE/DEPENDENCIES_WORKING/) — inventaire des dépendances, proposition non gelée.

## Qualification actuelle

- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_QUALIFICATION_VERDICT_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_QUALIFICATION_VERDICT_v0.1.md) — qualification locale, sans déclaration de production publique.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_GO_NO_GO_LOCAL_PACKET_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_GO_NO_GO_LOCAL_PACKET_v0.1.md) — dossier GO conditionnel local / NO-GO public.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_LOCAL_RAG_VERDICT_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_LOCAL_RAG_VERDICT_v0.1.md) — RAG temporaire, indexation persistante désactivée.
- [`03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_DCE_CORPUS_OWNER_REVIEW_PACKET_v0.1.md`](03_PRODUCT_DESIGN_WORKING/SMART_AO_PHASE11_DCE_CORPUS_OWNER_REVIEW_PACKET_v0.1.md) — revue propriétaire du corpus redacted.

## Réouverture produit v2 en examen

- [`03_PRODUCT_DESIGN_WORKING/realignment_v2/SMART_AO_PACKAGE_CODEX_REALIGNEMENT_V2_README_2026-09-24.md`](03_PRODUCT_DESIGN_WORKING/realignment_v2/SMART_AO_PACKAGE_CODEX_REALIGNEMENT_V2_README_2026-09-24.md) — ordre de lecture et mandat actif.
- [`03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md`](03_PRODUCT_DESIGN_WORKING/realignment_v2_audit/MASTER_V2_TRACEABILITY_MATRIX.md) — confrontation initiale v2 au code et blockers T0.

Le Product Freeze v2.0 ci-dessus est désormais l'autorité produit/métier active. Le v1.0 est archivé.

## Organisation

- `03_PRODUCT_DESIGN_WORKING/` contient les contrats, preuves, freezes et qualifications utiles au pilotage.
- `04_DESIGN_ASSETS/` contient les assets visuels de travail.
- `_ARCHIVE/` contient les propositions, anciennes architectures, revues et cahiers remplacés. Un document archivé n’a aucune autorité active.
- `rapports/` reste historique et ne reçoit plus de livrables actifs.

En cas de contradiction, l’ordre de priorité est : code/tests exécutés, Product Freeze v1.0, contrats approuvés, checklist globale, puis Basic Memory.
