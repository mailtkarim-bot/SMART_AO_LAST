# Visites génériques, abstention et preuve RC — candidat v7 — 18 octobre 2026

## AS-IS, risques, insertion, plan minimal

Checkout principal codex/reconcile-smartao-20261009,HEAD30f2693/WIP préservé. Index/plan et autorités v3.1 lus; UNKNOWN/provenance source/version/hash/localisateur et CT2-083 restent impératifs. Jeu8historique :5omissionsgénériques,2fauxretoursheure,1parasiteDPGFadministratif surDC2. Aucun tuning du jeu8 pendant sa mesure.

Risques : perdre négation/condition/citation, inférerun type ouuneportée, élargirdroits, modifier silencieusementv6. Insertion minimale : nouvellepolitique rc-subject-proof-v7 opt-in,profils1–6préservés; utiliserpreuvev6 etdirectiveRCindépendante pourlesformesbornées dequestionsgénériques etDC2. Rejeterquestionsvisitehoraire/date/lieunonprouvées etrequêtesRCambiguës. Aucunmoteuractif/factory/API/UI/schéma/dépendance remplacé.

- [x] Reproduirelesdéfauts surdéveloppement avantcode;correctionminimalepuisrouges complémentaires/vert.
- [x] Projections ettraces typées,conditions/quotes/scopes/budgets/retries et anciensprofils;revueindépendante.
- [x] Nouveaujeu9goldindépendant,gelcode/profil/jeu;E5CPUréel+lecteurSQLisolésansréseau,1200MiB/CPU2/600s,PG768MiB/CPU1/tmpfs512MiB.
- [x] Suitespertinentes,lint/types/format/diff/secrets/Semgrep;cleanupdédié etjournal/case/index/BM.

A1nonadmis/A2HOLD/NO-GOpublic;DPGFnonévaluable,v6etv7nonactivés. Lescasdev neconstituent paspreuve degénéralisation. Aucunlive/corpusréel/VPS/P3/déploiement/commit/push.

## Clôture locale — qualification bornée, candidat HOLD

Politique candidate rc-subject-proof-v7 codée sans activation : preuve de directive et sujet pour visites génériques qualifiées/non qualifiées et DC2, refus des questions de visite non prouvées et ambiguïtés RC, conditions/citations/négations/lot/UNKNOWN conservés. V1–v6 et identité v6 préservés. 21 tests ajoutés, 445 knowledge/candidat/SQL/architecture réussis en16,75s; 2 SQL finaux verts. Rouges : 8/9 initiaux v6, CLI, 2 ambiguïtés denses, segment mixte et ancre de validation SQL; contre-revue code et rapport sans blocage. Jeu9 gelé18sources/20questions : E5CPUv7+SQL 8/8 positives évaluables complètes,5/5 visites génériques,0 faux retour sur11 cas sans candidat,15 couples query/source pertinents/0parasite; v6 témoin7/8,0/5 génériques,10pertinents/36parasites. Rappel brut@5/@10=88,89%, deux gates rouges DPGF annoncées avant mesure; admitted=false/HOLD. V7p95chaud38,239ms,froid15,062s,RSS875,328MiB,cgroup938,980MiB sous budget1200;6/6validationsSQL,144statements+12validation.15régions/81preuves/95signaux confrontés aux octetsSQL,15SHA pré/post mesure verts,aucun réglage après résultat. Ruff/mypy634/format/diff verts;Semgrep1.179.0/225règles/10fichiers0finding0erreurJSON+2warningsfixpoint;secrets0nouveau nontrié/3checksums publics v7 précisément triés,sans filtre/staging. PGjetable sans réseau/socket Unix,head0136→base/Alembic0,2mesures exit0 sansOOM/3conteneurs dédiés retirés. Segment DC2 mixte conserve DPGF brut et évidence hors projection REQUIRED/ASSERTION mais directiveUNKNOWN; pas absence totale de parsing DPGF ni effet financier. Aucun schéma/factory/API/UI/encodeur actif/dépendance/commit/push/live/corpus réel/VPS/P3/déploiement/GOpublic;HEAD30f2693/WIP conservés. Généralisation,atomicité et DCEentiers non qualifiés;A1nonadmis/A2HOLD.

### Ce qui a été codé

- `rc_recall.py` ajoute une lecture bornée de la question d'obligation avec suffixe lot. Une requête RC hors grammaire contenant DC1/DC2/mémoire/variantes reste `UNKNOWN`; aucun lot n'est inventé. `rc_specific_intent.py` dispose d'un mode strict réservé à v7 : une question de visite horaire/date/lieu ou conditionnelle non reconnue ne peut plus retomber sur le dense. Le mode par défaut de v6 est conservé.
- `rc_candidate_conflicts.py` généralise additivement la preuve de directive aux sujets RC non financiers couverts, indépendamment de la valeur normalisée. La source complète doit correspondre au hash et aux octets du segment. Une condition amont ou aval conserve valeur et nature `UNKNOWN`; citations et fragments tronqués restent refusés. Les marqueurs de condition ne constituent pas une preuve d'applicabilité.
- `candidate_retrieval.py` applique le même filtre de preuve au dense et au secours typé. La famille générique VISIT peut contenir VISIT_MEDICAL, VISIT_SITE et VISIT non qualifié, sans convertir une visite non qualifiée en site. DC2 exige une clause DC2 du lot demandé si sa portée est prouvée. Fenêtre50/top_k, score positif et seuil0.85 restent inchangés; candidats non retenus TOP_K_LIMIT, refus tracés.
- `embedding_profile.py` et `profile-v7.json` ajoutent une identité opt-in, sans remplacer v6. `qualify_candidate_retrieval.py` sérialise et vérifie les preuves de v7, y compris sujets génériques et DC2. `qualify_candidate_sql.py` choisit sa sonde d'invalidation par visite de site qualifiée, mono-source et lot explicite, plutôt que par ID d'un ancien jeu.
- Tests : `test_rc_subject_retrieval.py` (19 cas), un test CLI et un test SQL supplémentaires. Le test SQL du banc a aussi été modifié pour prouver son indépendance à l'ID de question. Aucun endpoint, UI, migration, dépendance ou factory ajouté.

### Preuves de développement et contrôles

Répertoire privé : `~/.local/share/smartao-proofs/rc-subject-v7-20261018/`.

- `development-red.log` : 8 échecs attendus et1réussite sur v6, couvrant les trois défauts. `development-green.log` contient aussi une erreur syntaxique intermédiaire corrigée avant tout gel; les preuves finales ne la présentent pas comme une régression produit. `ambiguous-red.log` :2rouges, `mixed-red.log` :1rouge, `cli-red.log` :1rouge; tous corrigés avant mesure. `validation-anchor-red.log` : StopIteration reproduit quand la question SQL est renommée, puis correction et test vert.
- `targeted-final.log` :445réussites/16,75s, périmètre candidat/RC/knowledge/worker/benchmark/encodeur/CLI/SQL/fraîcheur/architecture. `sql-final.log` :2réussites/3,88s après mise en forme finale des imports de test; `cli-final.log` :test CLIv7 vert. Aucun test de production supprimé ou rendu moins strict.
- `ruff.log`, `mypy.log` :lint backend/scripts et634sources; formatage10Python, `git diff --check`. `semgrep.json`/`.log` :1.179.0/225règles/10paths/0finding/0erreurJSON,2timeouts fixpoint de la règle boto3 hardcoded-token (projecteur etCLI, sans appelboto3). Metrics off,analyse locale,pas d'upload des résultats; limite d'analyse conservée.
- `secrets-scan.json`, `secrets-triage.json`, `baseline-before.json` :3checksums publics identiques au profilv6 ajoutés précisément sous le cheminv7,0nouveau nontrié; autres résultats/plugins/filtres de baseline inchangés. Aucun staging/commit ni hook de livraison qualifié.
- `code-before-heldout-sha256.txt` :15fichiers gelés avant modèle et revalidés après. SHA du jeu9 : `b193cd188120152e68706f275f96461f83848eca38fa7f0b5aed2e2de869240d`. Profilv7 : `candidate-e5-v1:e6b28ff4585e5d3b5e00736c94414bddfb39dc0e7b9ba71f41f03084f08a7470`. `profile-identities.json` confirme notamment v6 inchangé à `candidate-e5-v1:c6bdb66f1a1a057cc85aadb157c14f7ed62d34148318eaa41cf422c60ad50083`.

### Jeu9 et mesure réelle

18 sources :14 courantes complètes et4 exclusions réelles (tenant,Affaire,ancienneversion,REVIEW_REQUIRED).20questions,8positives évaluables et1positive DPGF refusée;11cas attendus sans candidat dont marge refusée. Gold relu indépendamment avant mesure, sans passage des attentes au parseur/encodeur. Jeu synthétique nouveau mais proche des familles de développement : généralisation bornée.

| Mesure sur jeu9 | V6 témoin, source virtuelle | V7, lecteur SQL réel |
|---|---:|---:|
| Positives évaluables complètes @5 |7/8|8/8|
| Sources de visite générique retrouvées @5/@10 |0/5|5/5|
| Cas sans candidat mais avec parasites |6/11|0/11|
| Couples query/source pertinents / parasites |10/36|15/0|
| Rappel macro brut @5/@10, DPGF incluse |77,7778%|88,8889%|
| p95 chaud |24,772ms|38,239ms|
| Premier appel |15,101s|15,062s|
| RSS max |878,156MiB|875,328MiB|
| Pic cgroup pendant mesure |917,887MiB|938,980MiB|

Quatre répétitions stables par processus;60requêtes chaudes, refus rapides compris. La qualité est comparée au même gold; les temps ne mesurent pas isolément l'effet de v7 car le témoin utilise la source virtuelle et v7 SQL. Deux processus successifs sur la même machine avec cache partagé, pas une estimation statistique générale. Aucune remise en cause des résultats historiques du jeu8, aucun ajustement après ceux du jeu9.

`v6-reference.json` et `v7-sql.json`, états/logs, `verification.json`, `sql-fragments.json` et `containers-final.json` permettent le rejeu/audit. V7 :15régions,81évidences et95signaux relus contre les octets/hash/locators SQL; contre-lecture indépendante confirme ces résultats et46régions du témoin,270tracesv7,refus et6/6validations SQL. Les270traces sont des observations répétées par question, pas270sources.

Le SQL compte144statements pour la mesure principale,12pour les validations complémentaires (754,00ms). Déréférencement et extraction devenue inéligible pendant encode_query prouvés, aucune atomicité après dernière lecture ni remplacement vers un successeur revendiqué. RSS aprèsvalidation inchangé; piccgroup du rapport pris avant ces validations.

CPU :image locale `sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938`,E5small/révision/manifestes et runtimeCPU épinglés inchangés,FP32/L2/préfixesquery-passage/threads2,CPU2/1200MiB/sansswap/600s. Code/poids/runtime readonly,user1000,networknone,tmpfs/tmp64MiB. PG :CPU1/768MiB/tmpfsdata512MiB,networknone,socketUnixseul/aucunportpublié. Aucun environnement actif modifié ni téléchargement modèle. FutureWarning de renommage de get_sentence_embedding_dimension conservé. Upgrade tête20261010_0136,downgradebase/Alembic0 final;2mesures exit0 sansOOM et3conteneurs dédiés retirés.

### Décision et limites

Deux gates demeurent fausses : `critical_complete` et `evidence_recall_at_5`. DPGF est au dénominateur brut mais reste refusée/nonévaluable. Le plafond8/9=88,89% avait été indiqué avant mesure; seuil90% et gold n'ont pas été abaissés. Toutes les autres gates et les six contrôles SQL sont vrais; cela n'autorise aucune admission automatique.

Le segment DC2 mixte contient encore la clause DPGF brute. Sa projection hors du sujet demandé peut garder `value=REQUIRED`, `kind=ASSERTION`, avec `directive_signal=UNKNOWN`. Ce n'est ni une absence totale de parsing DPGF ni une qualification financière. La requête DPGF est refusée avant lecteur/encodeur; aucune source privée réelle n'est utilisée. La précision mesurée au niveau query/source ne prouve pas une précision de toutes les clauses dans un segment.

Grammaire finie et conservatrice,conditions complètes parfois hors segment,portée absente conservéeUNKNOWN,top50/top_k etbudget128sources inchangés. Aucune analyse DCE entier/corpus réel,aucun GO ni effet métier,aucune validation humaine remplacée. Pas de nouvelle suite globale backend/Web,couverture exhaustive,preuve multithread ou audit sécurité global. Pics sous1200MiB surcejeu seulement; le jeu8 avait atteint le plafond et aucune marge RAM générale n'est acquise.

Méthode :Superpowers using-superpowers/cadrage/plan/TDD/diagnostic/revue/vérification;ECC ai-regression-testing etverification-loop. Graphify consulté,Serena activé,BasicMemory miroir. Context7 sans objet (pas nouvelle API/fournisseur),Jev/Manus non nécessaires,OpenDesign/Impeccable sans objet (aucun visuel).

Prochaine étape : ESSAIS DCE — éprouver v7 sur des paraphrases RC indépendantes et des fragments multi-exigences, mesurer omissions et faux rappels par type de question et au niveau des clauses, puis expliciter les limites de couverture; conserver UNKNOWN, les sources et l’abstention hors preuve, sans activer le candidat. DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
