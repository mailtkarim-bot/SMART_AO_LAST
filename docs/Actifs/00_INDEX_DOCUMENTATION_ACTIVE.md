# SMART AO — Index des documents actifs

**Autorités actuelles : v3.1 — 1er octobre 2026.**

## Cahiers des charges — documents à lire en premier

Les trois cahiers complets sont réunis dans [`01_Cahiers_des_charges/`](01_Cahiers_des_charges/) :

- [Product Freeze métier v3.1](01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md) — autorité produit/métier : promesse, périmètre, personnalisation et invariants.
- [Cahier directeur métier v3.1](01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md) — besoins, objets, parcours, règles, scénarios et exigences différées.
- [Cahier technique d’exécution v3.1](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md) — architecture d’insertion, contrats, données, API, sécurité, migrations et preuves attendues.

En cas de contradiction produit/métier, le Product Freeze prévaut. Les cahiers décrivent la cible ; leur présence ne prouve pas que chaque capacité est codée.

## Autres documents actifs

- [Produit et UX](02_Produit_et_UX/) — catalogue des écrans/parcours, fondations UX et contrats d’expérience.
- [Architecture et implémentation](03_Architecture_et_implementation/) — architecture directrice, Phase 0/Gate 0 et preuves techniques.
- [Parcours et preuves](04_Parcours_et_preuves/) — dossiers EXP-01 à EXP-07 et tranche C08/C09.
- [Qualifications locales](05_Qualification_locale/) — résultats datés de recette, accessibilité et qualification ; ils ne valent pas GO public.
- [Pilotage et audits](00_Pilotage_et_audits/) — plan opérationnel, décisions V3.1, couverture et snapshot du checkout.
- [Matrice E1 KEEP/ADAPT/MOVE/ABSENT](00_Pilotage_et_audits/V3_1/E1_MATRICE_EXIGENCES_RESTANTES_2026-10-03.md) — gaps V3.1 cartographiés ; C2/C3/C4 livrés dans le WIP local.
- [Qualification Q1 intégrée A1→B1→C1 du 2 octobre](00_Pilotage_et_audits/V3_1/Q1_CHAINE_A1_B1_C1_INTEGREE_2026-10-02.md) — recette même-Affaire et gates locales ; NO-GO public maintenu.
- [Preuve C1→C2 des engagements A1](04_Parcours_et_preuves/C1_C2_LIAISON_A1_SOURCES_AUDIT_PREUVE_v0.1.md) — lecture Patron du snapshot B1 et liaison append-only `LINKED`/`UNKNOWN` ; WIP local non poussé.
- [Preuve C1→C3 des impacts d’événement](04_Parcours_et_preuves/C1_C3_IMPACT_HUMAIN_SOURCE_A1_AUDIT_CADRAGE_v0.1.md) — acte Patron source/axe append-only, `UNKNOWN` explicite, tests HTTP/PostgreSQL et C07/C12 ; WIP local non poussé.
- [Preuve C1→C4 action/impact](04_Parcours_et_preuves/C1_C4_ACTION_IMPACT_LIAISON_AUDIT_CADRAGE_v0.1.md) — acte C4 append-only distinct, états `LINKED`/`UNKNOWN`/`NOT_APPLICABLE`, C1 Action demeure `RECORDED` ; E2E local et gates complets consignés.
- [Cadrage C1→C5 preuve d’exécution](04_Parcours_et_preuves/C1_C5_PREUVE_EXECUTION_ACTION_AUDIT_CADRAGE_v0.1.md) — distingue intention, réalisation déclarée, pièce effectivement retrouvée et confirmation externe ; `UNKNOWN` demeure sans preuve source-vérifiée ; audit/cadrage seulement, C5 non implémenté.
- [Diagnostic Q1 du 1er octobre](00_Pilotage_et_audits/V3_1/Q1_QUALIFICATION_FIXTURES_LOCALES_2026-10-01.md) — constat partiel historique, complété par la qualification intégrée ci-dessus.
- [Contre-audit Smart BTP et roadmap R0](00_Pilotage_et_audits/Veille_concurrentielle_2026-10-01/SMART_AO_READ_ME_FIRST.md) — pièces de recherche reçues, propositions de pilotage, pas de nouvelle autorité produit.
- [Dépendances et exploitation](06_Dependances_et_exploitation/) — runbook et inventaires opérationnels.

## Autorité et limites

Le [plan global](00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) porte l’unique tranche active. Le code et les tests réellement exécutés décrivent l’état livré ; les cahiers fixent l’état cible ; les audits et preuves sont datés. Les documents remplacés, candidats et historiques sont dans [`../Archive/`](../Archive/).

**NO-GO public maintenu.** Aucun document d’audit ou de qualification locale n’autorise à lui seul un déploiement public.
