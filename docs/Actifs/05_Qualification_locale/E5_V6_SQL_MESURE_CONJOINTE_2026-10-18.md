# E5 CPU / v6 / lecteur SQL — mesure conjointe synthétique — 18 octobre 2026

## AS-IS, risques, points d'insertion, plan minimal

HEAD30f2693/WIP préservé; plan/index/autorités v3.1 et sources de preuve précédentes vérifiés. Profilv6/scoreur existants; SQL et modèle ont été mesurés séparément. Aucune factory/route candidate active. Risques : confondre performance et fidélité SQL, gold calé sur omissions connues, condition ou provenance perdue, fuite de scope, mesure CPU tronquée.

Insertion minimale : injection explicite source/encodeur dans le banc existant, orchestrateur de qualification SQL synthétique, jeu8 nouveau. Sources internes cohérentes avec le schéma réel; aucune prétention à stocker une classification privée que le lecteur ne représente pas. DPGF/marge restent refusées par garde de requête.

Budgets fixés avant mesure : modèle CPU2/FP32/L2/threads2,1200MiB sans swap,timeout600s; PostgreSQL CPU1/768MiB/tmpfs512MiB (capacité128MiB insuffisante pendant les tests de migrations, corrigée avant gel et toute mesure E5). Deux conteneurs sans réseau ni port publié, socket Unix local uniquement. 1200MiB est le budget conjoint choisi pour couvrir ORM/SQL en plus d'E5, supérieur au précédent900MiB sans marge; aucune comparaison à enveloppe RAM identique. Seuil dense0.85/profilv6 inchangés. p95chaud≤2000ms et Recall@5≥0.90 conservés du banc; admission jamais automatique, DPGF reste dans le dénominateur brut. Aucun réglage après résultat du jeu8.

- [x] Banc injecté rouge/vert et seed SQL/contrats/invalidations testés sans modèle.
- [x] Geler code/profil/jeu avant mesure réelle; lire gold indépendant sans le transmettre à l'extracteur/encodeur.
- [x] Mesurer référence source synthétique et SQL sur le même jeu8,4répétitions chacune; conserver divergences/omissions/abstentions.
- [x] Vérifier invalidation avec E5 chargé et ancres SQL exactes; coûts RAM/temps et requêtesSQL tracés.
- [x] Suites/contrôles/revue,cleanup dédié,plan/index/BM.

A1nonadmis/A2HOLD/NO-GOpublic;v6nonactivé,aucun corpus réel/backend live/VPS/P3/déploiement/push.

## Clôture locale — mesure exécutée, candidat HOLD

Mesure conjointe E5CPU/v6/SQL exécutée sur jeu8 gelé18sources/16questions,14fragmentscourants/4exclus. Référence et SQL identiques en classements/scores/traces/états/gates;6/6validations SQLvraies,17régions/87preuves/108signaux confrontés aux octets SQL. Rappelmacro@5/@10=81,9444%,7/8positivesévaluables complètes,questiongénérique3/8(cinqomissions),j8-hour2fauxcandidats etDC2unparasiteDPGFadministratif;précisionmicro14/17=82,35%. DPGF/margerefusées,6gatesrouges,HOLD/admittedfalse;aucun réglage après mesure. p95chaud référence21,893ms/SQL44,928ms,froid14,298s/16,559s,RSS999,895/1028,867MiB;plafond1200MiB atteint en référence,marge nonprouvée. SQL112statements mesurés+12validation/946,78ms;déréférencement prouvé,pas remplacement atomique.11testsajoutés/424réussites en15,30s;Ruff/mypy634/format/diff/10SHAverts. Revue corrigeguardTCP/libpq après4rouges;contre-revuecodeetrapports conformes. Semgrep1.179.0/225règles/4fichiers0finding0erreur+1warningfixpoint,secrets1.5.0 zéro finding. PGjetable sansréseau/socketuniquement,capacité128MiBsaturée avantgel→512MiB,testsrejoués;head0136→base/Alembic0final,2mesuresexit0/3conteneursdédiésretirés. Code moteur/profil/factory/API/UI/schéma/dépendances inchangés;seulbancadditif,aucunlive/corpusréel/VPS/P3/déploiement/commit/push. HEAD30f2693/WIPconservés;v6nonactivé,A1nonadmis/A2HOLD/NO-GOpublic.

### Résultats du jeu8

| Mesure | Référence synthétique | Lecteur SQL réel |
|---|---:|---:|
| Rappel macro brut sources/régions @5 et @10 (DPGF incluse) |81,9444%|81,9444%|
| Positives évaluables complètes |7/8|7/8|
| Question générique (sources distinctes) @5 et @10 |3/8|3/8|
| Cas attendus sans candidat mais fautifs |1/7|1/7|
| Vrais/faux retours sources |14/3|14/3|
| Précision micro des sources retournées |82,3529%|82,3529%|
| p95 chaud (48requêtes/3cycles après1er) |21,893ms|44,928ms|
| Premier appel |14,298s|16,559s|
| RSS max du processus |999,895MiB|1028,867MiB|
| Pic cgroup pendant mesure |1200MiB|1001,969MiB|

Les quatre cycles par processus sont stables. La comparaison utilise exactement le même jeu/profil/runtime et budget1200MiB; elle reste descriptive (un seul démarrage froid de chaque,ordre référence puis SQL/cachemachine partagé). RSS et cgroup sont des comptabilités distinctes, non additionnables. Le picPG pendant cette campagne/tests est212,590MiB sous budget768MiB; il n'isole pas la seule phase modèle. Le p95 inclut les refus financiers rapides. Les946,78ms/12statements de validations après mesure sont séparés des112statements et des latences principales. RSSaprèsvalidationinchangé; le pic cgroup enregistré dans le rapport précède ces validations, pas une borne finale de toute la phase.

**Défauts constatés sans tuning :**

- `j8-generic` :5directives médicales/site omises,3/8retrouvées même à@10. Gold8sources pertinent confirmé indépendamment. La complétude@5 était mathématiquement impossible avec8attendus, mais les5omissions@10 montrent aussi un défaut réel de rappel. Ni gold réduit ni top_k augmenté après résultat.
- `j8-hour` :2sources parasites au lieu d'abstention sur « À quelle heure se tient la visite du lot524 ? ».
- `j8-dc2` :clause DPGF administrative remontée enplusduDC2. Cette pièce est INTERNAL_OPERATIONAL et ne contient pas de montant; aucun test ne démontre une fuiteFINANCIAL_PRIVATE. C'est un fauxrappel, à ne pas masquer derrière le7/8de rappelcomplet. La requête DPGF directe et la marge restent refusées/nonévaluables; leur refus n'est pas une analyse DPGF.

Six gates fausses :abstention,critical_complete,evidence_recall_at_5,rc_unknown_refusals,specific_intent_exact,specific_projection_typed. Le manqueUNKNOWN porte sur `j8-generic`. Paires médicales exactes,ancres/proofs/scopes/refus financiers valides. UNKNOWN de réponse reste toujours conservé; pas de complétude métier inférée.

### Modifications et preuves

- `scripts/qualify_candidate_retrieval.py` :injection source/encodeur optionnelle uniquement au banc,source virtuelle et CLI antérieurs par défaut. Aucun changement service/domain/encodeur/SQLreader/profile/factory.
- `scripts/qualify_candidate_sql.py` :orchestrateur synthétique dédié,seeding transactionnel à base vide,sourceSQL réelle et encodeurCPU épinglé,compteurSQL et invalidations sur encode_query réel. Garde avantlecture fixture impose driverpostgresql+psycopg,userproof,database smartao_e5_sql,aucunhost/port,queryexactehost=/socket,flagdisposable1;rejette PGHOSTADDR/PGSERVICE/PGSERVICEFILE. Aucun nouveauendpoint.
- `backend/tests/fixtures/knowledge/btp_e5_sql_heldout_v8.json` :jeu8 nouveau,14sourcescomplètes éligibles+tenantétranger/Affaireétrangère/versionancienne/REVIEW_REQUIRED,16questions avec goldindépendant. Aucune classification privée simulée dans un modèle SQL qui ne la représente pas. Ordinals etpages cohérents entrelesdeuxbancs.
- Tests :`test_candidate_qualification_cli.py`10cas ajoutés(injection,guardenv/URL,fixtureprivée/non synthétique),`test_e5_sql_measurement.py`1cas DBcomposé(seed,texte,source,invalidation). `injection-red.log` rouge observé puisvert; `seed-red-corrected.log` seedabsent avantimplémentation,puisvert; `socket-red.log`4contre-exemplesrouges avantgarde stricte,puis17opsverts.
- `seed-red.log` est une erreur de connexion sandbox corrigée par accès au seul socket; ce n'est pas un défaut produit. `targeted-before-freeze.log`390verts/1échec/30erreurs est nonqualifiant :PGtmpfs128MiBsaturé pendant migrationsrépétées (`postgres-capacity-before.log`),sansOOM. Instance dédiée recréée512MiB avantgel/mesure,`targeted-final.log`424verts/15,30s. Ne pas confondre panne du banc et régressionlogicielle.
- `ruff.log`,`mypy.log`634sources,format4Python etdiffverts;`semgrep.json`/`.log`1.179.0/225règles/4paths/0finding0erreurJSON,1warningfixpoint python.boto3.security.hardcoded-token sur CLI sansappelboto3. Analyse locale,metrics off,pasupload;limite conservée. `secrets.json`1.5.0/0finding sur5fichiers,baseline inchangée.

Répertoire privé :`~/.local/share/smartao-proofs/e5-v6-sql-20261018/`. `code-before-heldout-sha256.txt` :10fichiers gelés/revalidés. SHAjeu8 `29eb7a63c0ad8cc6756fce94c8616f67c41c9f1c505c8711de2b29ac08584c83`. `reference.json`,`sql.json`,`comparison.json`,logs/états exit0 sansOOM,`sql-fragments.json`18fragments et métadonnées synthétiques. Confrontation locale87preuves/108signaux/17régions aux octets/hash/locatorsSQL;contrelecture indépendante confirme égalité et défauts,sans exécutionDB/modèle.

Runtime CPU :image `sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938`,poids/CPUruntime/venv/code readonly,user1000,networknone,tmpfs/tmp64MiB,CPU2/mémoire1200MiB/sansswap/timeout600s. ModèleE5smallrévision614241f622f53c4eeff9890bdc4f31cfecc418b3,manifestes/profil exactsv6,FP32/L2/préfixesquery/passage/threads2;chargements vérifiés par l'encodeur existant. FutureWarning de renommage get_sentence_embedding_dimension conservé,sans changementAPI surcejeu. PGnetworknone/aucunport,CPU1/mémoire768MiB/tmpfsdata512MiB/socketlocalmonté;`containers-final.json` décrit isolation. `upgrade-for-measurement.log` tête20261010_0136,`downgrade-final.log`+`alembic-final.txt`0 aprèsTRUNCATE données synthétiques. Seuls3conteneurs dédiés retirés.

### Limites et suite

Cette passe prouve la fidélité surcejeu du transportSQL au service candidat et l'invalidation d'une extraction/déréférencement de version durant encode_query. Aucun remplacement vers un successeur/rectificatif ni garantie atomique après dernièrelecture;ces limites restent distinctes des testsSQLdéterministes précédents. Pas de relecture blob/PDF,de DCE réel,de qualification droitsMFA/UI,ni suiteglobale backend/Web/couvertureexhaustive. Aucun benchmark de l'indexvectorielSQL actif :v6 utilise sessegmentsenmémoire. Pas de margeRAMgénérale prouvée à1200MiB(atteint enréférence),ni preuve charges128sources. LesgatesrestentHOLD,aucuneadmission/activation. Lespreuvesjeu7(10/10évaluables,0/8faux) ne généralisent pas aujeu8;lesrésultatsactuelspriment pourlesdéfautsobservés.

Méthode :Superpowers using-superpowers/cadrage/planTDD/revue/verification,systematic-debugging pourlesproblèmesdu banc;ECCverification-loop. Graphifyconsulté,Serena disponible via activation précédente,BasicMemorymiroir;Context7sansobjet(pasnouveaufournisseur/API externe),Jev/Manusnonnécessaires,OpenDesign/Impeccablesansobjet(aucunvisuel).

Prochaine étape : ESSAIS DCE — reproduire sur cas de développement les omissions des visites qualifiées dans les questions génériques, le défaut d’abstention sur l’heure de visite et le faux rappel DPGF sur DC2; corriger les causes avec preuves typées et UNKNOWN, puis requalifier sur un nouveau jeu synthétique gelé sans activer le candidat. DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
