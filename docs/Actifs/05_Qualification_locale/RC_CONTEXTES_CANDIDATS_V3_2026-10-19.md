# Intentions RC — contextes candidats v3 — 19/10/2026

## AS-IS / risques / insertion

Checkout principal codex/reconcile-smartao-20261009/HEAD30f2693,WIP conservé. Les20hashes v2 et les preuves v1 restent immuables. V2 :14omissions liées aux préambules/compléments ;ce diagnostic de famille seul guide un développement distinct,aucun ancien challenge utilisé pour régler un moteur.

Adaptateur v3 isolé autour du reconnaisseur v2 gelé,avec ancres de tous les contextes certifiés neutres et correspondance byte/positions source. Une vue grammaticale interne peut neutraliser ces régions,mais la requête brute et toutes les preuves originales restent conservées ;aucune requête réécrite vers retrieval/encodeur. Refus financier avant toute analyse sur la requête entière. Aucune dépendance/schéma/profil/API/UI/factory modifié.

Risques :suppression d’autre sujet/demande,négation/condition/portée,ancre décalée par accents,contexte inconnu présumé neutre. Contrat v3 prospectif :liste de grammaires neutres bornées,preuve séparée,refus et raisons clarifiés,aucune applicabilité déduite.

## Plan minimal et preuves attendues

- [x] Développement distinct et rouges :préfixe/suffixe/combinaison,accents/offsets,contexte chargé/inconnu,financier,référence,raisons et préservation v2.
- [x] Contrat prospectif et nouveau challenge indépendant relu sans accès candidat/développement ;scellé avant gel.
- [x] Adaptateur minimal et banc :contextes exacts/intégrité/promotions séparés,revue contradictoire et correctifs testés.
- [x] Tests/scans puis gel et qualification indépendante sans réglage après mesure ;référencev2 sur le même nouveau jeu si utile,aucune comparaison entre jeux différents.
- [x] Suivi/plan/index/mémoire autorisée,aucun branchement ni activation.

A1nonadmis/A2HOLD/NO-GOpublic,DPGFnonévaluable ;v7/v8/v9/v10/v1/v2 préservés. Aucun live/corpus réel/SQL/E5/VPS/P3/déploiement/commit/push.

## Qualification locale d’intention acquise sur le périmètre testé

V3 contextuelle isolée codée autour de v2 gelée :qualification bornée des préambules/suffixes de préparation,preuve séparée de chaque région consommée,vue grammaticale interne sans changement des positions caractères,recalage de tous les offsets UTF8 sur le texte original et SHA original conservé. Aucun texte réécrit vers retrieval/encodeur. Contextes inconnus/chargés non certifiés,portée légitime brute conservée sans neutralisation;gardefinancièresurqueryentièreavantcore. Enveloppe de sortie fermée :types/enums,sujet/cue,matrice état/demande/raison,indice lexical et portée cohérents;erreur/timeout => abstention sans fallback. Raisons d’abstention clarifiées prospectivement. Développement15/15 exacts,71ciblés verts (66application/5CLI),dont20cas de développementv2 conservés,contextes chargés,accents,tirets,chevauchement,fausse preuve et corruption de slots/raison. Revue/contre-revue indépendante a confirmé les corrections de cohérence. Nouveau challenge32cas préparé et relu par deux agents sans accès code/dev/anciens challenges;seules32métadonnées expected_refusal corrigées avant mesure,textes/sémantique/ancres/contextes inchangés. Gel28fichiers avant ouverture consignée puis aucun réglage. V3 sur nouveau jeu :32/32exacts,16/16positives,4/4UNSUPPORTED,5/5AMBIGUOUS,6/6UNKNOWN,1/1financier;32occurrences de contexte exactes (4cas doubles,24simples,4sans). Zéro promotion,ancre invalide,écart d’ancre ou contexte;toutes7gateslocales vraies. Référencev2 sur EXACTEMENTmêmejeu :13/32intentions exactes,0/16positives;preuves de contexte non évaluées parv2. 128appelsv3(32initiaux/96chauds),p95chaud0,115ms contre0,078msv2,donnéesdescriptives intentionseule,pasperformance retrieval. Aucune admission automatique :admittedfalse,moteuractifinchangé,aucunreadsource/encodeur/E5/SQL. Contre-lecture indépendante confirme comptes/ancres/contexte/28hashes etlimites. Backend sansDB2656réussites/846désélectionnés/1warning38,64s;Ruff/format4/mypy637/diff verts. Semgrep1.179.0/225règles/4Python0finding/0erreurJSON;detect-secrets49SHA de provenance publique triés exactement,baseline/filtres non modifiés. V1/V2 et anciennes politiques inchangés;aucun backend live/corpus réel/VPS/P3/déploiement/commit/push;HEAD30f2693/WIP conservés,A1nonadmis/A2HOLD/NO-GOpublic,DPGFnonévaluable.

### Fichiers concernés

- `backend/app/modules/knowledge/application/rc_context_intent_v3.py` : adaptateur explicite et preuves de contexte, aucun branchement au logiciel actif.
- `scripts/qualify_rc_intent_recognition_v3.py` : banc d’intention, gates de contexte distinctes de celles des composantes, répétitions et gel obligatoire avant scellé.
- `backend/tests/application/test_rc_context_intent_v3.py`, `backend/tests/ops/test_rc_intent_recognition_qualification_v3.py` : preuves reproductibles.
- Contrat, développement, challenge et protocole v3 sous `backend/tests/fixtures/knowledge/` :`rc_intent_context_contract_v3.json`, `rc_intent_development_context_v3.json`, `rc_intent_independent_challenge_v3.sealed.json`, `rc_intent_independent_qualification_protocol_v3.json`.

### Ce que prouve la vue grammaticale

Elle n’est pas une nouvelle requête destinée au moteur. Chaque contexte reconnu est conservé dans `context_evidence`, avec délimiteurs/espaces exacts. Seules ces régions prouvées sont neutralisées pour l’analyse grammaticale. Les ancres retournées par le core sont converties depuis les positions caractères de cette vue vers les octets du texte original ;une intersection ou discordance entraîne UNKNOWN/INVALID_RECOGNIZER_OUTPUT. Les tests accents/tiret long, faux extrait, champ manquant, booléen de lot, mauvais enum et incohérence sujet/demande/raison rendent ces refus observables.

Un préambule de lot correctement interprété par le core n’est pas neutralisé :sa portée et son ancre restent celles de la requête brute. La détection financière couvre toute la requête, y compris les contextes potentiels. UNKNOWN reste la règle sur toute preuve absente ;COVERED décrit le sens de la question, pas la réponse métier.

### Qualification indépendante et référence

Auteur et second relecteur ont utilisé les seuls contrats prospectifs, sans lecture du candidat, du développement ni d’anciens challenges. Les31booléens de refus non financiers ont été remplacés par null et le booléen financier par son code, avant toute mesure. Original et hash conservés hors dépôt ;aucune correction sémantique ou de texte après observation.

SHA final du challenge : `96aedd3f1a6c259dbe33e19d9d7b6398482ea4e4bde509c4df1658c661d89f6d`. Le gel28fichiers inclut les20fichiers de preuvev2, eux-mêmes incluantv1. Les deux rapports utilisent le même hash de jeu. La référencev2 n’évalue pas les contextes, et ne sert qu’à comparer intentions/ancres sur ces mêmes entrées ;aucune comparaison avec les résultats v1/v2 sur d’autres jeux n’est faite.

Le challengev3 est maintenant ouvert et historique. Aucun réglage du candidat/gold après mesure. La préparation indépendante et ses contrôles ne démontrent pas une indépendance statistique ou une généralisation à tous les contextes français.

### Limites et invariants

Le lexique de neutralité est volontairement fini :il ne prouve pas que tout complément français soit neutre. Ce succès local ne qualifie ni extraction de PDF, source multi-sujets/tronquée, compréhension générale, retrieval, embeddings, SQL, tenant/permissions/MFA en exécution intégrée, UI ou DCE entier. La nouvelle fonction ne lit aucune source et ne change aucun droit. Les tests d’isolation source existants ne sont pas remplacés par cette preuve d’intention.

846tests DB sont exclus de la campagne actuelle ;aucune nouvelle globale PostgreSQL ni migration. Le warning sansDB est l’avertissement historique Starlette/httpx. Semgrep est limité aux4fichiers Python nouveaux, sans finding ni erreur ;ce n’est pas un audit complet du WIP. Les49signaux de hashes dans les données sont publics/synthétiques et triés en preuve privée, sans modifier baseline ou filtres.

Les profils actifs et v7/v8/v9/v10, les corev1/v2 et les sources restent inchangés. Le candidat est non admis/non activé malgré réussite des gates de ce stage ;A1nonadmis/A2génériqueHOLD/NO-GOpublic etDPGFnonévaluable maintenus.

### Méthode et conservation

Superpowers using-superpowers/cadrage/TDD/revue/vérification et ECC verification-loop. Graphify consulté avant lectures ciblées,graphe insuffisant pour ce nouveau WIP. Pas de navigation sémantique Serena,API/SDK nouveau pour Context7,UI pour OpenDesign/Impeccable,Jev ou Manus nécessaire. Les agents ont servi la préparation/revue technique, sans validation métier humaine.

Preuves privées : `~/.local/share/smartao-proofs/rc-context-v3-20261019/` (révisions du scellé,rouges/verts,développement,challenge/référence,gel28fichiers,ouverture,scans/triage,nonDB et état final). Le miroir Basic Memory reste en attente de l’autorisation explicite précédemment demandée après refus de revue automatique ;résumé minimal local préparé sans texte de cas.

Prochaine étape : ESSAIS DCE — coder un adaptateur expérimental séparé reliant l’intention v3 au retrieval candidat, en conservant la requête brute, ses ancres et les preuves de contexte; qualifier sur PostgreSQL jetable synthétique la provenance exacte, les refus de source, l’invalidation et l’isolation tenant/Affaire, sans modifier ni activer le moteur actif. DPGF non évaluable; UNKNOWN préservé, A1 non admis, A2 générique HOLD et NO-GO public maintenus.
