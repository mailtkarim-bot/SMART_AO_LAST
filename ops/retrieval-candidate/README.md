# Profil CPU candidat — non activé

Ce répertoire décrit une qualification locale. Aucun compose, worker, endpoint ou factory actif ne le charge. Les segments candidats sont en mémoire; leur persistance SQL n'est pas qualifiée.

`profile-v1.json` fixe E5-small, sa révision, les empreintes des manifestes, le découpage1000/recouvrement150 et le seuil expérimental0.85. L'identifiant SHA du profil inclut aussi les préfixes, les versions d'implémentation et les politiques. Un seuil ne prouve ni réponse correcte ni absence; tout résultat garde `answer_state=UNKNOWN`.

## Préparer les fichiers locaux

1. Acquérir les seuls fichiers déclarés dans `model-manifest-v1.json` depuis la révision exacte du dépôt public E5; vérifier chaque taille/SHA-256. Copier ce manifeste sous `qualification-manifest.json` dans le répertoire des poids. Aucun fichier supplémentaire ni module externe autorisé. Le worker ne télécharge rien.
2. Préparer un répertoire CPU séparé depuis les deux roues officielles de `runtime-v1.json`, vérifier leurs SHA avant extraction/installation. Torch et torchvision doivent être tous deux CPU. Ne pas modifier l'environnement actif. Les versions SentenceTransformers/Transformers/tokenizers/numpy/safetensors du profil sont vérifiées avant chargement.
3. Exécuter dans un conteneur dédié sans réseau, avec code/poids/runtime en lecture seule, répertoire de résultats inscriptible par l'UID local non privilégié, CPU2, mémoire900MiB et aucun swap, timeout600s. L'image locale déjà qualifiée `smartao-r2-proof:20261014` a servi aux mesures; ce n'est pas une nouvelle image de production.

Commande interne au conteneur, après montage du dépôt sous `/trial`, des poids sous `/model`, du couple CPU sous `/cpu` et de la sortie sous `/proof` :

```bash
PYTHONPATH=/cpu HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  python /trial/scripts/qualify_candidate_retrieval.py \
  --fixture /trial/backend/tests/fixtures/knowledge/btp_retrieval_heldout_v2.json \
  --profile /trial/ops/retrieval-candidate/profile-v1.json \
  --model-dir /model \
  --runtime-manifest /trial/ops/retrieval-candidate/runtime-v1.json \
  --output /proof/heldout.json
```

Une sortie MEASURED/exit0 indique que la mesure a terminé; consulter les gates, jamais assimiler ce statut à une admission. Ne pas ajuster le seuil ou les règles sur ce jeu tenu à l'écart. Les manifestes identifient les archives de runtime et les versions installées; ils ne constituent pas une attestation cryptographique de chaque binaire installé ni de toute la machine.

## Politique RC v2, toujours candidate

`profile-v2.json` conserve poids/runtime/segmentation/seuil, et choisit explicitement
`rc-opposition-v2`. Le profil v1 et son identité historique restent disponibles.
Pour reproduire la mesure du 17 octobre, employer la même commande avec
`--profile /trial/ops/retrieval-candidate/profile-v2.json` et
`--fixture /trial/backend/tests/fixtures/knowledge/btp_rc_conflicts_heldout_v3.json`.
Le CLI exige alors un gold de couples et d'inconnus distinct des entrées de l'encodeur.

La projection couvre une grammaire bornée (visite, certaines pièces, variantes),
avec lot explicite dans la phrase, ancres UTF8 et refus des conditions/segments
tronqués. Les couples restent candidats et leur applicabilité UNKNOWN.
Limites mesurées : deux couples d'autres lots remontent pour des requêtes ciblées;
le garde financier existant bloque DPGF avant recherche. Aucun assouplissement de droits.
Le jeu3 est désormais une preuve historique, pas un jeu vierge pour calibrer des règles.

## Portée de requête v3

`profile-v3.json` choisit `rc-query-lot-v3`, sans modifier les identités v1/v2.
Employer `btp_rc_query_scope_heldout_v4.json` avec ce profil pour reproduire la campagne.
La portée ne retient qu'un lot explicite unique de la requête, avec ancre UTF8;
absence, exclusion, condition ou plage non prouvée restent UNKNOWN.
Les hits bruts sont conservés. Les preuves non rattachées sont exposées dans
`rc_unscoped_evidence`, sans être promues en couples du lot demandé.
La grammaire reste bornée; aucun périmètre métier applicable n'est établi.

Le rapport trace les refus financiers avant source/encodeur dans `policy_refusal`
et `non_evaluable_queries`. Les métriques documentaires brutes restent inchangées :
une DPGF refusée n'est pas déclarée lue et ne ferme pas un gate de complétude.

## Rappel générique v4

`profile-v4.json` choisit `rc-recall-v4`, avec le même seuil dense0.85.
La grammaire bornée de questions génériques sans lot peut compléter le top_k
par des segments portant des clauses RC reconnues du même sujet. Les résultats
denses restent prioritaires; le motif RC_SUBJECT_RESCUE ne transforme pas le score
en probabilité ni la clause en obligation applicable. Portée et réponse restent UNKNOWN.
Le préfixe UTF8 exact du fragment source est contrôlé pour ne pas perdre une
condition amont entre segments. Les clauses ambiguës ne sont pas secourues.

`score_trace` expose rang dense, score, seuil, régions/hashes et décision
DENSE_FLOOR/RC_SUBJECT_RESCUE/TOP_K_LIMIT/BELOW_FLOOR sur au plus50segments positifs.
La fenêtre n'est pas une preuve de couverture exhaustive des512segments possibles.
Pour reproduire la campagne : même commande avec `profile-v4.json` et
`btp_rc_recall_heldout_v5.json`. Les profils v1/v2/v3 restent inchangés.

La campagne v4 du17octobre utilise l'image locale de preuve
`smartao-rc-cpu-proof:20261017`, base Python épinglée identique au Dockerfile backend,
avec libstdc++6/libgomp1 et les paquets `.venv` montés en lecture seule.
Ajouter `/trial/.venv/lib/python3.12/site-packages` après `/cpu` dans PYTHONPATH;
TorchCPU reste prioritaire. OMP/MKL/OpenBLAS sont bornés à2threads.
Dockerfile, imageID et versions système sont archivés dans
`~/.local/share/smartao-proofs/rc-recall-20261017/`. Aucun environnement actif installé/modifié.
Le jeu5 a encore un faux candidat dense sur la visite médicale; profil HOLD,
pas de réglage après résultat ni de comparaison directe de latence entre runtimes.

## Questions spécifiques v5

`profile-v5.json` choisit `rc-specific-v5` et se mesure avec
`btp_rc_specific_heldout_v6.json`, dans le même runtime CPU de preuve.
Les questions d'obligation de visite médicale/chantier/site/locaux couvertes par
la grammaire exigent une clause sourcée du type demandé et du lot demandé s'il
est prouvé. Aucun type « chantier » n'est déduit d'une visite non qualifiée.
Les questions ambiguës ou spécifiques non couvertes restent UNKNOWN.

La trace conserve SPECIFIC_MISMATCH/SPECIFIC_UNPROVEN/SPECIFIC_QUERY_UNKNOWN.
Les citations ouvertes, préfixes de segments et apostrophes sont contrôlés avant
de reconnaître une preuve. Les clauses négatives restent pertinentes, sans
applicabilité automatique; les preuves d'autres types restent non rattachées.
Les anciennes identités v1–v4 et leur comportement restent disponibles.

Jeu6 : aucun faux candidat sur8cas attendus sans candidat, mais deux questions
positives évaluables restent incomplètes (sous seuil/condition). Profil HOLD;
ne pas ajuster les règles ou le seuil sur ce jeu devenu historique.

## Preuve de type et rattrapage typé v6

`profile-v6.json` choisit `rc-type-proof-v6`; la fixture gelée est
`backend/tests/fixtures/knowledge/btp_rc_visit_type_heldout_v7.json`.
Reprendre la commande CLI et le runtime CPU isolé décrits ci-dessus en changeant
uniquement profil et fixture. Ne pas activer le candidat ni régler sur jeu7.

Le sujet médical/site a sa propre ancre; la directive est distincte de la valeur.
Une mention ou citation n'est pas secourue. RC_TYPED_RESCUE permet un rappel
sous0.85 dans fenêtre50/top_k; le dense garde priorité, le rappel génériquev4
reste disponible. Les conditions dans le fragment entier vérifié par hash et
inclusion exacte du segment maintiennent UNKNOWN. Les marqueurs conditionnels
ne prouvent ni leur portée ni l'applicabilité; aucune obligation n'est confirmée.

Jeu7 :10/10positives évaluables complètes@5,0fauxcandidat/8cas sans candidat;
rappelbrut90,91%,DPGFnonévaluable et gate critical_complete fausse. HOLD.
Voir le dossier actif de preuve de type pour limites et mesuresCPU.

## Mesure conjointe SQL / E5 — jeu8

Le banc `scripts/qualify_candidate_sql.py` reprend les cinq arguments du banc
standard et exige une base synthétique vide à la tête Alembic. Il est dédié
à `smartao_e5_sql`,userproof,flag `SMART_AO_TEST_DISPOSABLE_DATABASE=1`,
DSN PostgreSQL+psycopg à socket Unix `/socket` uniquement. Ne pas utiliser une
base existante. Aucun backend/factory n'appelle ce script. Les paramètres
libpq de redirection et les fixtures privées/non synthétiques sont refusés.

Pour reproduire :suivre les montages/read-only/runtime épinglés précédents,
utiliser `profile-v6.json`,`btp_e5_sql_heldout_v8.json` et l'orchestrateurSQL
dans un conteneur networknone partageant uniquement le socket du PGjetable.
Budget conjoint CPU2/1200MiB/sansswap/600s;PGCPU1/768MiB/tmpfs512MiB,sansport.
Comparer avec le banc standard sur mêmejeu/mêmebudget.

Jeu8 :sources/traces/états exacts entreSQL etréférence,mais rappel81,94%,
5omissions génériques et3fauxretours;6gatesrouges etHOLD. Aucun réglage sur
ce jeu historique. Voir dossier actif pour commandes,hashes,limites etcleanup.

## Preuve de sujet RC et abstention v7

`profile-v7.json` choisit `rc-subject-proof-v7`, sans modifier les profils1–6.
La famille de visite générique inclut les types prouvés et la visite sans type;
une question DC2 bornée exige une directive DC2 sourcée. Les questions de visite
hors grammaire et ambiguïtés RC reconnues restent UNKNOWN avec refus du dense.
Conditions/négations/citations/ancres et top50/top_k restent conservés.

La preuve SQL se reproduit avec `qualify_candidate_sql.py`, le profilv7 et
`btp_rc_subject_heldout_v9.json`, sous les contraintes socket/runtime/budgets
décrites ci-dessus. Le banc choisit désormais une visite de site mono-source
à lot explicite pour son contrôle d'invalidation, sans ID de jeu imposé.

Jeu9 :8/8positives évaluables complètes,5/5génériques,0parasite/11casnégatifs;
les deux gates brutes DPGF restent rouges, aucune activation/admission.
Le texte d'un segment DC2 peut rester mixte avec DPGF : seule la projection
demandée est filtrée, l'évidence hors sujet reste traçable. Voir dossier actif
pour résultats/limites, ne pas régler sur ce jeu devenu historique.

## Paraphrases RC et précision des clauses — jeu10

`btp_rc_paraphrases_heldout_v10.json` ajoute `clause_inventory` et, par
question, `expected_clause_ids`/`family`. Ces champs sont du gold de mesure :
ils ne sont pas passés au candidat. Exécuter le bancSQL existant avecv7, puis :

```bash
.venv/bin/python scripts/score_rc_clauses.py \
  --fixture backend/tests/fixtures/knowledge/btp_rc_paraphrases_heldout_v10.json \
  --report /chemin/local/v7-sql.json --output /chemin/local/clause-scores.json
```

Le scoreur refuse une identité de fixture modifiée, vérifie ancres/hash/page/
version et distingue détection(contexteinclus),projection,contexte,UNKNOWN,
valeurs/typesconnusfauxetsurcertitude. Il ne réécrit ni résultat ni moteur.
Jeu10 :17/43couples question-clause détectés,14projetés,26omissions;v7HOLD.
Ne pas extrapoler le jeu9 aux paraphrases libres et ne pas régler surjeu10.

## Intention RC fermée v8 (non activée)

`profile-v8.json` choisit `rc-intent-v8`; profils1–7 inchangés. Le parseur fermé conserve sujet, demande, portée, couverture, ancres UTF8 et SHA256 de la requête brute. Une intention non couverte refuse avant source/encodeur; le garde financier précède le parseur. COVERED ne prouve aucune complétude documentaire.

Le banc existant `qualify_candidate_sql.py` accepte le profilv8 et le jeu `backend/tests/fixtures/knowledge/btp_rc_intent_heldout_v11.json`; le gold indépendant inclut `expected_intent` et `expected_query_anchors`. Le scoreur existant `score_rc_clauses.py` mesure les clauses. Jeu11 gelé :14/18questions positives évaluables complètes,20/25occurrences de clauses détectées et14projetées;3gates fausses,HOLD. Lot préfixé,formulaire au passif,source impérative et demande composée restent incomplets. Aucun réglage après mesure; voir le dossier actif du18/10/2026.

## Intentions préfixées et impératifs v9 (non activée)

`profile-v9.json` choisit `rc-imperative-v9`. Les profils v7/v8 sont conservés. L’extension reconnaît le lot en tête de requête et les formulaires DC1/DC2 au passif, avec offsets sur la chaîne brute. Les obligations impératives simples ont des ancres `SUBJECT/DIRECTIVE/LOT` ; un préambule antérieur non qualifié bloque leur promotion.

Le banc existant accepte ce profil et `backend/tests/fixtures/knowledge/btp_rc_imperative_heldout_v13.json`. Le gold indépendant `imperative_anchors` est exigé par la CLI et n’entre pas dans le moteur. Le jeu12 est un diagnostic historique de fixture non représentable (document dit étranger mais version partagée), pas un dossier d’admission. Jeu13 corrige seulement cette métadonnée, sans réglage moteur.

Résultat borné : dix cas nominaux ciblés complets, mais omissions conditionnelle/multi-sujet/lot « n° ». Le gold de la question sans lot est incomplet et celui du signal legacy horaire doit être explicité ; ne pas exploiter le score global comme une mesure exhaustive. Candidat HOLD ; détails, preuves et prochaine étape dans le plan et le dossier `RC_IMPERATIFS_INTENTION_V9_2026-10-18.md`.
