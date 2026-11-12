# Livrables métier et preuves — pilotage du 19 octobre 2026

**Consolidation datée du 02/11/2026 :** le [bilan L01–L11/T01–T03](BILAN_LOCAL_L01_L11_T01_T03_2026-11-02.md) rassemble les preuves plus récentes, leurs limites et le contrat de sortie du cash minimum L07. Les constats et journaux antérieurs ci-dessous gardent leur date ; le plan global demeure l’unique statut et prochaine étape.

## Révision Owner22–23/10 — codage fonctionnel

La [révision fonctionnelle](REALIGNEMENT_FONCTIONNEL_2026-10-22.md) confronte la carte existante aux manques concrets du code et réoriente le plan vers L06→L07→L05→L08 puis aval. Les parcours locaux prouvés sont conservés sans être confondus avec une couverture automatique exhaustive. Douze références périmées application/analysis_dossier_* ont été corrigées vers infrastructure dans le CSV. Aucun nouveau catalogue parallèle et aucune exigence différée supprimée.

## Décision et limites

À la demande Owner, le programme revient aux livrables métier complets du Freeze v3.1. Les cycles d’intention RC isolés sont reportés au sous-chantier de L04 ; aucun nouveau benchmark d’intention ne devient la prochaine tranche principale. Ce document regroupe le suivi existant, sans réécrire les cahiers ni réduire les exigences différées. Le **plan global reste l’unique statut opérationnel**.

Autorités : [Freeze produit/métier v3.1](../01_Cahiers_des_charges/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md), [Master métier v3.1](../01_Cahiers_des_charges/SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md), [cahier technique v3.1](../01_Cahiers_des_charges/SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md). Réutilise la [revue globale du14/10](REVUE_GLOBALE_METIER_CODE_CONCEPTION_2026-10-14.md), son registre917chapitres et sa matrice45familles ; elle ne constitue pas une nouvelle relecture intégrale ni917 verdicts individuels.

Checkout principal/HEAD30f2693/WIP inclus. Les 45 familles sont rattachées exactement une fois à11livrables et3garanties transversales. Le CSV compagnon conserve les références historiques, chemins de code/tests et leurs limites. Les chemins sont vérifiés présents aujourd’hui ; leur présence n’est pas une preuve de comportement. Aucun pourcentage global d’achèvement n’est calculé.

**Lecture des états :** tous les livrables restent PARTIELS ou NON REQUALIFIÉS ENSEMBLE. Certains sous-parcours ont une preuve locale ; cela ne clôture pas toute la ligne. « Surface présente » signifie lecture statique du composant, pas recette navigateur fraîche. Une preuve ancienne reste datée. Les reports PF31-09 restent visibles et n’empêchent pas le socle manuel sourcé.

<a id="pilotage-fonctionnel"></a>
## Pilotage par livrables fonctionnels — décision Owner du 20 octobre 2026

**Décision :** regrouper le travail en livrables fonctionnels cohérents et coder leurs manques jusqu’à une frontière utilisable. Les11livrables et3garanties existants restent la carte du produit; aucun nouveau catalogue parallèle. Le plan global reste l’unique statut et la seule prochaine étape. La présente fiche décrit le résultat et ses critères, pas un second backlog actif.

### Règle de travail et de clôture

- Une unité de travail correspond à une tâche utilisateur complète avec entrée, résultat visible, règles métier et refus. Un axe, un champ, un adaptateur ou un reçu est une sous-tâche interne; il ne devient pas automatiquement le prochain livrable ni une clôture métier.
- Pour cette unité, vérifier les exigences du cahier, le code réellement existant et les tests; identifier les manques puis enchaîner tests rouges, code Python/API/persistance, interface et recette jusqu’au résultat utile. Ne pas intercaler un nouveau dossier de preuve à chaque petit raccordement.
- Réutiliser les registres/parcours actuels; aucune réécriture générale, nouvelle dépendance ou activation de candidat sans nécessité et preuve. Les calculs relevant de L06/L07 restent dans ces contextes; leur affichage en L04 ne les remplace pas.
- Un résultat UNKNOWN reste honnête mais n’est pas une fonctionnalité livrée. L’inconnu doit être explicable; si un point critique doit être résolu ou arbitré, rendre sa source, son responsable, son action et la preuve attendue accessibles. Un calcul, une saisie ou un contrôle demandé mais absent reste un manque, même si l’écran affiche UNKNOWN.
- Le rapport d’avancement montre : résultat utilisateur obtenu, fichiers Python/API/UI changés, manques fermés et restant ouverts, recette métier et limites. Les nombres de tests soutiennent cette preuve; ils ne mesurent pas l’achèvement du produit.
- Une preuve locale de composant peut rester cochée dans l’historique. Un livrable n’est clos que si ses critères sont démontrés sur le parcours complet; ne pas promouvoir L04 par accumulation de coches techniques. Arrêt avant cette frontière seulement pour un blocage réel, une décision Owner nécessaire ou une interruption explicite; laisser le livrable actif et un point de reprise exact.

### Frontières utilisables des livrables existants

| Livrable | Frontière utilisateur à atteindre et prouver |
|---|---|
| L01 | Opportunité qualifiée → Affaire/lot exacts ouverts sans doublon, motifs et inconnus consultables |
| L02 | Pièces/profil entreprise préparés → version publiée et adoptée dans une Affaire avec preuves et invalidations |
| L03 | Version DCE reçue → inventaire/extraction/consultation par lot/version, exclusions et pièces non lues ou manquantes visibles |
| L04 | Version DCE applicable → dossier d’analyse préparé et revu sur12axes, points critiques sourcés et traitement exploitable; frontière détaillée ci-dessous |
| L05 | Dossier analysé → carte d’engagement et décision humaine motivée, conditions/responsables/preuves exacts, aucune porte levée implicitement |
| L06 | Données de prix/devis → chiffrage traçable, couverture des postes et hypothèses lisibles, inconnus et validité visibles |
| L07 | Demandes/ressources/flux datés → appréciation capacité/trésorerie prudente et scénarios; un statut solveur ou un solde isolé ne suffit pas |
| L08 | Exigences de réponse → pièces substantielles revues et ZIP exact autorisé; couverture/format/preuves vérifiables, dépôt humain distinct |
| L09 | Offre gagnée → dossier conducteur des engagements/écarts/conditions et sources exactes, relecture dans le parcours destinataire |
| L10 | Changement sourcé → conséquence, engagement, action puis preuve d’exécution suivis dans la même Affaire, historique conservé |
| L11 | Réception/paiement/sortie → obligations et preuves traitées, actions et enseignements consultables; les reports juridiques PF31-09 restent explicites |
| T01/T02/T03 | Permissions/confidentialité/intégrité et usage vérifiés dans chaque parcours concerné, pas une campagne horizontale remplaçant le livrable |

Ce tableau est un critère de travail, pas une déclaration de disponibilité. Les détails et reports des CDC v3.1 demeurent applicables; les critères particuliers existants sous chaque fiche ne sont pas réduits.

### L04 — contrat de sortie du parcours d’analyse

**Utilisateur et entrée :** Patron autorisé, Affaire et lot/version DCE applicables; préparation dans les permissions existantes. Le périmètre de qualification reste local et synthétique, sans corpus réel ni backend live.

**Résultat utile :** dans le parcours Affaire → DCE → synthèse existant, le Patron prépare et relit un dossier de12axes. Pour chaque point critique couvert : fait/extrait et source/version/locator exacts, applicabilité et certitude, conséquences qualifiées ou inconnues, action, responsable, échéance, preuve attendue et risque résiduel. Les données économiques demeurent Patron/FINANCIAL_PRIVATE. Les informations non automatisées passent par les actes humains autorisés et tracés; leur absence n’est pas cachée par une mention générique « à revoir ».

**Critères de fin cumulatifs :**

1. Inventaire du DCE et12axes accessibles depuis une même Affaire; pièces non lues/exclues/manquantes visibles et refus de complétude. Aucun point annoncé dans le scénario d’acceptation omis silencieusement.
2. Sur les points critiques du scénario : le Patron retrouve la source exacte et peut effectuer puis relire les traitements autorisés sans SQL ni logs. Les relations absentes sont identifiées; les fonctions de saisie/relecture nécessaires sont codées, pas remplacées par des UNKNOWN décoratifs.
3. Exigences, risques, actions/responsables, preuves attendues et risque résiduel forment un fil cohérent; conséquences techniques, prix, délai, trésorerie et contractuelles ne sont ni inventées ni confondues. Chaque champ non prouvé a une raison visible et un traitement lorsque nécessaire.
4. Un rectificatif ou une extraction incomplète invalide la relecture concernée; les anciennes preuves ne sont pas transférées et l’historique reste consultable dans ses droits.
5. Un scénario d’acceptation local synthétique couvrant lot/version, pièce non lue, exigences/risques critiques, traitement humain et données économiques relie les preuves HTTP/PostgreSQL et navigateur sur des identifiants/sources cohérents. Nominal, permissions/tenant/rôle, retry/concurrence et source obsolète sont prouvés aux frontières concernées; une simple fixture UI indépendante ne suffit pas à qualifier toute la chaîne.
6. Le bilan distingue parcours utilisable, automatismes réellement qualifiés, manques et reports. L04 n’est pas déclaré « analyse exhaustive automatique ». Aucune porte/P3/admission n’est modifiée pour réussir la recette.

**État historique au changement de méthode (20/10) : PARTIAL.** Assemblage12axes, relations, anatomie, actes humains révisionnés et lectures Prix/CASH sont des acquis locaux. Les axes sans faits/revue, la couverture des points critiques, les conséquences complètes et la recette de ce parcours complet ne sont pas démontrés. La courbe de trésorerie et les calculs approfondis restent des manques de leurs livrables L06/L07, pas des fonctions devenues complètes parce que L04 affiche leurs états.

**Ordre interne de réalisation, sans nouvelles tranches de statut :** écrire le scénario d’acceptation et la première preuve rouge à partir du parcours existant; compléter les fonctions manquantes et les branchements nécessaires ensemble; qualifier la chaîne et ses refus; mettre à jour le bilan une fois la frontière atteinte. Le raccordement Capacité déjà envisagé est une sous-tâche de ce bloc si nécessaire, pas une fin en soi. Ne pas consacrer la prochaine session à une nouvelle revue documentaire seule.

**Gates conservées :** DPGF non évaluable par RAG; candidats inactifs; UNKNOWN/REVIEW_REQUIRED; A1 non admis, A2 générique HOLD et NO-GO public; aucun live/corpus réel/VPS/déploiement/P3/dépôt externe/push.

## Tableau de pilotage

| ID | Livrable / garantie | Familles existantes | Preuve fraîche de cette revue |
|---|---|---|---|
| [L01](#l01) | Choisir une opportunité et ouvrir une Affaire | F04 | Présence contrôlée ; recette complète non rejouée |
| [L02](#l02) | Préparer le dossier entreprise et son profil métier | F03, F37 | Présence contrôlée ; recette complète non rejouée |
| [L03](#l03) | Dossier documentaire DCE par lot et version | F05, F06, F07 | Inventaire/extraction/lecture partiellement qualifiés; synthèse12axes suivie en L04; parcours complet PARTIAL |
| [L04](#l04) | Dossier d’analyse métier sourcé sur les douze axes | F08, F09, F10, F12, F28, F29 | Acquis locaux assemblage/relations/anatomie/actes/Prix/CASH; parcours humain préparation/revue qualifié21/10; alimentation DCE complète non prouvée, PARTIAL |
| [L05](#l05) | Carte d’engagement et décision Patron motivée | F11, F20, F26, F38 | Parcours local qualifié24/10 ; périmètre général PARTIAL |
| [L06](#l06) | Chiffrage traçable et couverture des offres partenaires | F18, F19, F23, F24, F25 | Présence contrôlée ; recette complète non rejouée |
| [L07](#l07) | Capacité et trésorerie prudentes par Affaire | F21, F22 | Présence contrôlée ; recette complète non rejouée |
| [L08](#l08) | Réponse acheteur et paquet exact autorisé | F27, F30 | Rédaction/revue natives qualifiées localement ; périmètre général PARTIAL |
| [L09](#l09) | Offre gagnée, écarts et dossier conducteur | F13, F31 | Parcours humain qualifié localement; général PARTIAL |
| [L10](#l10) | Changements en exécution et actions prouvées | F17 | Parcours humain qualifié localement; général PARTIAL |
| [L11](#l11) | Réception, paiement, sortie et retour d’expérience | F14, F15, F16, F32, F33, F34, F36 | Présence contrôlée ; recette complète non rejouée |
| [T01](#t01) | Accès, rôles et confidentialité de tous les livrables | F01, F02, F42 | Présence contrôlée ; recette complète non rejouée |
| [T02](#t02) | Intégrité, qualification et exploitation maîtrisée | F35, F40, F41, F43, F44, F45 | Présence contrôlée ; recette complète non rejouée |
| [T03](#t03) | Parcours utilisables et lisibilité transversale | F39 | Présence contrôlée ; recette complète non rejouée |

<a id="l01"></a>
## L01 — Choisir une opportunité et ouvrir une Affaire

- **Exigence :** PF31-03; M31-01; M31-03. Acteur : Patron. Technique : CT31-02/06.
- **Résultat utilisateur attendu :** Une opportunité expliquée, qualifiée humainement, reliée à une Affaire et à ses lots.
- **Code existant :** [backend/app/modules/opportunity/__init__.py](../../../backend/app/modules/opportunity/__init__.py); [backend/app/modules/opportunity/application/__init__.py](../../../backend/app/modules/opportunity/application/__init__.py).
- **Résultat visible / surface existante :** [web/src/features/opportunities/BoampOpportunityPanel.tsx](../../../web/src/features/opportunities/BoampOpportunityPanel.tsx) ; [web/src/features/cases/CreateCasePanel.tsx](../../../web/src/features/cases/CreateCasePanel.tsx). Veille/scoring/qualification et création d’Affaire existent ; présence des composants vérifiée, parcours utilisateur non rejoué ici.
- **Manques précis / qualification restante :** La frontière synthétique source → qualification → ouverture est qualifiée localement ; la collecte live, les autres sources/références génériques, le redémarrage et les séparations ultérieures de lots gardent leurs limites. Aucun score de probabilité commerciale inventé.
- **Preuves disponibles :** [backend/tests/application/test_boamp_ingestion.py](../../../backend/tests/application/test_boamp_ingestion.py); [backend/tests/application/test_boamp_qualification.py](../../../backend/tests/application/test_boamp_qualification.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Complément local du 03/11 :** [source mémoire → P0 → Affaire natifs](../05_Qualification_locale/L01_OPPORTUNITE_AFFAIRE_2026-11-03.md), avec refus/reprise, motifs et inconnus avant ouverture, déduplication et navigation ; preuve bornée sans collecte live.
- **Critère de fonctionnement à démontrer :** Une même opportunité rejouée ne crée pas une seconde Affaire ; l’utilisateur peut expliquer chaque critère et chaque UNKNOWN.

<a id="l02"></a>
## L02 — Préparer le dossier entreprise et son profil métier

- **Exigence :** PF31-05; M31-06. Acteur : Patron et préparateur autorisé. Technique : CT31-05.
- **Résultat utilisateur attendu :** Bibliothèque de preuves/capacités et profil publié, versionné puis adopté explicitement par une Affaire.
- **Code existant :** [backend/app/modules/enterprise/infrastructure/models/enterprise.py](../../../backend/app/modules/enterprise/infrastructure/models/enterprise.py); [backend/app/modules/enterprise/application/enterprise_capability.py](../../../backend/app/modules/enterprise/application/enterprise_capability.py).
- **Résultat visible / surface existante :** [web/src/features/enterprise/EnterpriseLibraryPanel.tsx](../../../web/src/features/enterprise/EnterpriseLibraryPanel.tsx) ; [web/src/features/enterprise/BusinessMethodProfilePanel.tsx](../../../web/src/features/enterprise/BusinessMethodProfilePanel.tsx). Éditeur/bibliothèque et versions/adoption présents ; preuves locales antérieures dans le plan, pas de nouvelle recette complète.
- **Manques précis / qualification restante :** Prouver adéquation/validité des pièces pour chaque exigence et delta d’adoption sur Affaire existante ; une attestation ne prouve pas une couverture réelle.
- **Preuves disponibles :** [backend/tests/api/test_enterprise_capability_api.py](../../../backend/tests/api/test_enterprise_capability_api.py); [backend/tests/application/test_enterprise_capability_foundation.py](../../../backend/tests/application/test_enterprise_capability_foundation.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Aucune recette complète de cette ligne ; ne pas annoncer PASS.
- **Critère de fonctionnement à démontrer :** Même Affaire sous deux versions : décisions passées inchangées, adoption tracée, pièce expirée/inapplicable signalée.

<a id="l03"></a>
## L03 — Dossier documentaire DCE par lot et version

- **Exigence :** PF31-03; M31-03 étape 1; M2-029. Acteur : Préparateur et Patron selon droits. Technique : CT31-02/04.
- **Résultat utilisateur attendu :** Inventaire de la version applicable : reçus, exclus, annoncés manquants, extraits/non extraits, sources consultables.
- **Code existant :** [backend/app/modules/case/infrastructure/models/case.py](../../../backend/app/modules/case/infrastructure/models/case.py); [backend/app/modules/dce/infrastructure/models/dce_version.py](../../../backend/app/modules/dce/infrastructure/models/dce_version.py).
- **Résultat visible / surface existante :** [web/src/features/dce/DceOpeningPanel.tsx](../../../web/src/features/dce/DceOpeningPanel.tsx) ; [web/src/features/dce/DceKnowledgePanel.tsx](../../../web/src/features/dce/DceKnowledgePanel.tsx). Contrats lecture/coverage et panneaux présents ; chaîne backend fraîche dans la campagne86. Le contrat impose analysis_complete=False et inventory_completeness=UNKNOWN.
- **Manques précis / qualification restante :** Qualifier l’inventaire réellement reçu et les portées lot ; ne pas confondre extraction avec analyse complète. Les PDF/raster/tableaux complexes et sources non éligibles conservent leurs limites.
- **Preuves disponibles :** [backend/tests/api/test_case_assigned_api.py](../../../backend/tests/api/test_case_assigned_api.py); [backend/tests/api/test_case_creation_api.py](../../../backend/tests/api/test_case_creation_api.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** 86 tests backend du lecteur DCE, analyse sourcée et matérialisation ; aucun test navigateur ou des12axes complets.
- **Critère de fonctionnement à démontrer :** Après rectificatif ou extraction refusée, aucune ancienne source ne reste présentée comme courante ; toute pièce non lue/manquante demeure visible.

<a id="l04"></a>
## L04 — Dossier d’analyse métier sourcé sur les douze axes

**Actualisation verticale21/10 :** Six types de signaux d’exécution source-only codés (technique, logistique, capacité/planning, HSE, paiement, réception) dans l’analyseur natif v7; contraintes SQL migrées vers0139 avec refus de downgrade peuplé. Les11 faits absents du jeu de développement sont maintenant présents (32/32points historiques et nouveaux), et15/15points du nouveau DCE synthétique gelé sont retrouvés sans point parasite mesuré. Types/axes, source/version/hash/ligne/offsets et portée lot candidate ou UNKNOWN contrôlés; négations/conditions UNSPECIFIED et applicabilité UNKNOWN jusqu’à acte humain. Sur PostgreSQL jetable,15points ont été traités, puis dossier12axes préparé/revu sur SHA exact,17actes uniques vérifiés en navigateur via vraies routes TestClient. Aucun GO métier ni analyse exhaustive déduits. [Preuve source/traitement/revue](../05_Qualification_locale/L04_PRESCRIPTIONS_EXECUTION_2026-10-21.md). Le parcours humain fonctionne localement; l’analyse automatique complète reste non prouvée.


**Alimentation DCE —21/10 :** Chaîne active extraction→analyse→matérialisation→dossier qualifiée sur deux DCE synthétiques de8pièces, lots1/2 et4/8. Correction Python : mapping CCAP/CCTP incomplet du handler (KeyError reproduit), visites de chantier/site omises, faux signaux RC sur pièces classifiées nonRC; version6 avec relecture historique1–5 conservée. Développement21/21et nouveau holdoutv2 22/22signaux attendus restitués avec type/axe/source/version/hash/ligne/offsets,0signal parasite mesuré,11faits métier toujours non interprétés par dossier (32/33faits attendus); L04 PARTIAL, aucune analyse complète déduite. Backend global3697passés/1avertissements/874.99s/exit0;74SQL ciblés et382purs verts. Ruff/format/mypy650/diff verts;Semgrep1.179.0/225règles/9fichiers0finding/0erreur;24SHA publics triés,0secret nouveau nontrié. Revue P2 des assertions corrigée et contre-revue sans autre constat. [Preuve multi-pièces/multi-lots](../05_Qualification_locale/L04_ALIMENTATION_DCE_MULTILOTS_2026-10-21.md). Les onze écarts concernent technique/logistique, capacité, HSE, paiement/réception; ils ne sont pas couverts par le seul parcours humain.


**Actualisation21/10 :** Parcours humain de préparation/revue qualifié localement : traitements source-liés, applicabilité motivée, cinq conséquences déclarées ou UNKNOWN motivé, action/responsable explicite/échéance, preuves attendues et risque résiduel; préparation puis revue des douze axes sur SHA exact, historique protégé après rectificatif. Backend3678 réussites/2avertissements; Web615/4ignorés; navigateur23desktop+23mobile+12historique/invalidation; quatre refus API tenant/financier supplémentaires. PostgreSQL jetable, HTTP réel via TestClient et session synthétique; aucune analyse exhaustive automatique déduite. [Dossier de recette](../05_Qualification_locale/L04_PARCOURS_PREPARATION_REVUE_2026-10-20.md). Les constats20/10 ci-dessous restent historiques; le manque courant est la couverture sur DCE complet multi-pièces/multi-lots.


- **Exigence :** PF31-06; M31-02/03; M2-026/027. Acteur : Patron et préparateur dans leurs permissions. Technique : CT31-02/03/06.
- **Résultat utilisateur attendu :** Pour chaque axe : constats, exigences, risques, applicable/inconnu, sources, conséquences, responsable, action et preuve attendue.
- **Code existant :** `backend/app/modules/case/application/analysis_summary.py`, `backend/app/modules/case/infrastructure/analysis_summary_reader.py`, `analysis_follow_up_reader.py`, contrat public Case et route `case_analysis_summary.py` ; registres DCE/Decision/PatronAction natifs réutilisés.
- **Résultat visible / surface existante :** [web/src/features/dce/DceKnowledgePanel.tsx](../../../web/src/features/dce/DceKnowledgePanel.tsx) ; [web/src/features/decision/DecisionRisksPanel.tsx](../../../web/src/features/decision/DecisionRisksPanel.tsx). Exigences/valeurs candidates, risques et liens ont des registres/panneaux ;Synthèse initiale CaseAnalysisSummaryPanel intégrée, douze axes et preuves visibles côté Patron ; L04 complet reste PARTIEL.
- **Manques précis / qualification restante :** Actes humains preuve attendue/risque résiduel désormais codés et qualifiés localement; ancienne mention « à coder » caduque. Compléter le parcours de préparation/revue et les fonctions nécessaires aux axes sans faits ou traitement; qualifier couverture des points critiques et conséquences selon le contrat de sortie ci-dessus. Compréhension automatique, tableaux/plans, réglementaire et MIRP restent partiels; aucune applicabilité déduite d’un LLM.
- **Preuves disponibles :** [backend/tests/api/test_knowledge_api.py](../../../backend/tests/api/test_knowledge_api.py); [backend/tests/application/test_knowledge_benchmark.py](../../../backend/tests/application/test_knowledge_benchmark.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** 20/10 : 78 ciblés backend, global3628 ; Web20 ciblés/global578 et4 ignorés ;42 contrôles navigateur synthétiques. [Dossier L04](../05_Qualification_locale/L04_SYNTHESE_DOUZE_AXES_2026-10-20.md). Aucune preuve d’analyse complète des12axes.
- **Critère de fonctionnement à démontrer :** Le Patron retrouve les12axes, chaque point critique et sa source exacte ; absence de fait/revue ne devient jamais absence de risque ni analyse terminée.


Raccordement natif qualifié20/10 : actions, conséquences déclarées et conditions/responsables exacts. Backendglobal3641,Web582/4ignorés,50contrôlesnavigateur synthétiques. [Dossier relations](../05_Qualification_locale/L04_RELATIONS_ACTIONS_CONSEQUENCES_2026-10-20.md). Applicabilité et analyse complète non acquises ;L04PARTIEL.


Anatomie lisible20/10 : citation exacte et criticité native codées,preuve attendue/risque résiduel UNKNOWN faute de champ rattaché ;115backend ciblés,586Web,64contrôles navigateur synthétiques. Pas de nouveau globalbackend. [Dossier anatomie](../05_Qualification_locale/L04_ANATOMIE_POINTS_CRITIQUES_2026-10-20.md). L04 reste PARTIEL.

<a id="l05"></a>
## L05 — Carte d’engagement et décision Patron motivée

- **Exigence :** PF31-03/06/07/08; M31-02/03; M2-028. Acteur : Patron habilité. Technique : CT31-02/03/06.
- **Résultat utilisateur attendu :** Un engagement précis, ses impacts/hypothèses et une condition humaine expliquée, avec portes et inconnus visibles.
- **Code existant :** [projection source](../../../backend/app/modules/decision/application/commitment_card.py), [lecture et historique](../../../backend/app/modules/decision/infrastructure/commitment_reader.py), [service/lien natif](../../../backend/app/modules/decision/infrastructure/commitment_service.py), [route](../../../backend/app/interfaces/http/routes/patron_commitment_card.py); registre decision/analyses existant et association append-only0142.
- **Résultat visible / surface existante :** [carte d’engagement native](../../../web/src/features/decision/CommitmentCardPanel.tsx), puis actes détaillés existants : [web/src/features/decision/ContractBaselineImpactsPanel.tsx](../../../web/src/features/decision/ContractBaselineImpactsPanel.tsx) ; [web/src/features/decision/PatronDecisionPanel.tsx](../../../web/src/features/decision/PatronDecisionPanel.tsx). Douze axes, points exacts, hypothèses humaines, impacts/liens/conditions et historique des actes; champs absents UNKNOWN et relations périmées REVIEW_REQUIRED. Aucun score ni décision automatique.
- **Manques précis / qualification restante :** La [reprise native après changement DCE](../05_Qualification_locale/L05_ANALYSE_CARTE_DECISION_2026-11-04.md) crée un nouveau brouillon ; le même DCE reste refusé et aucune décision antérieure n’est transférée. Exhaustivité de l’analyse automatique, quantification économique complète et authenticité des preuves externes non démontrées. La phrase transport séparée du scénario reste non matérialisée et explicitement UNKNOWN.
- **Preuves disponibles :** [backend/tests/db/test_business_method_profile_persistence.py](../../../backend/tests/db/test_business_method_profile_persistence.py); [backend/tests/domain/dce/test_contract_baseline_deviation_impact.py](../../../backend/tests/domain/dce/test_contract_baseline_deviation_impact.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** [Dossier L05](../05_Qualification_locale/L05_CARTE_ENGAGEMENT_2026-10-23.md) :17contrôles Chromium synthétiques,652Web complets+4ignorés et43cœur ciblés recouvrants; globale backend finale en cours dans le plan, aucune clôture anticipée.
- **Critère de fonctionnement à démontrer :** Le fil rouge accès contraint/transport exclu conduit à une condition Patron explicable ; condition non levée reste ouverte sans promotion P3 automatique.


Le [panneau de carte](../../../web/src/features/decision/CommitmentCardPanel.tsx) restitue les douze axes, points/actes/hypothèses/actions/responsables/preuves et inconnus, puis utilise création/gel/finalisation natives et lien exact aux conditions. Source remplacée ou droits retirés entraînent refus/REVIEW_REQUIRED. Les décisions et traitements passés gardent leurs références et valeurs, sans transfert au courant. Les sources de transport non matérialisées restent inconnues; aucune quantification automatique ni exclusion de devis réel déduite. La reprise après changement DCE conserve la décision FINALIZED historique.

<a id="l06"></a>
## L06 — Chiffrage traçable et couverture des offres partenaires

- **Exigence :** PF31-08; M31-03 étapes 3–4; M2-026 axes6/9. Acteur : Patron uniquement pour les données financières. Technique : CT31-02/03/06.
- **Résultat utilisateur attendu :** Prix importés et scénarios, devis exacts, inclusions/exclusions, validité, transport et postes couverts/inconnus.
- **Code existant :** [backend/app/modules/pricing/infrastructure/models/financial.py](../../../backend/app/modules/pricing/infrastructure/models/financial.py); [backend/app/modules/pricing/application/import_commands.py](../../../backend/app/modules/pricing/application/import_commands.py).
- **Résultat visible / surface existante :** [web/src/features/draft/FinancialDraftPanel.tsx](../../../web/src/features/draft/FinancialDraftPanel.tsx) ; [web/src/features/pricing/PartnerOfferLineComparisonsPanel.tsx](../../../web/src/features/pricing/PartnerOfferLineComparisonsPanel.tsx). Import transactionnel/prix/revues de périmètre/comparaisons manuelles et UI présents ; pas de preuve de couverture exhaustive du DCE.
- **Manques précis / qualification restante :** Rattachements sourcés, cellules, devis/exclusions et incomparabilité sont éprouvés dans la [campagne L06 du04/11](../05_Qualification_locale/L06_CHIFFRAGE_RAPPROCHEMENT_2026-11-04.md). La [répartition humaine du05/11](../05_Qualification_locale/L06_REPARTITION_COUT_PARTAGE_2026-11-05.md) permet les montants affectés et le reste, avec budget concurrent et sources révisées ; les rattachements sans montant/incohérents restent UNKNOWN. La [continuité au chiffrage publié](../05_Qualification_locale/L06_REPARTITIONS_CHIFFRAGE_PUBLIE_2026-11-05.md) est qualifiée localement : nouvelles revues sur source exacte, totaux inchangés et anciennes versions historiques, sans transfert automatique. DPGF hors essais RAG ne signifie pas absence du module financier.
- **Preuves disponibles :** [backend/tests/application/test_pricing_import.py](../../../backend/tests/application/test_pricing_import.py); [backend/tests/application/test_pricing_import_commit.py](../../../backend/tests/application/test_pricing_import_commit.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Aucune recette complète de cette ligne ; ne pas annoncer PASS.
- **Critère de fonctionnement à démontrer :** Transport exclu et coût inconnu empêchent toute conclusion de coût couvert ; hypothèses et cellules sources consultables sans fuite Collaborateur.

<a id="l07"></a>
## L07 — Capacité et trésorerie prudentes par Affaire

- **Exigence :** PF31-08/09; M31-02; M2-026 axes7/8. Acteur : Patron. Technique : CT31-02/07.
- **Résultat utilisateur attendu :** Ressources/périodes/compétences et hypothèses de cash/garanties, séparant prévu, déclaré, inconnu et constaté.
- **Code existant :** [calcul daté](../../../backend/app/modules/optimization/application/dated_capacity.py), [service révisionné](../../../backend/app/modules/optimization/infrastructure/dated_service.py), [route Patron](../../../backend/app/interfaces/http/routes/patron_capacity.py); solveur et contrats historiques conservés.
- **Résultat visible / surface existante :** [panneau de capacité](../../../web/src/features/capacity/CapacityPanel.tsx) intégré à l’Affaire, calculs/sources/historique et UNKNOWN; [synthèse existante](../../../web/src/features/cases/CaseResolutionPanel.tsx) sans promotion de couverture globale. Le [socle CASH déclaré](../05_Qualification_locale/L07_ECHEANCIER_DECLARE_2026-11-03.md) dispose désormais de son parcours local de flux/cumuls/révisions ; ce n’est pas une couverture financière complète.
- **Manques précis / qualification restante :** Le parcours de capacité datée est implémenté et éprouvé localement (dossier ci-dessous); validation globale finale terminée (preuves dans le plan). Restent les disponibilités multipériodes/calendriers et charges inter-Affaires automatiques, les garanties non couvertes. Le socle d’échéancier déclaré a sa preuve locale du 03/11. Portefeuille cash avancé explicitement différé.
- **Preuves disponibles :** [backend/tests/application/test_capacity_planning.py](../../../backend/tests/application/test_capacity_planning.py); [backend/tests/application/test_resource_optimization.py](../../../backend/tests/application/test_resource_optimization.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** [Capacité datée Python/API/UI](../05_Qualification_locale/L07_CAPACITE_DATEE_2026-10-23.md) : saisie humaine sourcée, affectations/périodes/conflits, révisions/UNKNOWN et historique. Recette Chromium synthétique11assertions et33tests L07 finaux; backend complet3887/Web644+4ignorés verts sur le code gelé. Aucune preuve d’échéancier cash complet ni de couverture globale déduite.
- **Critère de fonctionnement à démontrer :** Une ressource indisponible et une donnée cash manquante restent visibles ; aucun zéro ou cash certain déduit du silence.

<a id="l08"></a>
## L08 — Réponse acheteur et paquet exact autorisé

- **Exigence :** PF31-03/07/09; M31-02; M2-026 axe11. Acteur : Préparateur puis Patron pour autoriser. Technique : CT31-36–42.
- **Résultat utilisateur attendu :** Réponse technique/administrative substantielle, pièces acheteur, engagements vendus et paquet exact versionné/hashé.
- **Code existant :** [assemblage des contributions](../../../backend/app/modules/preparation/application/document_content.py), [contrats et actes](../../../backend/app/modules/preparation/application/review.py), [provenance courante](../../../backend/app/modules/preparation/infrastructure/contribution_sources.py), puis modules natifs : [backend/app/modules/preparation/__init__.py](../../../backend/app/modules/preparation/__init__.py); [backend/app/modules/preparation/application/__init__.py](../../../backend/app/modules/preparation/application/__init__.py).
- **Résultat visible / surface existante :** [web/src/features/wizard/PreparationReviewPanel.tsx](../../../web/src/features/wizard/PreparationReviewPanel.tsx) ; [web/src/features/submission/SubmissionPanel.tsx](../../../web/src/features/submission/SubmissionPanel.tsx). La saisie de contributions humaines par exigence/section est raccordée au wizard; manques UNKNOWN, sources exactes et relecture Patron sur hash, puis snapshot natif. Les actes C10/P5/export historiques gardent leur périmètre. Aucun pli acheteur complet ni couverture automatique démontrés.
- **Manques précis / qualification restante :** Rédaction/revue et cadre DOCX synthétique à régions dédiées qualifiés localement dans leurs preuves; les cadres acheteur arbitraires DOCX/PDF et la couverture exhaustive demeurent ouverts. Les pièces tierces et actes humains de contrôle des signatures ont des preuves locales bornées, sans validation juridique ni signature automatique. Le brouillon Markdown avec sources ne prouve pas la conformité d’un formulaire acheteur. Les manques et portées non prouvés restent UNKNOWN.
- **Preuves disponibles :** [backend/tests/api/test_preparation_routes.py](../../../backend/tests/api/test_preparation_routes.py); [backend/tests/api/test_preparation_transmission_routes.py](../../../backend/tests/api/test_preparation_transmission_routes.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve locale datée du 27/10 :** [assemblage et sélection L08](../05_Qualification_locale/L08_ASSEMBLAGE_SELECTION_2026-10-26.md),27/10 :backend4011,Web695/4ignorés,29contrôles Chromium natifs. Choix/revue exacts et mêmes octets jusqu’au ZIP/conducteur. Le [dossier du24/10](../05_Qualification_locale/L08_CONTRIBUTIONS_REPONSE_2026-10-24.md) reste une preuve historique. Aucun pli acheteur complet, signature ou dépôt déduit.
- **Critère de fonctionnement à démontrer :** Aucune exigence critique sans réponse ou refus explicite ; le ZIP autorisé et exporté correspond au manifeste exact sans prétendre à un dépôt/récépissé externe.


**Complément du 03/11 :** [noms complets sourcés](../05_Qualification_locale/L08_NOMS_COMPLETS_SOURCES_2026-11-03.md), nouveau run de provenance 11 sans troncature du point interne au littéral ; contrôle actuel compare le nom complet, anciens v10 inchangés et ambiguïtés UNKNOWN. Quatre ZIP natifs V1/V2, aucun renommage, conformité ou changement de porte déduit.

<a id="l09"></a>
## L09 — Offre gagnée, écarts et dossier conducteur

- **Exigence :** PF31-04/06; M31-04. Acteur : Patron puis conducteur affecté. Technique : CT31-02/04/06.
- **Résultat utilisateur attendu :** Engagements vendus, exclusions, conditions ouvertes, contrat attribué distinct et dossier conducteur sans données privées.
- **Code existant :** [backend/app/modules/pricing/infrastructure/models/contract_instrument_version.py](../../../backend/app/modules/pricing/infrastructure/models/contract_instrument_version.py); [backend/app/modules/pricing/infrastructure/models/contract_instrument_supersession.py](../../../backend/app/modules/pricing/infrastructure/models/contract_instrument_supersession.py).
- **Résultat visible / surface existante :** [CaseHandoverPanel](../../../web/src/features/results/CaseHandoverPanel.tsx) : sélection P5/contrat déclaré, revue des points et actions/responsables/preuves, inconnus, lecture/reçu exact du Responsable et historique. Python/API/projection/reader/migration0143 dans le [dossier L09](../05_Qualification_locale/L09_OFFRE_CONTRAT_PASSATION_2026-10-25.md).
- **Manques précis / qualification restante :** Contrat/fichier/signature réels non authentifiés, écarts déclarés humainement et corpus synthétique; couverture non exhaustive. Brouillons C10 non présumés inclus dans le P5; actions/responsables déclarés sans exécution ni droit déduit. L09 général PARTIAL; dette de typage des tests hors L09 ouverte.
- **Preuves disponibles :** [backend/tests/domain/pricing/test_contract_instrument_supersession.py](../../../backend/tests/domain/pricing/test_contract_instrument_supersession.py); [backend/tests/domain/pricing/test_contract_execution_evidence_requalification.py](../../../backend/tests/domain/pricing/test_contract_execution_evidence_requalification.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Backend 3964 passed, 1 warning in 1519.68s (0:25:19); Web668/4ignorés,25contrôles Chromium synthétiques et34SHA stables. Invalidation, tenant/rôle/finance/MFA, reprise et concurrence, append-only et migration0143 qualifiés. Limites et non-qualification CI dans le dossier L09.
- **Critère de fonctionnement à démontrer :** Le conducteur retrouve l’obligation et sa condition/source sans marge ni hypothèses privées ; P7 ne devient pas un OS.

<a id="l10"></a>
## L10 — Changements en exécution et actions prouvées

- **Exigence :** PF31-04/08; M31-05. Acteur : Conducteur et Patron selon droits. Technique : CT31-02/04/07.
- **Résultat utilisateur attendu :** Instruction/OS/avenant relié à l’engagement concerné, delta déclaré et action/preuve suivis dans la chronologie.
- **Code existant :** [backend/app/modules/dce/application/impact.py](../../../backend/app/modules/dce/application/impact.py); [backend/app/modules/pricing/domain/contract_instrument_supersession.py](../../../backend/app/modules/pricing/domain/contract_instrument_supersession.py).
- **Résultat visible / surface existante :** [CaseContractChangePanel](../../../web/src/features/decision/CaseContractChangePanel.tsx) : pointsL09 exacts, delta, actions/responsables/preuves, historique/requalification; [OperationalChangeRead](../../../web/src/features/decision/OperationalChangeRead.tsx) : lectureResponsablefiltrée. CodesPython/API/migration0144 dansle [dossierL10](../05_Qualification_locale/L10_CHANGEMENTS_EXECUTION_2026-10-25.md).
- **Manques précis / qualification restante :** GénéralPARTIAL; deltaopérationneltextuel, impactsquantifiésprivésC3sur sourcesA1. Corpus/auth/scannerréels, adéquationterrain, réceptionexterne et calculjuridique/calendaire nonqualifiés. Sanctionsquantitatives/settlement/DGDstructurés différésparPF31-09; dette mypytests horsL10ouverte.
- **Preuves disponibles :** [backend/tests/application/test_case_dce_impact.py](../../../backend/tests/application/test_case_dce_impact.py); [backend/tests/domain/pricing/test_contract_instrument_supersession.py](../../../backend/tests/domain/pricing/test_contract_instrument_supersession.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Backend 3983 passed, 1 warning in 2342.53s (0:39:02);672Web/4ignorés,10scénarios Chromium/47assertions,31SHAstables. MêmeAffaireoffre/passation/instruction/delta/action/preuveSHA, puisremplacement/requalification sans transfert implicite; refus/tenants/concurrence/rollback/UNKNOWNqualifiés synthétiquement, CIentière nonqualifiée.
- **Critère de fonctionnement à démontrer :** Changement → engagement → condition → action → preuve exacte consultables ; nouvelle version invalide les relations à revoir sans effacer l’historique.

<a id="l11"></a>
## L11 — Réception, paiement, sortie et retour d’expérience

- **Exigence :** PF31-08/09; M31-05/07; M2-026 axe12. Acteur : Patron et intervenants autorisés. Technique : CT31-04/07.
- **Résultat utilisateur attendu :** Réserves/obligations/événements de paiement distincts, actions de préservation et enseignements sourcés.
- **Code existant :** [backend/app/modules/pricing/infrastructure/models/contract_execution_evidence.py](../../../backend/app/modules/pricing/infrastructure/models/contract_execution_evidence.py); [backend/app/modules/pricing/domain/contract_execution_evidence.py](../../../backend/app/modules/pricing/domain/contract_execution_evidence.py).
- **Résultat visible / surface existante :** [web/src/features/decision/PostReceptionObligationsPanel.tsx](../../../web/src/features/decision/PostReceptionObligationsPanel.tsx) ; [web/src/features/enterprise/TeachingApplicabilityPanel.tsx](../../../web/src/features/enterprise/TeachingApplicabilityPanel.tsx). Parcours intégré [CaseClosurePanel](../../../web/src/features/decision/CaseClosurePanel.tsx), registres natifs et API privée : réception/réserve/action/responsable/preuve, facture/attente/encaissement distincts, sortie sourcée et REX humain. Les actes déclarés ne prouvent pas un règlement final complet.
- **Manques précis / qualification restante :** Chaîne humaine et écarts locaux qualifiés le26/10; preuves documentaires référencées, sans inspection bancaire/juridique/externe réelle. Calcul juridique/calendaire validé, sanctions quantitatives et settlement/DGD structurés restent différés par PF31-09.
- **Preuves disponibles :** [backend/tests/db/test_contract_execution_evidence_e2e.py](../../../backend/tests/db/test_contract_execution_evidence_e2e.py); [backend/tests/domain/pricing/test_contract_execution_evidence.py](../../../backend/tests/domain/pricing/test_contract_execution_evidence.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Parcours synthétique complet qualifié : backend3993,Web678/4 ignorés,24 assertions navigateur finales; [dossier L11](../05_Qualification_locale/L11_RECEPTION_PAIEMENT_SORTIE_REX_2026-10-25.md). L11 général PARTIAL, reports PF31-09 inchangés.
- **Critère de fonctionnement à démontrer :** Facture, paiement attendu et encaissement restent distincts ; date déclarée ≠ échéance juridique ; réemploi du REX nécessite acte humain.

<a id="t01"></a>
## T01 — Accès, rôles et confidentialité de tous les livrables

- **Exigence :** PF31-05/06/07; M31-07. Acteur : Tous acteurs selon politique serveur. Technique : CT31-06.
- **Résultat utilisateur attendu :** Session/MFA/step-up/permissions, refus sans fuite, retry sans double effet.
- **Code existant :** [backend/app/platform/security/authenticated_context.py](../../../backend/app/platform/security/authenticated_context.py); [backend/app/platform/security/authentication.py](../../../backend/app/platform/security/authentication.py).
- **Résultat visible / surface existante :** [web/src/features/auth/MfaPanel.tsx](../../../web/src/features/auth/MfaPanel.tsx) ; [backend/app/platform/security/authorization.py](../../../backend/app/platform/security/authorization.py). Socle testé dans les campagnes historiques et suite pure récente ; pas de nouvelle recette de menace exhaustive.
- **Manques précis / qualification restante :** Rejouer les refus serveur et projections croisées pour chaque verticale ; pas de pentest ou exploitation réelle déduit des tests locaux.
- **Preuves disponibles :** [backend/tests/security/test_authentication_services.py](../../../backend/tests/security/test_authentication_services.py); [backend/tests/security/test_totp.py](../../../backend/tests/security/test_totp.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Aucune recette complète de cette ligne ; ne pas annoncer PASS.
- **Critère de fonctionnement à démontrer :** Aucun objet/compteur/relation privé observable hors droits ; MFA/idempotence/tenant/ownership inchangés.

<a id="t02"></a>
## T02 — Intégrité, qualification et exploitation maîtrisée

- **Exigence :** PF31-09/10; M31-08/09. Acteur : Owner et exploitation autorisée. Technique : CT31-08/09/10.
- **Résultat utilisateur attendu :** Migrations/provenance/export/audit/reprise vérifiables et bilan de limites, avant toute ouverture.
- **Code existant :** [backend/app/modules/patron_action/infrastructure/models/patron_action.py](../../../backend/app/modules/patron_action/infrastructure/models/patron_action.py); [backend/app/modules/dce/infrastructure/models/contract_query_export.py](../../../backend/app/modules/dce/infrastructure/models/contract_query_export.py).
- **Résultat visible / surface existante :** [backend/app/platform/persistence/schema.py](../../../backend/app/platform/persistence/schema.py) ; [ops/restore-preprod.sh](../../../ops/restore-preprod.sh). Scripts/contrats de schéma/preuves locales présents ; A1 Golden non admis/A2 HOLD/NO-GO public demeurent.
- **Manques précis / qualification restante :** Droits corpus/validation métier, restauration et exploitation réelle restent à qualifier ; ERP et validation marché ne sont pas déduits des adaptateurs.
- **Preuves disponibles :** [backend/tests/db/test_contract_query_export_audit_persistence.py](../../../backend/tests/db/test_contract_query_export_audit_persistence.py); [backend/tests/db/test_contract_query_export_persistence.py](../../../backend/tests/db/test_contract_query_export_persistence.py). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Aucune recette complète de cette ligne ; ne pas annoncer PASS.
- **Critère de fonctionnement à démontrer :** Preuves datées et périmètre explicite ; aucun GO public ou déploiement inféré de cette matrice.

<a id="t03"></a>
## T03 — Parcours utilisables et lisibilité transversale

- **Exigence :** PF31-06/11; M31-03/04/05. Acteur : Tous acteurs dans leurs permissions. Technique : CT31-06.
- **Résultat utilisateur attendu :** Accès compréhensible aux sources, états et actions, clavier/responsive et masquage hors contexte.
- **Code existant :** [web/src/app/App.tsx](../../../web/src/app/App.tsx); [web/src/app/deepLink.ts](../../../web/src/app/deepLink.ts).
- **Résultat visible / surface existante :** [web/src/app/App.tsx](../../../web/src/app/App.tsx) ; [web/src/features/dce/useDceKnowledge.ts](../../../web/src/features/dce/useDceKnowledge.ts). Panneaux et plusieurs recettes navigateur synthétiques existent ; aucune recette UX exhaustive de toutes les surfaces dans ce bilan.
- **Manques précis / qualification restante :** Qualifier chaque livrable complet en navigateur, règles de masquage et accessibilité ; utiliser OpenDesign Local Codex/Impeccable avant toute édition visible.
- **Preuves disponibles :** [web/src/app/App.test.tsx](../../../web/src/app/App.test.tsx); [web/src/features/decision/PatronDecisionPanel.test.tsx](../../../web/src/features/decision/PatronDecisionPanel.test.tsx). Les dossiers datés du plan gardent leur périmètre historique.
- **Preuve rejouée maintenant :** Aucune recette complète de cette ligne ; ne pas annoncer PASS.
- **Critère de fonctionnement à démontrer :** Le résultat métier est lisible dans le parcours existant ; capture/prototype seul ne vaut pas assertions de fonctionnement.

## Ordre d’exécution : un résultat métier à la fois

1. **L03/L04 — dossier d’analyse d’une Affaire** : pièces et sources courantes, douze axes visibles, points critiques et inconnus. Réutiliser les exigences/risques/relations existants.
2. **L05/L06 — engagement et économie** : même engagement, offre partenaire exacte, transport exclu, impact déclaré, condition Patron ; ne pas refaire la verticale A1 déjà prouvée sur son scénario.
3. **L07 — capacité/cash minimum** : hypothèses et inconnus par Affaire, sans portefeuille avancé.
4. **L08 — sortie acheteur** : réponse substantielle, exigences couvertes et paquet exact autorisé ; dépôt humain.
5. **L09 → L10 → L11** : contrat gagné/passation, changement/action/preuve puis réception/sortie/REX sur la même Affaire.

L01/L02 et T01–T03 sont réutilisés et vérifiés à chaque verticale ; une régression de sécurité ou source bloque la livraison concernée. Les dépendances et embeddings sont évalués quand ils empêchent un de ces résultats ; pas de remplacement opportuniste ni nouvelle succession de micro-versions de parseur comme pilotage principal.

## Première tranche concrète : synthèse L04 dans les parcours existants

**Observation de code actuelle :** `CaseDceReadingResponse` expose DCE, compteurs, exigences et couverture documentaire. `CaseDceCoverageResponse` garde explicitement `analysis_complete=False`, `inventory_completeness=UNKNOWN` et `REVIEW_REQUIRED`. Les panneaux de risques/impacts/conditions existent séparément. L’absence de synthèse12axes dans ce DTO ne signifie pas absence de tous les autres modules. Le besoin est d’assembler un résultat cohérent et sourcé, sans reconstruire les registres.

**Sortie attendue :** pour une Affaire/version exacte, le Patron voit les12axes et, sur chacun, les faits candidats ou confirmés, les preuves courantes, les inconnus et l’action nécessaire. Un axe vide est NON ÉVALUÉ, pas « sans risque ». Une extraction complète ne clôture pas un axe. Un risque garde conséquence/responsable/action/preuve absents comme UNKNOWN. Les confirmations humaines et P0–P7 sont inchangés.

**Insertion :** partir de la lecture DCE, des projections risques/relations/exigences existantes et de la Carte d’Engagement existante ; déterminer le propriétaire de la projection en respectant les contrats publics, sans port/stockage générique ni nouveau moteur RAG. Commencer par le contrat/projection et les tests backend ; OpenDesign Local Codex puis Impeccable avant toute édition visible de l’interface existante.

**Recette de fin :** Affaire synthétique site occupé, CCTP accès contraint, exclusion transport partenaire, pièce critique non extraite, exigence conditionnelle et rectificatif. Vérifier source/version/hash/locator, lien exigence→risque→impact/condition quand établi, trous visibles sinon, lecture autorisée et refus tenant/Affaire/rôle, invalidation et aucune fuite de données financières/personnelles ou de compteurs privés. Le conducteur/Collaborateur n’observe aucune conséquence économique privée. Mesurer omissions par sortie attendue et faire des assertions sur le parcours, pas seulement une capture.

La mise en place d’une projection ne vaut pas, à elle seule, analyse des12axes. La recette devra distinguer ce qui est assemblé, ce qui provient d’un humain et ce qui est automatique ; aucun GO public ni admission Golden n’en découle.

## Preuve fraîche et contrôle documentaire

Campagne synthétique :86 tests/22,28s/exit0 sur `test_case_dce_reading_projection.py`, `test_dce_rc_analysis.py`, `test_dce_requirements.py`, `test_case_dce_reading_reader.py`. Elle prouve les contrats locaux exercés (provenance, états, refus, extraction/analyse/matérialisation/rejeu), pas la complétude réelle d’un DCE ni la qualité de tous les axes. PostgreSQL dédié sans réseau/ports publics, URL explicite ; aucune base métier. Logs/manifeste privés dans `~/.local/share/smartao-proofs/livrables-metier-20261019/`.

Méthode : Graphify puis lecture ciblée, ECC product-capability et cadrage/planification Superpowers déjà appliqués. Pas d’édition de production, donc pas de nouvelle TDD de comportement ni scan Semgrep requis sur du Markdown/CSV ; contrôles de références, familles, chemins et tests documentaires. Aucun changement visible nécessitant OpenDesign dans cette tranche ; obligation conservée pour l’implémentation UI à venir. Basic Memory proposé localement, transmission toujours en attente de l’autorisation déjà demandée.

A1 Golden non admis ; A2 générique HOLD ; UNKNOWN/FINANCIAL_PRIVATE/PERSONAL_DATA/tenant/MFA/append-only et NO-GO public maintenus. Aucun corpus réel/live/VPS/déploiement/P3/dépôt externe/commit/push.

Base finale Alembic0 vérifiée,conteneur dédié retiré. Aucune modification de production dans cette tranche ; le codage de la synthèse L04 suit dans la prochaine tranche.

Prochaine étape : L04 — implémenter et qualifier la synthèse sourcée des douze axes du dossier d’analyse d’une Affaire dans les projections et parcours existants, avec pièces non lues, exigences, risques et UNKNOWN visibles; prouver source/version/lot, invalidation et refus tenant/rôle sans modifier les confirmations ni les portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.


## Actualisation L04 — 20 octobre 2026

Assemblage initial qualifié ; critères métier complets non atteints. Le détail des preuves et limites figure dans le dossier L04 du20/10 et le statut opérationnel dans le plan global.

Prochaine étape : L04 — raccorder les exigences et risques sourcés aux actions, responsables et conséquences déjà enregistrés, avec preuves et portées exactes; rendre visibles les relations manquantes en UNKNOWN, qualifier invalidation et refus tenant/rôle dans la synthèse existante sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.


## Actualisation relations L04 — 20 octobre 2026

Raccordements natifs qualifiés ; plan global seul statut opérationnel.

Prochaine étape : L04 — restituer dans la synthèse le fait/extrait source exact, la criticité, les preuves attendues et le risque résiduel déjà enregistrés pour chaque point critique; qualifier ancres, invalidation et lecture Patron, avec UNKNOWN sur les champs absents sans inférer une analyse complète ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.


Prochaine étape : L04 — implémenter un enregistrement humain révisionné des preuves attendues et du risque résiduel des points critiques, avec source/version/portée exactes, UNKNOWN, append-only, concurrence et contrôles tenant/rôle; qualifier saisie et relecture sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Actualisation actes humains L04 — 20 octobre 2026

Preuves attendues et risque résiduel déclarés par le Patron désormais révisionnés et relus avec source SHA/version/portée, auteur/date et justification; absence reste UNKNOWN. Append-only, MFA, concurrence, retry et invalidation qualifiés localement. Ce sont des déclarations humaines, pas une analyse exhaustive ni une preuve reçue. L04 et ses familles restent PARTIAL. Voir [dossier](../05_Qualification_locale/L04_ACTES_HUMAINS_2026-10-20.md).

Prochaine étape : L04 — raccorder à l’axe Prix et marge les scénarios économiques natifs déjà enregistrés pour l’Affaire, avec révision, hypothèses et provenance exactes; afficher les absences ou obsolescences en UNKNOWN et qualifier tenant/rôle/FINANCIAL_PRIVATE sans utiliser le RAG pour la DPGF ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Actualisation Prix/marge L04 — 20 octobre 2026

Scénarios natifs reliés à PRICE; chiffres/hypothèses/source/révisions visibles, obsolescence UNKNOWN et refus financiers qualifiés. L04 reste PARTIAL; aucune analyse DPGF/RAG ni coût BTP exhaustif déduit. [Dossier](../05_Qualification_locale/L04_PRIX_MARGE_SCENARIOS_NATIFS_2026-10-20.md).

Prochaine étape : L04 — raccorder à l’axe Trésorerie et garanties les déclarations financières publiées et réserves déjà enregistrées pour l’Affaire, avec source/révision et hypothèses exactes; laisser UNKNOWN l’échéancier, le pic de financement et toute portée non prouvés, puis qualifier invalidation et confidentialité sans modifier confirmations ni portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Actualisation CASH L04 — 20 octobre 2026

Rapports publiés et réserves distinctes de scénarios raccordés : montants déclarés/lignes/source/révisions exacts; manque/discordance/obsolescence UNKNOWN; calendrier/pic/portée non prouvés. Lecture privée qualifiée localement, pas une preuve de liquidité ni de complétude économique. L04 PARTIAL. [Dossier](../05_Qualification_locale/L04_TRESORERIE_GARANTIES_NATIVES_2026-10-20.md).

Prochaine étape : L04 — raccorder à l’axe Capacité et ressources les exécutions de planification natives déjà enregistrées pour l’Affaire, avec révision, hash des entrées, hypothèses et statut solveur exacts; afficher UNKNOWN les sources, disponibilités ou portées non prouvées et qualifier invalidation/tenant/rôle sans lancer de solveur ni modifier confirmations ou portes. DPGF non évaluable par RAG, aucun moteur candidat activé; A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Journal de correction du pilotage — 20 octobre 2026

Décision Owner appliquée : unité de livraison = résultat fonctionnel utilisable, sous-tâches techniques internes. Correction de la mention obsolète « actes humains à coder » dans fiche/CSV et du classement de la synthèse12axes sous L03. Les anciennes mesures/prochaines étapes ci-dessus restent des traces datées, pas l’ordre actuel; les acquis locaux ne clôturent pas L04. Aucun code de production ou test logiciel modifié lors de cette révision documentaire; aucun nouveau comportement qualifié. Le plan global porte le seul statut et la prochaine étape.

## Preuve locale L04 — 21/10/2026 — multi-formats et rectificatif

[Qualification](../05_Qualification_locale/L04_MULTIFORMATS_RECTIFICATIF_2026-10-21.md) : code partagé extraction DOCX/registre courant corrigé; parcours natif PDF-DOCX-XLSX, trois points source/version/lot et une annexe non lue, V1 puis V2 et reprise sur la même version traités/revus. Historique conservé, ancien point refusé, tentative échouée invalide sans effacer;3730backend/96ciblés/37synthèse-reprise verts. Ceci ne clôt pas L04 : tableaux non extraits, livrables techniques/durées explicites hors grammairev7 et analyse entière non qualifiée. Le plan global reste l'unique statut et porte la suite exacte.

## Preuve locale L04 — 21–22/10/2026 — livrables techniques et durées

[Qualification](../05_Qualification_locale/L04_LIVRABLES_TECHNIQUES_DUREES_2026-10-21.md) : deux omissions corrigées dans la recette native8, négations/conditions et refus financiers conservés, validation7 inchangée. Dossier de développement neuf pièces PDF/DOCX/XLSX/texte,34/34points avec sources/locators/lots exacts, traitements/revue puis rectificatif6→9semaines et historique qualifiés. Backend3763réussites;31dédiés/384domaine/126ciblés verts, sans somme des ensembles recouvrants. Les tableaux et la généralisation restent non qualifiés, analyse_complete=false. L04 reste PARTIAL; le plan porte seul le statut et la prochaine étape exacte.

## Preuve locale L04 — 22/10/2026 — prescriptions des tableaux DOCX

[Qualification](../05_Qualification_locale/L04_TABLEAUX_DOCX_2026-10-22.md) : lecture des cellules simples et ancres exactes codées, contexte intercellulaireUNKNOWN et structures ambiguës refusées.37points du dossier complet traités/revus avec rectificatif et historique; navigateur synthétique39intentions→37traitements+2revues, masquage et refus rôle. Backend3795/Web628+4ignorés verts. Les cellules ne nourrissent pas le RAG ou les comparateurs automatiques sans contexte qualifié. Aucun nouveau droit/gate/admission/activation, analyse_complete=false, L04 global PARTIAL. Le plan porte seul le statut et la prochaine étape exacte.


## Preuve locale L04 — 22/10/2026 — contexte sourcé des tableaux DOCX

[Qualification](../05_Qualification_locale/L04_CONTEXTE_TABLEAUX_DOCX_2026-10-22.md) : en-têtes de lot, conditions et négations restitués comme textes exacts de cellules avec provenance propre, sans héritage automatique. Traitement37points, préparation/revue et rectificatif de contexte seul qualifiés, actes invalidés/historique conservé; limites et discordances UNKNOWN. Backend3809/Web629+4ignorés verts;15assertions navigateur synthétique puis6rectificatif,37actes+2revues sans doublon. Aucune modification de portes ni activation; grands tableaux/structures complexes et généralisation non qualifiés. L04 reste PARTIAL, analyse_complete=false. Le plan porte seul le statut et la prochaine étape exacte.


## Fonction L06 — 23/10/2026 — bordereau multi-feuilles vers brouillon

[Code et preuve](../05_Qualification_locale/L06_IMPORT_FINANCIER_2026-10-23.md) : parser/commandes/API/persistance/UI modifiés, toutes les feuilles compatibles et lignes consultables, sources de cellules conservées, quantités/formules/montants ambigus refusés, aperçu incomplet non committable.17parseur/103financiers-API-SQL-migration et backend3830réussites verts;Web631/4ignorés. Navigateur synthétique25postes→25lignes/61000centimes une fois, sources et refus financiers. Ceci livre le sous-parcours d’import natif; obligations/coûts/devis/couverture/devise/lien DCE et original binaire restent des manques de L06, pas un résultat déduit des compteurs. L06 global PARTIAL; seul le plan fixe la suite.


## Fonction L06 — 23/10/2026 — chiffrage sourcé par poste

[Code et preuve](../05_Qualification_locale/L06_CHIFFRAGE_PAR_POSTE_2026-10-23.md) : sélection/revue humaine de l’obligation confirmée, coûts natifs, offre/prix et transport; sources et révisions exactes, origine de fichier par hash ouUNKNOWN. Coûts absents, bases/unités/devises différentes, exclusions, expiration et réutilisations visibles, sans allocation/FX/coût couvert déduits. Actes append-only révisionnés, invalidation et historique complet. Backend3854/Web638+4ignorés et15assertions navigateur synthétiques. L06 global reste PARTIAL pour couverture économique générale; le parcours de rattachement est utilisable localement. Suite fonctionnelle L07 dans le seul plan.


## Raccord transversal qualifié localement — 26 octobre 2026

La [preuve T01–T03](../05_Qualification_locale/T01_T03_CONTINUITE_AFFAIRE_2026-10-26.md) suit une même Affaire synthétique multi-pièces/deux lots de L04 à L11 puis un réemploi explicite dans une seconde Affaire. Capacité, engagement, réponse revue, ZIP et document conducteur, changement, réception/paiement et REX ne sont plus seulement juxtaposés dans des fixtures indépendantes. Les ruptures réelles de provenance, préparation, publication et retry ont été corrigées dans les modules natifs. Les garanties générales restent PARTIAL et aucun pourcentage produit n’est déduit de4005tests. Le plan global garde seul statut et prochaine étape.

L08 conserve un manque fonctionnel explicite : plusieurs contributions/textes revus différents ne sont ni sélectionnés ni fusionnés arbitrairement. Le document unique composé et sa revue exacte doivent être livrés avant de prétendre couvrir cette pluralité. Les formats et cadres acheteur spécifiques, signatures et exigences exhaustives demeurent ouverts.


## Assemblage et sélection L08 — complément du 27 octobre

Le manque de sélection explicite identifié par la preuve transversale est levé localement : le document natif unique contient plusieurs contributions sourcées, est choisi et revu sur son hash exact, puis conservé jusqu’au ZIP et au conducteur. Plusieurs brouillons complets concurrents ne sont pas fusionnés arbitrairement. Les cadres et formats acheteur spécifiques restent un manque distinct; le Markdown natif ne prouve pas leur conformité. Le plan global reste seul statut et prochaine étape.


## Cadre acheteur DOCX L08 — complément du 27 octobre

[Remplissage DOCX et preuve locale](../05_Qualification_locale/L08_CADRE_ACHETEUR_DOCX_2026-10-27.md) : contributions sélectionnées depuis le Markdown source exact accepté, régions de paragraphe/cellule hashées, champ sans contribution UNKNOWN, brouillon binaire distinct et revue Patron exacte. Mêmes octets au ZIP et téléchargement Conducteur avec MIME/extension corrects.137tests ciblés backend,704Web/4ignorés,18assertions navigateur natives; couverture backend complète4027tests consolidés en deux segments après correction de fixture, code applicatif gelé. Statut/next uniquement dans le plan. Les cadres synthétiques contiennent des marqueurs dédiés; aucune conformité de cadre arbitraire, signature ou pli complet n’est déduite. Aucun moteur candidat activé ni porte modifiée.


## Actualisation des preuves — 05/11/2026

Le [bilan daté](BILAN_LOCAL_L01_L11_T01_T03_2026-11-05.md) consolide les 14 parcours/garanties sans créer de statut concurrent : ordre et tranche active dans le plan seul. L01/L02 ont des recettes dédiées du03/11 ; L05 reprend FINALIZED par nouveau brouillon après DCE changé (04/11), sans rouvrir un même DCE. L07 dispose de l’échéancier déclaré par Affaire et de sa reprise (03–04/11), sans cash certain. L08 noms complets (03/11), puis chiffrage révisé→pli exact (04/11), L09→L11 et T01–T03 (04–05/11) ont des preuves locales bornées. Les descriptions historiques « preuve rejouée maintenant » ci-dessus désignent leur campagne datée, pas un rejeu effectué dans ce bilan. Les contrôles humains des pièces/signatures, assurances et autres pièces tierces ont leur périmètre synthétique ; ils ne prouvent ni leur validité ni la conformité du pli complet. DOCX reste clos localement. Voir le bilan pour les manques réels, entrées humaines, reports PF31-09 et limites de sources ; aucun report Owner nouveau décidé ici.


**Complément L06 du05/11 :** [répartition déclarée](../05_Qualification_locale/L06_REPARTITION_COUT_PARTAGE_2026-11-05.md), montants/reste et historique natifs, nouvelle revue humaine après remplacement ; aucune réécriture du coût natif ou du prix publié. Voir le plan seul pour l’ordre et le statut.


**Complément L06 publication du05/11 :** [recette native et limites](../05_Qualification_locale/L06_REPARTITIONS_CHIFFRAGE_PUBLIE_2026-11-05.md), publication→invalidation→nouvelles répartitions→révision, historique et données JSON publiées inchangées. Provenance visible en Prix ; les revues ultérieures ne font pas partie du contenu publié. Statut et prochaine tranche dans le plan seul.


**Complément L07 du05/11 :** [chiffrage publié et flux datés](../05_Qualification_locale/L07_CHIFFRAGE_PUBLIE_FLUX_DATES_2026-11-05.md), provenance financière exacte enregistrée dans les nouveaux actes, sources anciennes UNKNOWN sans enrichissement, remplacement et nouveaux consentements ; calculs inchangés et cash certain non déduit. Unicité des formulaires après relecture corrigée. Statut et prochaine tranche dans le plan seul.


**Complément L08 du05/11 :** [reprise avec flux privés présents](../05_Qualification_locale/L08_REPRISE_CHIFFRAGE_FLUX_PRIVES_2026-11-05.md), nouveau chiffrage publié/revues/pli exact, nouveaux actes P5 sans héritage et absence des registres privés dans les sorties vérifiées ; modification CASH ultérieure sans changement du ZIP. Fonctionnement local, pas une offre complète, validité ou conformité déduite. Statut et ordre dans le plan seul.


**Complément L09 du 11/11 :** [passation et flux privés](../05_Qualification_locale/L09_PASSATION_FLUX_PRIVES_2026-11-11.md), sources et reçus exacts, sans héritage et sans marqueurs privés dans les sorties exercées. Le plan seul porte le statut.


**Complément L10 du 11/11 :** [changements et flux privés](../05_Qualification_locale/L10_CHANGEMENTS_FLUX_PRIVES_2026-11-11.md), événements/actions sur passations exactes, anciennes sources à revoir et C3/C4 UNKNOWN dans ce parcours. Le plan seul porte le statut.


**Complément L11 du 11/11 :** [clôture et flux privés](../05_Qualification_locale/L11_CLOTURE_FLUX_PRIVES_2026-11-11.md), actes et réserves sourcés, paiement déclaré et requalification après invalidation, sans héritage. Simulation SQL et limites explicites ; le plan seul porte le statut.
