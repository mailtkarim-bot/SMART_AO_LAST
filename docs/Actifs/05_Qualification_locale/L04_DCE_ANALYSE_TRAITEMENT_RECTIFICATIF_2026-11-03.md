# L04 — DCE applicable, analyse et traitement humain après rectificatif

Statut exclusivement dans le plan global ; preuves et limites bornées ci-dessous.

AS-IS : synthèse12axes, sources/extraits exacts, traitements humains, préparation/revue et historique existent. L03 livre l’admission et le remplacement explicites. Le raccordement actuel de la synthèse peut conserver une lecture CURRENT pendant l’incertitude d’admission ; la chaîne reçue→classifiée→analysée→traitée reste à requalifier sur le nouveau parcours.

RISQUES : afficher un ancien contexte comme courant, relire pendant UNKNOWN, transférer un traitement/revue à V2, confondre axes vides et risque absent ou analyse terminée.

POINTS D’INSERTION : raccords App/CaseAnalysisSummaryPanel et gardes de lecture existants ; pipeline natif, actes et lecteurs existants. Aucun moteur, migration, candidat ou nouvelle porte prévu.

PLAN MINIMAL : rouges sur cache et actes pendant admission inconnue ; suspendre la synthèse et ses actions dans ce contexte ; recette de réception native,12axes et actes humains, puis vrai rectificatif et nouvelles sources/consentements ; qualifier refus/retry/historique ; contrôles, revue et navigateur locaux.

TESTS : contexte/tenant/rôle, sources et hash exacts,12axes dont non évalués, UNKNOWN motivé, traitement humain et revue exacte, source remplacée/acte obsolète, retry identique et nouveaux accords distincts sous V2.

## Fonctions livrées et vérifiées

- Le raccord App neutralise la version de synthèse pendant pending/busy de l’admission DCE ; la clé du cache est invalidée. Le panneau suspend synthèse, traitements et historique avant de rendre des sources ou commandes. Les hooks restent inconditionnels et les anciens intents restent conservés dans leurs registres.
- Un traitement UNKNOWN qui n’appartient plus aux points/source-contextes affichés est rendu séparément comme acte antérieur reprenable ; il ne bloque plus V2 sans offrir son retry. Aucun formulaire courant n’est dupliqué pour le même point sous un autre contexte. Le reçu retrouvé est annoncé comme historique, sans accord transféré.
- Après un reçu ou409, la déclaration de point exige une nouvelle confirmation. Après résolution d’un ancien acte de dossier sous une autre empreinte, ses notes/actions et justification ne deviennent pas les valeurs du dossier courant : douze axes UNKNOWN sont reconstruits, avec consentement neuf. La reconstruction après une revue invalidée était déjà protégée par le garde CURRENT ; sa régression positive est ajoutée.
- Réception, classification, analyse, matérialisation, traitements, préparation/revue et historique natifs existants sont enchaînés sur un DCE effectivement admis, puis un vrai rectificatif. Aucun nouvel analyseur, candidat, contrat métier, migration ou porte ajouté.

Code de production : `web/src/app/App.tsx`, `web/src/features/dce/CaseAnalysisSummaryPanel.tsx`, `AnalysisAssessmentForm.tsx`, `AnalysisDossierForm.tsx`. Tests correspondants, nouveau `backend/tests/api/test_l04_received_analysis_rectification.py`, helpers `tests/api/test_dce_authenticated_api.py` et `tests/support/l03_dce.py`. Les options d’horloge/date restent propres aux fixtures et conservent leurs valeurs historiques par défaut ; aucune règle d’authentification de production n’est modifiée.

## Preuves

Racine privée locale : `/home/noor/.local/share/smartao-proofs/l04-dce-analysis-20261103/`.

**Backend : 90 réussis /60,54 s**, routes analyse, règles d’actes et dossiers, persistance/source/history, réception authentifiée, inventaire rectifié L03 et ancien pipeline L04 d’exécution. Après précision de typage UUID dans le nouveau test, recette native rejouée seule : **1 réussi /7,11 s**. L’ancien corpus d’exécution apporte des cas supplémentaires ; le nouveau parcours reçu contient un point de candidature sourcé par version, pas un fait sur chacun des douze axes.

La recette nouvelle traverse staging/upload, hash des octets, admission et rattachement V1, classification/analyse/matérialisation réelles. Elle retrouve12axes uniques, les axes vides NON_EVALUATED et les pièces non lues. Chaque point a son extrait exact, document/version/hash/locator et un traitement humain UNKNOWN motivé (applicabilité, conséquences, échéance), action et responsable SELF. Replay des mêmes corps sans doublon ; préparation puis revue par actes distincts. Le vrai remplacement invalide sources/revue V1 ; un nouvel acte sur l’ancien contexte est refusé409. V2 reçoit de nouveaux IDs, aucune évaluation humaine héritée, puis nouveaux traitements/préparation/revue. Au final : deux évaluations uniques, quatre actes de dossier, historique des deux versions, analysis_complete=False. Tenant étranger404 et Collaborateur403, y compris replay d’un ancien corps, sont exercés.

**Frontend ciblé : 58 réussis /16,79 s**, formulaires de point/dossier, synthèse et hook ; **2 régressions App/panneau réussies /13,09 s** après rouges. Rouges observés : cache V1 visible sous admission UNKNOWN, rendu de synthèse malgré blocage, retry orphelin absent sous V2, notes V1 conservées après reçu historique, consentement de point encore coché après succès. Les nouveaux contrôles de reprise sont ensuite observés verts. Le résultat Web global final est ajouté après sa fin.

**Navigateur local :** composants et client API de production, Chrome DevTools MCP isolé/headless, vraies routes TestClient/PostgreSQL de fixture, JWT hors navigateur. Un point traité V1, réponse native201 masquée503 puis retry200 de corps/IDs identiques, sans GET entre UNKNOWN et reçu. Douze notes/actions UNKNOWN et consentements distincts pour préparationr1 puis revuer2. Réception de V2 par le contrôleur de qualification utilisant les mêmes routes natives, traitement différent et champs vides/non confirmés sous V2, puis préparationr3/revuer4. Final natif : deux évaluations, quatre actes de dossier, aucune analyse complète déduite. La réception V2 est ici pilotée par le harnais, pas un nouveau contrôle de production ; le geste multi-fichiers L03 n’est pas revendiqué une seconde fois.

Captures bureau1280/mobile émulé393 inspectées, aucun débordement du document ; la table métier reste horizontalement défilante et les champs exacts restent accessibles dans sa région. Version/source V2 et limites sont visibles. Cookies/localStorage/sessionStorage vides, ressources de page externes absentes ; pas une garantie de trafic OS nul. Une première tentative avait préparé le dossier mais omettait la justification fraîche de la revue : refus UI correct, tentative non concluante. La reprise a relu l’état préparé et envoyé seulement la revue manquante, puis V2 ; aucune mutation connue n’a été rejouée à l’aveugle.

Les premières erreurs de montage sont distinguées des défauts produit : session de fixture d’août correctement refusée403, puis alignement date/horloge de fixture ; une substitution trop large et une horloge non transmise ont été détectées par contraintes SQL/Ruff, corrigées sans abaisser ces gardes. Seules les fabriques de tests sont paramétrées. Un sélecteur de navigation ambigu et une référence DOM de scroll JSDOM ont été corrigés ; les assertions de cache/panneau ont bien échoué avant changement métier.

Types/lint/build finaux vérifiés ; avertissements préexistants setDecisionDossier et chunk>500kB. Mypy app/tests : **206 diagnostics dans40 fichiers /1265 sources**, identités normalisées identiques à L03, aucune nouvelle dette ; les708 sources applicatives restent sans erreur. Ruff/format ciblés et revue du delta contre WIP conservé, non HEAD seul. Scan final et Web global consignés ci-dessous.

## Limites et garanties

L04 général PARTIAL. Douze axes affichés et revus ne signifient pas douze axes automatiquement interprétés : axes sans fait/revue, applicability et conséquences restent UNKNOWN/NON_EVALUATED. Aucun zéro financier, absence de risque ou calcul juridique n’est déduit. La recette reçue est bornée à un point natif par version et ne prouve pas tous PDF/OCR/tableaux/plans ou une extraction exhaustive.

Scanner CLEAN de fixture, MIME natif, traitements techniques pilotés localement ; aucune qualification de ClamAV réel, livraison d’outbox/worker déployé ou exploitation réelle. L’authentification UI humaine complète n’est pas testée : session synthétique MFA fraîche et gardes serveur réels. Aucun Playwright MCP disponible. La preuve navigateur couvre le harnais des composants analyse ; le raccord App est couvert par sa régression et la suite Web. Les intents vivent en mémoire de l’application : pas de reprise garantie après reload/perte de session. Aucun gel universel des autres modules métier n’est déduit.

Isolation tenant/Patron, MFA, source/version/hash/locator, append-only et actes humains distincts conservés. A1 non admis, A2 HOLD, B0/B1/B2/P0–P7 et NO-GO public inchangés. Aucun corpus réel, live, VPS, dépôt externe, commit, push ou effet externe. Bases propres et ressources de qualification fermées après retour à0 table métier/0 version Alembic ; services utilisateur préservés.

Méthode : Superpowers using-superpowers/brainstorming/writing-plans/TDD/requesting-code-review et ECC product-capability/verification-loop. Revues indépendantes statiques du cache, scopes, orphelins et consentements sans finding bloquant ; pas une validation humaine. OpenDesign Local : catalogue courant, artefact C08 et système consultés ; identité existante conservée. Impeccable craft-floor et contexte déjà établis dans la session, contrôle borné sur les composants. Graphify interrogé avant navigation manuelle ; Basic Memory miroir du plan. Serena sans navigation sémantique, Context7 sans nouvelle API externe à inférer, Jev/Manus/GitHub non nécessaires à ce travail local vérifiable.

## Vérification finale — 04/11/2026

**92 fichiers Web réussis, 763 tests réussis /4 ignorés, 105,50 s**. Un global précédent762/1 a révélé la lecture automatique avant matérialisation de la projection d’Affaire (identifiant sélectionné déjà connu, hook pending pas encore restauré). Le garde exige désormais que la projection corresponde à l’ID sélectionné ; deux scénarios App rejoués ensemble sont verts, puis ce global final. Les sources sont restées figées pendant cette dernière passe. Le changement App de sélection ne fait pas partie du harnais navigateur ; il est couvert par la régression et le global.

Semgrep1.183.0, `p/security-audit`, métriques désactivées et `--no-git-ignore` : **99 règles sur11 fichiers, 0 finding, 0 erreur**, sur le delta final. Aucun envoi de résultats ; pas une certification sécurité. Impeccable detector : aucun constat sur les trois composants modifiés. Types, lint, build, format ciblé, revue du delta et `git diff --check` verts, avertissements préexistants conservés. Identités de la dette mypy206/40 inchangées. Aucun motif de secret ajouté détecté dans le delta.

Le dossier a été ouvert le03/11 et sa vérification achevée le04/11 ; le plan seul porte le statut et la suite.
