# R4 — Chaînes de listes RC — 15 octobre 2026

## Synthèse lisible

**Statut :** qualification technique locale acquise sur le périmètre testé. Les cinq omissions résiduelles restent non qualifiées ; aucun statut Golden ou GO public n'est accordé.

La correction relie les listes entre parties d'une même page et sur plusieurs pages. Chaque région reste rattachée à son fragment original. Un mot ou un en-tête découpé peut être reconstitué uniquement lorsque l'identité de l'extraction, les hashes et la continuité sont prouvés. Les préfixes incomplets restent ambigus.

| Contrôle acquis | Résultat |
|---|---|
| Détecteur et texte exact | 94 tests purs réussis |
| Extraction, SQL, lecture et API | 119 tests ciblés réussis |
| Panneau | 13 tests réussis |
| Web global, exécution en série | 547 réussites, 4 tests ignorés |
| Types, lint, build | Verts ; avertissement de taille de bundle conservé |
| Semgrep | 225 règles, 10 fichiers, aucun constat ni erreur |
| Sources et navigateur | Deux PDF synthétiques, chaînes vérifiées, affichage local vérifié |
| Backend global final | **2 727 réussites, 2 avertissements, 1 367,89 s, sortie 0** |

**Mesure de calibration :** 9 occurrences omises corrigées ; 5 occurrences restent non détectées dans les tableaux, titres répétés et en-têtes avec portée lot. Ces mesures concernent 14 cas synthétiques créés par Codex, pas des DCE réels ni des annotations humaines Golden. Présence, applicabilité et criticité restent `UNKNOWN`.

Le journal ci-dessous conserve les essais rouges, les erreurs de fixtures et les limites. Les fichiers du dépôt et les preuves privées permettent de rejouer les contrôles.


## AS-IS / risques / insertion
Reprise bornée entre deux pages déjà qualifiée. Restent omis les listes sur trois pages et les découpes d'une même page. Risques : concaténation sans preuve, mots/en-têtes découpés, offsets attribués au mauvais fragment, en-tête conservé malgré rupture, coût non borné. HEAD30f26934430095632000a1d82519f61dbb4c6411,branchecodex/reconcile-smartao-20261009,WIPpréservé.

## Plan minimal — Superpowers/ECC
- [x] TDD : omissions même page/trois pages, découpes de mots/en-têtes, négations et ruptures; référence synthétique sans attendus injectés dans l'extracteur.
- [x] Réutiliser le détecteur sur séquences prouvées : concaténation exacte entre parts, séparateur explicite entre pages; remapper chaque région vers son fragment original. Ancres d'en-tête, continuité et annonce, bornes et refus sans résultat partiel.
- [x] Reader/DTO/panneau : même tenant/document/version/extraction, ordinals/pages/parts successifs, tailles de chunks et hashes vérifiés; chaîne lisible sans texte/hash privé exposé, anciennes identités conservées.
- [x] SQL/API/navigateur synthétiques, suites appropriées, types/lint/Semgrep/revue; plan/case/journal/prochaine étape et miroir Basic Memory.

Aucune migration, dépendance, commande, admission ou présence/applicabilité/criticité connue créée. UNKNOWN/REVIEW_REQUIRED conservés,A1nonadmis,A2HOLD,NO-GOpublic. Aucun backend live,corpus réel,VPS,déploiement,push ou effetP3.


## Preuves intermédiaires — pas de clôture globale anticipée

TDD :6rouges de séquence puis89verts; défaut de strip aux bords reproduit (1rouge de hash/texte exact et1SQL de count mismatch) puis corrigé dans DceExtractionFragmentInput.text uniquement via StringConstraints(strip_whitespace=False), validé sur version installée et documentation Context7. Les métadonnées restent normalisées, limites et contrôles de hash/count/SYSTEM inchangés. 91tests purs verts incluant limites et liens invalides.

Quatre modes SQL initialement rouges (3pages, même page, mot/en-tête découpés). Contrat de parseur inconnu reproduit rouge puis refusé; seulement smart-ao-deterministic/version2 est qualifié pour ces jonctions, part8000/part+1 pourconcaténation exacte. Les fixtures de refus ont heurté les contraintes d'unicité lors d'un deuxième enregistrement du même extracteur; corrigées en semant directement une unique preuve synthétique malformée, sans UPDATE ni désactivation de contraintes. Une passe ciblée interrompue6réussites/exit2 n'est pas qualifiante.

Revue indépendante :3rouges d'identité/polarité/lot autonomes,1rouge de version sur listeprolongée,1rouge de préfixe perdu; correction de priorité locale et UNKNOWN. Deux autres rouges (en-tête local incomplet et long1019chars/règle2) corrigés; contexte effectivement retenu vérifié, règles1/2 réservées aux cas historiques, nouvelles chaînes et préfixes nonprouvés règle3. Relecture de5scénarios par lecteur/session simulée, aucun nouveau blocage concret.

Dernier ciblé backend **119/119**,1warningStarlette,51,54s,extractionstd/avancée/reader/API inclus. Typesmypy624,Ruffbackend/scripts,Webtypecheck/lint/build verts;13testsdupanneauverts. Semgrep1.179.0,p/security-audit,225règles/10fichiers,0finding0erreur,codeanalysélocalement/résultatsnonenvoyés. Suite backend globale en cours sur code figé avec DISPOSABLE_DATABASE=1/PRESERVE_C5_RESTORE_FIXTURE=0,log /tmp/smartao-r4d-backend-final.log,session97002,PGjetablesmartao-r4d-proof-20261015,labelr4d-20261015,port55439. Aucun autre runnerDB sur cette base.

Premier global Web :543réussites/4ignorés/4timeouts15000ms,2fichiers App.test etCollaboratorWizardPanel.test,251,94s. Machine sous pression mémoire/swap; aucune preuve de bug produit tirée de cette seule corrélation. Rejeu complet avec1worker en cours, sans retrait de tests ni augmentation des timeouts; log /tmp/smartao-r4d-web-serial.log.

## Mesure figée des omissions
Référence `backend/tests/fixtures/rc_document_announcement_sequences_v1.json`,14cas/22occurrencesfamilles attendues :jeuCodexsynthétique,**pas Golden, ni annotation humaine indépendante, ni mesure de présence documentaire réelle**. Les annotations attendues ne sont jamais passées à l'extracteur; les jointures de test ne prouvent pas celles de production.

| Périmètre | Retrouvées | Omissions | Fauxpositifs de famille |
|---|---:|---:|---:|
| Avant,lecture historique parfragment/2pages |8|14|0|
| Après,ensemble des14cas |17|5|0|
| Après,formes de continuité qualifiées |17|0|0|

**9occurrences omises corrigées**,5restantes :tableau2,titre répétédossier-suite2,en-têtegrammaticalavecportéelot1. Elles restent non qualifiées/UNKNOWN; on ne déduit ni absence réelle ni analyse complète de leur non-détection. SHAfixture1b586c36ba7945be9c916198a08c9dad58e7890197b34bacca3716931eb913d3;comparaison avant sur snapshot local exact du détecteur précédent,d1af39ee41eaff2a8fbd6d9c1be7be721054eb9ab7f84b7c1e5f89f9bdb0271b. Script et métriques horsGit dans /home/noor/.local/share/smartao-proofs/r4d-20261015/.

## Contrat de lecture
Pour règle3, les anciens champs source/contexte désignent la première région correspondante; la chaîne est nécessaire pour lire toutes les régions d'un mot/en-tête découpé. Chaque ancre a fragment/ordinal/page/part/type/offsetUTF8 dans le même document/extraction/version. AncresHEADING,BRIDGE,SOURCE :aucun texte/hash privé ajouté au public. Au plus64ancres/candidat et8192agrégées; rejet REJECTED_LIMIT sans résultat partiel,1Mcaractères/séquence etbornes existantes agrégées conservées. Un préfixe manquant rend aussi ambiguës les annonces qui dépendent de l'en-tête partiel, même si leur corps commence après un saut de ligne. Les lignes autonomes complètes conservent leurs identités/portées/polarités et règles historiques1/2.


## Web et chaîne source — résultats acquis

Rejeu Web intégral **547réussites/4ignorés,66fichiers,120,44s,exit0** avec1worker;aucun timeout ou test modifié. Les4timeouts du premier global ne se reproduisent pas :
- `src/app/App.test.tsx > App readiness integration > clears the submission manifest when the authenticated tenant changes`;
- `src/app/App.test.tsx > App readiness integration > affiche l’état backend et les dépendances dans la configuration API`;
- `src/features/wizard/CollaboratorWizardPanel.test.tsx > CollaboratorWizardPanel > renders readiness, generated document and task controls from server projections`;
- `src/features/wizard/CollaboratorWizardPanel.test.tsx > CollaboratorWizardPanel > shows human-readable DCE and capability choices while keeping identifiers and proof locators out of the UI`.

Deux chaînes réelles sur sourcesPDF synthétiques :3pages/3fragments et1page/2parts,2candidatsCCAP/CCTPchacune. PDForiginal/hash/inputhash etfragments/locators/hash reparsés après teardownsecondaire,ancresHEADING/BRIDGE/SOURCE vérifiées. Tous les octets originaux entre en-tête et annonce sont couverts sans trou/chevauchement; seules les séparations logiques entre pages ne sont pas des octets de fragment. Régionsparcandidat3/4sur3pages,4/4surmêmepage. WordsplitCC+AP reconstruit exactement, sans substitution de lettres. Scope document/extraction/version identique à chaque nœud;UNKNOWNpréservé. Preuvesprivées `three-pages/`, `same-page/`, `source-chain-verification.json` etmanifestsdans `/home/noor/.local/share/smartao-proofs/r4d-20261015/`.

RouteFastAPI/TestClient etSQL réels,maisacteur/politique/runtimeCase synthétiques explicites;pas d'auth live,tenant/Case réel ou E2Eappcomplet. Le vérificateur privé avait initialement lu la version au mauvais niveauJSON; aligné sur le schéma réel `dce.dce_version_id`, puis vérification complète verte. Aucun changement produit pour cette correction d'outil.

ChromeDevToolsLocal isolé,composant/CSSréels etprojectionsAPI capturées. Régions de chaque page/part affichées;anciencas retiré lorsduswitch;chaînesmasquéessanscouverture;UNKNOWN/analysecomplètenondémontrée visibles. Largeurs réellementmesurées393/1440sansdébordement;requête387clampéeà393surce navigateur.13requêtesloopback,aucuneexterneobservée. Harnaisarrêté/ongletfermé. PasPlaywrightMCP,aucune nouvelle interaction métier.

11empreintesfinales code/tests/référence vérifiéesinchangées,Semgrep1.179.0/225règles10fichiers0finding0erreur;JSONréférence mesuré et contrôlé séparément. Résultats globauxbackend encoreattendus;aucunPASSanticipé.

## Méthodes et invariants
Superpowers using-superpowers/brainstorming/writing-plans/TDD/systematic-debugging/requesting-code-review/verification;ECC verification-loop etsecurity-review danslarevue. Graphify interrogé avantleslectures(grapheancien,orientationseulement),pasdenavigationSerenasupplémentaire. Context7 etversioninstallée pourla surchargePydanticde whitespace;OpenDesignMCPcourantLocalCodex etdesignOwnerPF31-11conservés,Impeccablecontext/craft-floor/detect([]),aucunstyle/palette/typeinventé. Jev/Manusnonutilesàceparseurdéterministeborné;pasdevalidationhumaineinventée. Isolationtenant,ownership/permissions,MFA/FINANCIAL_PRIVATE/PERSONAL_DATA etcommandes inchangés;texte/hash/count exacts renforcés sans mutationhistorique,sourceprovenance/UNKNOWN/review conservés. Aucun schéma/dépendance/effetP3/admission/publicGO.


## Dernier correctif de coût avant clôture

Le contrôle adversarial a établi un retour arrière excessif dans `_OBJECT_GAP` :1 000 espaces + caractère invalide en1,391s,8 000 espaces au-delà du budget3s. Cette limite existante devient critique quand plusieurs parts sont reconstituées en une longue ligne. Deux régressions à budget2s (sans préfixe et après `de `) ont été observées rouges. Quantificateurs possessifs sur espaces/ponctuations corrigés,alternatives de mots inchangées;CPython les supporte depuis3.11 et le dépôt exige3.12,documentationContext7 etruntimevérifiés. Aucune dépendance ajoutée.

**93 tests purs verts.** Comparaison différentielle de1 000 petits cas :0différence;relecture indépendante6 859 combinaisons :0différence. Rejet8 000espaces en12µs et1million en2,3msmesurés;relecture4préfixes/1million en2,66–2,85ms. Ce sont des sondes bornées, pas une certification de complexité de tous les motifs. Calibration14cas inchangée17TP/5FN/0FPfamille.

Global précédent volontairement interrompu :2 506 réussites,1warning,1 590,87s,exit2,**non qualifiant globalement**. Ancien journal conservé `smartao-r4d-backend-interrupted-cost.log`. **Seul runner final courant : session67459, `/tmp/smartao-r4d-backend-qualified.log`**,avec les mêmes paramètres jetables explicites. Empreintes11fichiers renouvelées :seulsle détecteur et ses régressions de coût ont changé;DTO/frontend/contratdecommandeinchangés. Captures sources/API/navigateur précédentes archivées sous`pre-cost-captures/`;capturesPDF/SQL/API à nouveau rejouées sur le code final, navigateur à relire sur ces données. AucunPASSglobalanticipé.


### Borne finale de ligne et reprise exacte

La reconstitution conserve aussi le budget logique de8 000caractères parligne :1rouge de limite puis94pursverts. Desdocuments de plus de8kcaractères avec lignes courtes restent acceptés;les lignes plus longues donnent REJECTED_LIMIT etaucuncandidatpartiel. Cetteborneévited'élargir implicitement l'ancienne borneparfragment dans les boucles de validation. Aucune troncature,masque de texte ou seuil de normalisation ajouté.

La passe aprèscoût a été interrompue pour figer cetteborne :172réussites,1warning,345,09s,exit2,nonqualifianteglobalement. **Seul runner final : session5922, `/tmp/smartao-r4d-backend-qualified-final.log`**. ParamètresPGjetablesinchangés etcontrôlés;nepasrelancerconcurremment. 11SHAfinals vérifiésinchangés après gel,semgrep final surcecode.

LescapturesPDF/SQL/API ontétérejouéesaprèscoût;le détecteur final avecborne de ligne reproduit exactement chaque type/offset/fragment/claim/lot de leur chaîne depuislesPDFreparsés. Sourceverificationflags `current_detector_reproduces_captured_anchor_chain=true` pourles2modes. Navigateur final relu surlesnouveauxUUIDssources :1440pxdesktop et394pxmobile réels,sansdébordement;chaînespages/parts etUNKNOWNvisibles,anciencas etsanscouverturemasqués,13requêtesloopback. Capturesprécédentes393pxconservéesdanspre-cost-captures,aucuntransfertdepreuveimplicite. Ongletfinalfermé,harnaisarrêté;pasdelive/authréelle/PlaywrightMCP.


## Résultat final du 15 octobre 2026

La suite backend finale a exécuté **2 727 tests réussis, 2 avertissements, 1 367,89 s, sortie 0**. Aucun test backend ignoré. Les 94 tests purs et les comportements SQL/API ciblés sont inclus dans ce global sur le code final. Journal `smartao-r4d-backend-qualified-final.log` conservé dans le répertoire privé de preuves.

Avertissements observés, non corrigés hors de cette tranche : dépréciation Starlette/httpx ; alias Pydantic `export_id` sans effet dans le contexte de génération de schéma du test `test_concurrent_capability_proposal_double_click_is_one_append_only_act`. L’avertissement de taille de bundle Web demeure également. Les quatre timeouts Web initiaux ne se reproduisent pas dans le global série, sans augmentation de délai ni retrait de test.

Les deux bases jetables ont été vérifiées à Alembic base (0 ligne), puis seul `smartao-r4d-proof-20261015`, label `r4d-20261015`, a été arrêté et retiré. Aucun service live touché. Les onze empreintes code/tests/référence sont inchangées depuis le gel final. Branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP préservé et non commité. Aucun push.

## Fichiers concernés

- `backend/app/modules/dce/application/document_announcements.py`
- `backend/app/modules/dce/application/queries.py`
- `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py`
- `backend/app/modules/dce/public/contracts.py`
- `backend/tests/domain/dce/test_document_announcements.py`
- `backend/tests/application/test_dce_document_announcements.py`
- `web/src/shared/types.ts`
- `web/src/features/dce/DceKnowledgePanel.tsx`
- `web/src/features/dce/DceKnowledgePanel.test.tsx`
- `backend/app/modules/dce/application/commands.py`
- `backend/tests/fixtures/rc_document_announcement_sequences_v1.json`


La qualification couvre l’assemblage natif démontré et ses refus. Elle ne prouve pas une analyse complète de DCE réel, une validation métier humaine, l’admission A1 ni un GO public. Les cinq occurrences résiduelles restent des omissions de calibration lexicales, pas des preuves de pièces absentes. Le plan, sa case, son journal et l’index sont actualisés avec une seule tranche active.

Prochaine étape : R4 — corriger et qualifier les cinq omissions résiduelles de la calibration RC (tableau, titre répété et en-tête avec portée lot), avec ancres source/région exactes et refus des ambiguïtés; préserver UNKNOWN, A1 non admis, A2 générique HOLD et NO-GO public.

Miroir Basic Memory `smart-ao-v8` synchronisé puis relu : 2727/2727, cinq omissions non qualifiées et prochaine étape exacte vérifiés. Le plan demeure l’unique autorité de statut.
