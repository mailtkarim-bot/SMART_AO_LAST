# V7 — paraphrases RC et clauses mixtes — 18 octobre 2026

## AS-IS, risques, insertion et plan minimal

Checkout principal codex/reconcile-smartao-20261009, HEAD30f2693, WIP conservé. Index/plan/autorités v3.1 relus : provenance exacte, UNKNOWN et séparation preuve technique/validation métier. V7 est non activé, qualifié seulement sur les familles du jeu9. Le moteur ne sera pas modifié dans cette tranche.

Risque : confondre pertinence d'un fragment, bonne projection des clauses et résolution effective; confondre abstention prudente avec couverture métier complète. Insertion minimale : nouveau jeu10 annoté indépendamment et scoreur pur, après exécution du banc E5/SQL existant. Les annotations ne sont jamais transmises au moteur. Les clauses gardées hors projection ne sont pas comptées comme affirmations de réponse.

- [x] Scoreur rouge/vert : omission, contexte, UNKNOWN, sur-certitude, vraie projection parasite, identité et ancres.
- [x] Relire le gold (paraphrases naturelles, source impérative, négations, conditions locales, lots et segments mixtes); geler jeu/code/profil avant E5.
- [x] Mesurer v7 inchangé avec E5 CPU réel/lecteur SQL et scorer par famille et clause, en conservant tous les échecs.
- [x] Contrôles/revue; nettoyage du seul PostgreSQL dédié, mise à jour plan/case/journal/index et Basic Memory.

Budgets fixés : modèle CPU2/1200MiB/sansswap/600s, PG CPU1/768MiB/tmpfs512MiB, conteneurs networknone et socket Unix seul. V7, seuil0.85, top50/top_k inchangés. Aucun tuning du jeu10 après mesure. DPGF non évaluable; A1 non admis/A2 HOLD/NO-GO public; aucun backend live/corpus réel/VPS/P3/déploiement/commit/push.

## Clôture locale — couverture insuffisante, HOLD

Qualification v7 inchangé sur jeu10 synthétique gelé :16sources/34questions/21annotations,26positives évaluables.11/26questions complètes,rappel source brut43,70% DPGFincluse;15retours source pertinents/0parasite et0/7cas attendus sans candidat(margeincluse).43couples question–clause attendus(15annotations distinctes) :17détectés contexteinclus,14projetés pertinents,26omissions;0extra projeté/valeurconnue fausse/typeconnu faux/surcertitude,20contextes nonpertinents,2occurrences de la même clause médicale841 laisséesUNKNOWN. Paraphrases dequestions0/20clauses,formulationssources0/3,demande multiple0/2 :couverture insuffisante,aucune complétudeDCE. Scoreur pur codé avec12tests nouveaux;382tests pertinents verts/2,50s,puis12/12 recontrôlés aprèsreprise;Ruff/mypy635/format/diff et13SHA verts,anciens15SHA v7 inchangés. Gold et compteurs revus indépendamment avant/aprèsmesure,aucun réglage aprèsrésultat. E5CPUv7+SQL p9536,734ms,froid15,228s,RSS908,328MiB,cgroup986,723MiB sousbudget1200;6/6contrôlesSQL vrais,256statements+12validation.6gatesrouges/HOLD/admittedfalse;DPGF/marge nonévaluables. Semgrep1.179.0/225règles/2fichiers0finding0erreurJSON sanswarning spécifique,secrets1.5.0 zérofinding,baselineinchangée. PGjetable réseauabsent/socketUnix,head0136→base/Alembic0,modèleexit0 sansOOM/deuxconteneurs dédiésretirés. Nettoyage initial arrêté par échec technique de revue automatique faute de crédits; aucune exécution refusée contournée,repris normalement aprèscontinue. Aucun changement moteur/profil/encodeur/factory/API/UI/schéma/dépendance/commit/push/live/corpus réel/VPS/P3/déploiement;HEAD30f2693/WIP conservés. A1nonadmis/A2HOLD/NO-GOpublic.

### Résultats : distinguer sortie prudente et couverture métier

| Mesure | Résultat |
|---|---:|
| Questions positives évaluables avec tous leurs fragments |11/26|
| Rappel macro source @5 et @10, brut avec DPGF refusée |43,7037%|
| Retours pertinents / parasites au niveau question–source |15/0|
| Cas attendus sans candidat mais recevant un résultat |0/7, marge refusée incluse|
| Détection des couples question–clause pertinents, contexte inclus |17/43 (39,5349%)|
| Couples pertinents effectivement projetés |14/43|
| Couples question–clause manquants |26|
| Candidats supplémentaires projetés / assertions connues supplémentaires |0/0|
| Valeurs connues fausses / types connus faux / surcertitudes |0/0/0|
| Occurrences de clauses hors sujet conservées comme contexte |20|
| Occurrences pertinentes laissées UNKNOWN malgré gold connu |2|

Les43occurrences attendues sont15annotations distinctes interrogées sous plusieurs formulations. Les deux UNKNOWN concernent la même clause médicale du lot841, dans la question classique puis générique : ce ne sont pas deux clauses différentes. Aucun compteur de précision ne compense les26omissions. Les20contextes restent hors projection; ce ne sont pas20affirmations fausses. Les types connus mesurés sont ASSERTION/NEGATION/RECTIFICATION; une valeur ou nature inconnue n'est pas classée artificiellement comme fausse certitude.

| Famille | Questions évaluables | Couples attendus | Détectés, contexte inclus | Projetés pertinents |
|---|---:|---:|---:|---:|
| Visites classiques |4|4|4|4|
| Documents classiques |5|6|6|6|
| Conditions, questions classiques |2|2|2|2|
| Générique classique |1|6|5|2|
| Paraphrases de questions (visite/document/générique) |10|20|0|0|
| Formulations sources nouvelles |3|3|0|0|
| Demande de plusieurs exigences |1|2|0|0|

La grammaire restrictive refuse les paraphrases (« faut-il », « doit-il », « nécessaire », « quelles visites… ») au lieu d'inventer une réponse. Cela reste une omission de couverture sur un besoin métier positif. Les formulations sources « une visite est imposée… » et « fournir le DC2 et un mémoire technique » constituent une autre limite du projecteur. Au lot841, la dispense vise explicitement la visite de chantier, mais la politique conservatrice rend aussi la visite médicale UNKNOWN : il faut mesurer cette non-résolution sans la qualifier de fausse affirmation.

Six gates rouges :critical_complete,evidence_recall_at_5,rc_unknown_refusals,review_signals,specific_intent_exact,unexpected_review_signals. Le garde financier et les ancres passent; cela n'admet ni le candidat ni le corpus. DPGF et marge sont nonévaluables; la DPGF reste au dénominateur brut du banc historique, mais les deux refus sont exclus du score de clauses.

### Code ajouté et méthode de mesure

- `scripts/score_rc_clauses.py` : scoreur indépendant appliqué après exécution. Il n'appelle jamais le candidat et ne lui transmet pas le gold. Identité exacte du fichier fixture, ancres UTF8, hash fourni, page et version réellement retournés sont vérifiés. Pas de hash manquant reconstruit depuis le gold.
- `backend/tests/ops/test_rc_clause_scoring.py` :12tests du scoreur couvrant omission, contexte, UNKNOWN, surcertitude, vraie projection parasite, nature de négation, rappel projeté distinct, identité/ancres/hash/page/version. Sixrouges initiaux(scoreur absent),quatre rouges de revue et un rouge de hash manquant observés avant correction. Aucun changement du moteur pour faire passer le jeu10.
- `backend/tests/fixtures/knowledge/btp_rc_paraphrases_heldout_v10.json` :16sources (12courantes/4exclusions),34questions et21annotations. Quotes/mentions ne sont pas des obligations attendues. Deux exigences peuvent occuper la même région avec sujets distincts. La question simple et sa paraphrase gardent le même besoin positif, même si v7 s'abstient. Annotations de création synthétique relues techniquement, pas validation humaine métier/A1.

Le scoreur sépare : détection de directives candidates pertinentes dans projection+contexte, pertinence de la projection, clauses hors sujet en contexte, valeurs/natures connues fausses, UNKNOWN non résolu et surcertitude. Les chiffres au niveau fragment restent ceux du banc existant. Les métriques de nature et valeur connues portent sur les candidats projetés; elles ne prétendent pas qualifier chaque phrase du texte brut.

### Preuves reproductibles

Répertoire privé : `~/.local/share/smartao-proofs/rc-paraphrases-v7-20261018/`.

- `scorer-red.log`,`scorer-review-red.log`,`hash-red.log` :rouges avant corrections du banc; `targeted-final.log` :382réussites/2,50s sur scoreur,CLI,candidat/RC/knowledge/benchmark/encodeur/architecture.12/12 rejoués après l'interruption et hashes inchangés. Pas de nouvelle suite globale backend/Web ni reprise des testsDB déterministes antérieurs : moteur etSQLreader inchangés; la composition réelleSQL est mesurée et ses6contrôles sont vrais.
- `ruff.log`,`mypy.log` :lint backend/scripts et635sources;format2nouveauxPython etdiffverts. `semgrep.json`/`.log` :1.179.0/225règlessecurity-audit/2paths/0finding/0erreurJSON,aucunwarning spécifique. Metrics off,analyse locale sans upload. `secrets.json` :1.5.0/0finding sur3fichiers,aucune édition baseline/filtre/staging.
- `v7-unchanged.log` :15SHA de la tranche précédente encore identiques. `code-before-heldout-sha256.txt` :13fichiers gelés avant mesure/revalidés après reprise. SHAjeu10 :`ec2236c0797e9a77a085ec54d330e9f7afe7dabb1f8d112eb5bbf8239f790091`. Profil inchangé :`candidate-e5-v1:e6b28ff4585e5d3b5e00736c94414bddfb39dc0e7b9ba71f41f03084f08a7470`.
- `v7-sql.json`,`clause-scores.json`,`verification.json`,`sql-fragments.json` et logs/état :exécutionCPU réelle,quatre cycles stables,102requêtes chaudes dont refus rapides.16fragmentsSQL et21ancresgold vérifiés contre octets/hash/page/version;40ancres de sortie contre-vérifiées indépendamment. Le gold n'entre ni dans l'encodeur ni dans la projection.
- `clause-scores.json` détaille les couples manquants et chaque famille; `verification.json` conserve les motifs de refus et décisions de trace. Les observations ne justifient aucun remplacement d'embedding : elles localisent des limites de reconnaissance de requête/source, sans benchmark causal d'un autre moteur.

CPU et runtime épinglés inchangés :image `sha256:d7c4dcbc6bdbbbd5cc93f13c3d8453cbcc2993c8211d788238bcc67c28141938`,E5small FP32/L2/préfixesquery-passage/threads2,code/poids/runtime readonly,user1000,networknone,CPU2/1200MiB/sansswap/600s,tmpfs/tmp64MiB. PGCPU1/768MiB/tmpfsdata512MiB,networknone,aucunportpublié,socketUnixseul. p95chaud36,734ms,premierappel15,228s,RSS908,328MiB,cgroup986,723MiB; pas de marge RAM générale inférée. SQL256statements principaux et12complémentaires/537,896ms; mesures complémentaires horsp95principal. Le pic cgroup est celui enregistré avant les validations, le RSS après validation est inchangé. FutureWarning de renommage get_sentence_embedding_dimension conservé, sans changement de dépendance.

Les6contrôles(SQLrefus extraction pendant encode_query,déréférencement,absence de réemploi et preuve historique) passent; aucune garantie atomique après dernière lecture ni remplacement par successeur revendiqué. `upgrade-measurement.log` tête0136,`downgrade-final.log` et `alembic-final.txt`0; deuxconteneurs dédiés retirés. L'interruption du cleanup était un échec de revue automatique lié aux crédits, pas un refus de sécurité ni un défaut produit. Aucune action non approuvée contournée; nettoyage repris par le mécanisme normal après « continue ».

### Décision et limites

V7 reste HOLD/nonactivé. Ce jeu prouve une insuffisance des questions libres et des sources non canoniques, pas une analyse complète de DCE. Les familles classiques réussies ne démontrent pas la robustesse linguistique générale. Les annotations sont synthétiques, la portée locale841 reste nonrésolue prudemment, et les fragments bruts peuvent contenir des clauses hors projection. Pas de corpus réel, UI, backendlive, VPS, P3, dépôt externe, déploiement, push ou GOpublic. A1nonadmis/A2HOLD.

Priorité de codage suivante : rendre l'intention RC explicite et fermée, avec sujet/demande/portée/couverture et ancres dans la requête; les impératifs sources et la portée locale des conditions restent deux risques séparés, sans modification improvisée après résultat.

Méthode :Superpowers using-superpowers/cadrage/plan/TDD/revue/vérification;ECCverification-loop. Graphify consulté,BasicMemory miroir,Serena activé lors des tranches liées mais aucune nouvelle navigation sémantique nécessaire;Context7/Jev/Manus sans objet(pas nouvelle API,fournisseur ni classement externe),OpenDesign/Impeccable sans objet(aucun visuel).

Prochaine étape : ESSAIS DCE — coder une intention RC candidate fermée (sujet, nature de la demande, portée et couverture), avec ancres exactes dans la requête; couvrir sur développement les paraphrases simples d’obligation révélées par le jeu 10, refuser les ambiguïtés, puis requalifier sur un nouveau jeu gelé sans activer le candidat. Conserver v7, les sources et UNKNOWN; DPGF reste non évaluable. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
