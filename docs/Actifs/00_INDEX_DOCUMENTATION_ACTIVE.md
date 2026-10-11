# SMART AO — Index des documents actifs

**Autorités actuelles : v3.1 — 1er octobre 2026.**

## Cahiers des charges — documents à lire en premier

Les trois cahiers complets sont réunis dans [`01_Cahiers_des_charges/`](01_Cahiers_des_charges/) :

- [Product Freeze métier v3.1](01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md) — autorité produit/métier : promesse, périmètre, personnalisation et invariants.
- [Cahier directeur métier v3.1](01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md) — besoins, objets, parcours, règles, scénarios et exigences différées.
- [Cahier technique d’exécution v3.1](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md) — architecture d’insertion, contrats, données, API, sécurité, migrations et preuves attendues.

**Direction visuelle obligatoire Owner (09/10) :** [PF31-11 — design Cytd adapté à SMART_AO](01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md#pf31-11), avec captures dark/light, typographies et palettes imposées. À appliquer aux sessions UI ultérieures après fermeture technique.

En cas de contradiction produit/métier, le Product Freeze prévaut. Les cahiers décrivent la cible ; leur présence ne prouve pas que chaque capacité est codée.

## Autres documents actifs

- [Produit et UX](02_Produit_et_UX/) — catalogue des écrans/parcours, fondations UX et contrats d’expérience.
- [Architecture et implémentation](03_Architecture_et_implementation/) — architecture directrice, Phase 0/Gate 0 et preuves techniques.
- [Parcours et preuves](04_Parcours_et_preuves/) — dossiers EXP-01 à EXP-07 et tranche C08/C09.
- [Qualifications locales](05_Qualification_locale/) — résultats datés de recette, accessibilité et qualification ; ils ne valent pas GO public.
- [C08 — commande humaine de rapprochement de lignes (08/10)](05_Qualification_locale/C08_RAPPROCHEMENT_LIGNES_UI_2026-10-08.md) — intégration locale du POST existant dans la Revue Patron; reçus/revue exacts, UNKNOWN, retry stable, 409 et relecture GET couverts par tests. Pas de recette navigateur réelle ni de backend live; NO-GO public maintenu.
- [C10/P5 — audit du snapshot transmis exact (09/10)](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md#ct31-37) — premier écart : origine C10 absente du candidat Submission; audit117backend/19Web locaux, contrat/proofs à qualifier avant code. P5,export et dépôt intégrés C10 non qualifiés; droits et NO-GO inchangés. Prochaine étape dans le plan seul.
- [C10/P5 — origine exacte, autorisation et export (10/10)](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md#ct31-40) — P5 Patron lie le SHA-256 exact du candidat schema 3; l’export revalide l’origine et les octets, ZIP synthétique contient seulement manifeste + document haché. UI exige le manifeste et préserve le retry exact. La recette navigateur Patron synthétique CT31-42 couvre UNKNOWN/retry, 409/GET courant, P5 et ZIP vérifié; clôture locale approuvée par l’Owner le 11/10, sans qualification backend/live/origine C10 réelle. La barrière DB de rollback est qualifiée en CT31-41, sans qualification d’exploitation générale de l’ancien runtime; NO-GO public maintenu.
- [C10/P5 — qualification navigateur Patron locale (10/10, clôture Owner 11/10)](05_Qualification_locale/EXP-05_C10_P5_QUALIFICATION_NAVIGATEUR_PATRON_2026-10-10.md) — Chromium isolé, session et API synthétiques; manifeste/SHA courant, MFA, confirmation P5, UNKNOWN/retry exact, 409 puis GET du manifeste courant et export ZIP exact vérifié. L’Owner a validé la clôture du parcours local synthétique. Aucun backend métier live, corpus réel, origine C10 réelle, dépôt externe ou GO public.
- [Revue Git et corrections C10/P5 avant push (11/10)](00_Pilotage_et_audits/REVUE_GIT_C10_P5_AVANT_PUSH_2026-10-11.md) — CT31-43 ferme les courses des vrais writers DCE/confirmation et les réponses UI tardives; suites, scans et limites du snapshot publiable consignés. Remote réel SMART_AO_LAST, branche de travail, aucun merge main/déploiement/GO produit public.
- [C10/P5 — barrière de rollback `d1f6db8` (10/10)](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md#ct31-41) — migration `20261010_0136` bloque sur PostgreSQL tmpfs les écritures legacy de candidat lié à C10, P5 et export, et refuse le downgrade en présence d’un plan ou candidat schema 3. Backend complet 2211/2211; Semgrep 1.179.0 `p/security-audit`, 225 règles/12 fichiers/0 finding. Miroir Basic Memory synchronisé et relu après réparation du lancement CLI/MCP local; le plan global reste source unique. Aucun ancien binaire en exploitation, aucun déploiement; NO-GO public maintenu.
- [C10 — plan, contenu, revue et transmission interne (09/10)](01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md#ct31-36) — chaîne locale synthétique jusqu’au snapshot des versions revues et au GET Patron des manifestes/reçus durables. Tête locale `20261009_0135`; historique CT31-33 à CT31-36 conservé. Le statut et la prochaine étape viennent uniquement du [plan global](00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md). Aucun backend/auth live, corpus réel, P5, dépôt externe ou GO public qualifié; NO-GO maintenu.
- [EXP-05 — qualification navigateur du formulaire Collaborateur (08/10)](05_Qualification_locale/EXP-05_QUALIFICATION_NAVIGATEUR_FORMULAIRE_2026-10-08.md) — tranche relue et clôturée par l’Owner le 08/10, sur navigateur headless isolé et API synthétique; UNKNOWN→retry identique→reçu/GET seul et 409→GET seul. Aucun backend live; le NO-GO public demeure.
- [Pilotage et audits](00_Pilotage_et_audits/) — le [plan global](00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) est le seul statut opérationnel et porte la prochaine étape exacte. Ses campagnes sont datées et rattachées au checkout testé; une ancienne recette n’est pas extrapolée au WIP. Gate A1 (corpus Golden DCE) en attente, A2 générique HOLD, Basic Memory miroir synchronisé par CLI local (MCP non exposé dans cette session), NO-GO public.
- [Matrice E1 KEEP/ADAPT/MOVE/ABSENT](00_Pilotage_et_audits/V3_1/E1_MATRICE_EXIGENCES_RESTANTES_2026-10-03.md) — gaps V3.1 cartographiés ; C2/C3/C4/C5 livrés localement dans le WIP.
- [Qualification Q1 intégrée A1→B1→C1 du 2 octobre](00_Pilotage_et_audits/V3_1/Q1_CHAINE_A1_B1_C1_INTEGREE_2026-10-02.md) — recette même-Affaire et gates locales ; NO-GO public maintenu.
- [Preuve C1→C2 des engagements A1](04_Parcours_et_preuves/C1_C2_LIAISON_A1_SOURCES_AUDIT_PREUVE_v0.1.md) — lecture Patron du snapshot B1 et liaison append-only `LINKED`/`UNKNOWN` ; WIP local non poussé.
- [Preuve C1→C3 des impacts d’événement](04_Parcours_et_preuves/C1_C3_IMPACT_HUMAIN_SOURCE_A1_AUDIT_CADRAGE_v0.1.md) — acte Patron source/axe append-only, `UNKNOWN` explicite, tests HTTP/PostgreSQL et C07/C12 ; WIP local non poussé.
- [Preuve C1→C4 action/impact](04_Parcours_et_preuves/C1_C4_ACTION_IMPACT_LIAISON_AUDIT_CADRAGE_v0.1.md) — acte C4 append-only distinct, états `LINKED`/`UNKNOWN`/`NOT_APPLICABLE`, C1 Action demeure `RECORDED` ; E2E local et gates complets consignés.
- [C1→C5 preuve d’exécution](04_Parcours_et_preuves/C1_C5_PREUVE_EXECUTION_ACTION_AUDIT_CADRAGE_v0.1.md) — capture, source immuable et confirmation distincte prouvées localement par HTTP/PostgreSQL; `RETRIEVED` exige relecture SHA-256, locator seul reste `REFERENCED`, absence reste `UNKNOWN`. Arrêt brutal, retry outbox, backup/restore **2** objets `CLEAN`, concurrence backup/restore, reçus invalides et reprise après échecs de suppression `docker volume rm`/`dropdb` prouvés. Les gates locales complètes C5/WIP sont passées; chiffrement et préproduction réelle restent ouverts. EXP-02 sépare `LIVE`/`REPLAY` (`20261005_0131`) et conserve contrat/hash transport (`20261005_0132`) sur chaque lien d’ingestion sans stocker le payload; `REPLAY` n’alimente pas `last_success_at`. NO-GO public maintenu.
- [Diagnostic Q1 du 1er octobre](00_Pilotage_et_audits/V3_1/Q1_QUALIFICATION_FIXTURES_LOCALES_2026-10-01.md) — constat partiel historique, complété par la qualification intégrée ci-dessus.
- [Contre-audit Smart BTP et roadmap R0](00_Pilotage_et_audits/Veille_concurrentielle_2026-10-01/SMART_AO_READ_ME_FIRST.md) — pièces de recherche reçues, propositions de pilotage, pas de nouvelle autorité produit.
- [Dépendances et exploitation](06_Dependances_et_exploitation/) — runbook et inventaires opérationnels.

## Autorité et limites

Le [plan global](00_Pilotage_et_audits/SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md) porte l’unique tranche active. Le code et les tests réellement exécutés décrivent l’état livré ; les cahiers fixent l’état cible ; les audits et preuves sont datés. Les documents remplacés, candidats et historiques sont dans [`../Archive/`](../Archive/).

**NO-GO public maintenu.** Aucun document d’audit ou de qualification locale n’autorise à lui seul un déploiement public.
