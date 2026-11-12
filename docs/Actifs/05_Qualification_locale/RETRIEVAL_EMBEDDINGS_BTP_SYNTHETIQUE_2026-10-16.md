# Retrieval et embeddings BTP synthétiques — 16 octobre 2026

## AS-IS, risques et insertion

Checkout principal codex/reconcile-smartao-20261009, HEAD30f26934430095632000a1d82519f61dbb4c6411, WIP conservé. Code : source SQL ne lit que la version de l'Affaire et l'extraction complète courante; service RAG encode puis indexe des RetrievalChunk, BGE dense local CPU viaSentenceTransformers, normalisationL2, indexSQL filtré par modèle/tenant/Affaire/version/classification et fraîcheur. Aucun segmenteur token-aware avant le modèle : fragments jusqu'à16000caractères, maxBGE8192tokens. L'adaptateur embed ne distingue pas query/passage : incompatible avec un remplacement E5 transparent, dont les préfixes diffèrent. Le modèle actuel n'est pas remplacé dans cette tranche.

Risques : troncature silencieuse, score assimilé à preuve, mélange modèles/scopes/versions, moyennes cachant omissions critiques, fuite via payload d'index/encodeur, OOM machine et comparaison inéquitable. Insertion : script de qualification hors production, corpus synthétique JSON et tests. Réutiliser RetrievalChunk/Scope, RagRetrievalService et InMemoryVectorIndex; résultats limités à identifiants/hashes/offsets, jamais de corpus réel. La source actuelle en SQL reste vérifiée par ses tests dédiés; un filtre synthétique ne la certifie pas seul.

## Protocole figé avant mesures

- Corpus texte et requêtes synthétiques uniquement, avec qrels séparés des entrées de l'encodeur; aucune admission Golden. Questions lexicales/paraphrases, négations, lots voisins, dates/conditions, absence de réponse, versions/extractions périmées, autreAffaire/tenant et FINANCIAL_PRIVATE/PERSONAL_DATA exclus. Sources/page/version/hash et intervallesUTF8 de chaque segment conservés.
- Segmentation commune par régions de1000caractères au plus, sans chevauchement ni réécriture; frontière espace privilégiée et contrôle des tokens réels, préfixes et tokens spéciaux inclus. Aucun segment tronqué admis. Mesure du fragment brut en parallèle pour révéler la perte possible sans segmentation, sans l'assimiler au pipeline de production.
- Référence BM25 locale, k1=1.5,b=0.75, tokenisation Unicode et accents repliés, stopwords limités ne supprimant ni négation ni chiffres; aucune dépendance ajoutée. BGE-M3 dense : aucun préfixe,1024dimensions,max8192. E5-small : query:/passage: distincts,384dimensions,max512. CPU,FP32,L2,batch1,deuxthreads,modèles épinglés et hashés,un processus à la fois. Aucun texte transmis à un fournisseur.
- Qualité ranking : Recall@1>=0.70,@5>=0.90,@10>=0.95 et rappel critique@5=1.00. MRR/precision@5, omissions détaillées et candidats retournés pour requêtes sans réponse mesurés. Un score de similarité n'est pas une preuve ni une probabilité; aucun seuil calibré sur ce jeu. UNKNOWN reste le statut métier, même si des candidats sont retrouvés. Toute fuite ou source interdite/obsolète, troncature ou ancre non reproductible est un refus absolu.
- Budgets matériels de cette machine chargée (~1.1Go disponible,swap presque plein) : conteneur CPU900MiB sansswap/réseau,CPU2,batch1; chargement<=180s,indexation<=180s,p95requête chaude<=2000ms,processus<=600s. Référence lexicale p95<=50ms. Temps chargement local (cache disque non purgé) distinct des premiers encodages et de trois répétitions chaudes; téléchargement et chargement ne sont pas confondus. PeakRSS/processus et peakcgroup séparés. Un OOM reste RESOURCE_REFUSED, jamais une mesure de qualité. Pas de quantification/fp16 ajoutées silencieusement.
- Acquisition contrôlée : fichiers publics MIT depuis révisions exactes Hugging Face,config/tokenizer/pooling/poids seulement,aucun code distant exécuté. BGE upstream ne fournit quepytorch_model.bin pour le modèle principal; Torch récent weights_only,trust_remote_code=False; E5safetensors. Poids horsGit,aucun corpus envoyé. ImageCPUlocale f166f5db31a5 déjà qualifiée réutilisée sans rebuild/pull.

## Plan minimal / preuves requises

- [x] TDD du filtre scope/fraîcheur/confidentialité, segmentation/hash/régions, préfixes et scoring sans réponse/omission.
- [x] Corpus figé et CLI reproductible, référence lexicale puis modèles un par un sous plafond.
- [x] Métriques par question/type, coût réel, refus et inconnus; aucun changement du moteur actif.
- [x] Tests knowledge et fraîcheurSQL sur base jetable; revue,lint/types/diff/secrets puisSemgrep.
- [x] Plan/case/journal/index et Basic Memory synchronisés après résultats.

Superpowers cadrage/TDD et ECC évaluation/vérification; Graphify et Serena pour orientation, Basic Memory comme miroir. Aucun UI/OpenDesign/navigateur nécessaire : pas de changement visible. A1 non admis,A2 générique HOLD,NO-GO public;aucunVPS/live/corpus réel/push/P3/déploiement.

## Revue préalable et corrections des métriques

Le premier smoke lexical, avant revue du gold, est archivé non qualifiant. Deux corrections indépendantes ont été appliquées avant toute mesure de qualité des modèles : q100 exige les sources initiale ET rectificative (la date initiale n'est jamais récompensée seule); q-tail exige la régionUTF8[9311,9405) de l'obligation H14, pas seulement l'identifiant parent. Fixture gelée après revue dans fixture-sha256.txt. Recall source et evidence_recall sont distincts; les segments dupliquant une source consomment toujours des places top-k, aucune agrégation optimiste. Les régions classées sont conservées avec chunk_id/offsets/hashes pour chaque question.

Régression rouge puis verte pour l'évidence : retrouver un autre segment du même parent reste une omission. La phrase H14 chevauche deux segments; seconde régression rouge puis verte : l'union contiguë retrouvée couvre la preuve, un trou reste refusé. Les classements de régions et de sources doivent rester identiques sur les quatre répétitions. **16 tests purs verts** après12rouges initiaux et ces deux régressions de revue. Ni fixture ni découpage modifiés pour améliorer un résultat de modèle.

## Ajustement explicite du profil matériel avant mesures finales

L'image existante porte Torch2.13.0+cu130 (586340KiB de pic lors des imports), bien que l'inférence vise CPU. E5 avec ce runtime, sous900MiB, est réellement refusé par cgroup : exit137/OOMKilled=true, aucun score produit. Ce n'est ni un bug produit ni une mesure de qualité E5. Le protocole ajoute un profil de qualification CPU pur de même version2.13.0+cpu, roue officielle vérifiéeSHA4ca4a9394b0c771238a4f73590fdbbc4debad85ed0fa63d026ae1b085da7d6e2, extraite horsGit et montée en lecture seule avant le runtime du conteneur. Aucun package/lock/image/service actif remplacé; aucune quantification ou réduction de précision. Les deux modèles seront comparés sous ce même profil CPU,plafond900MiB inchangé. La qualification de composition CPU de production reste ultérieure.

Le premier profil CPU partiel (Torch seul) a révélé une dépendance native : torchvision0.28.0 de l’imageCUDA ne peut enregistrer son opérateurNMS avecTorchCPU. Cette erreur de composition n’est pas un test produit ni une mesure de modèle. Le profil isolé est complété par la roue officielle torchvision0.28.0+cpu,SHAb545d46f4d2f9d30381281cf22874bfe1d32a8a7b0ee8396fccde89f30c6a9d9;aucunmasquage/désactivation artificielle de l’import. Torchaudio absent. Ce profil exige donc un coupleTorch/torchvision cohérent, pas un simple changement de device.

Checkpointmesure : E5CPU cohérent termine avec rapport JSON valide (profilnonprivilégiéUID1000 aligné avec la sortie;un premier run avait terminé les calculs mais échoué à écrire,nonqualifiant et archivé).45tests knowledge/21SQLHTTP verts,PGjetable tête0 puis retiré. SeulBGECPU est maintenant en cours,session46593,conteneursmartao-retrieval-bgecpu-measured-20261016,aucunrunnerconcurrent. Ne pas sélectionner/remplacer avant fin et revue des résultats.

## Résultats finaux — campagne locale bornée

26 sources texte synthétiques, dont19éligibles et7refusées,28segments indexés,23questions dont19avecattendus et4sansréponse. Les sources sont des fictions textuelles,page/version simulées; source_sha256 est le hashUTF8 du fragment synthétique, pas celui d'un PDF original. Les attendus ne sont pas une validation métier humaine. SHA du jeu gelé : `1b04b0eabd37af027352791c186e52cfd96b38906b7c3440ef38bb43dd5d08fd` (contrôle dansfixture-sha256.txt; le fichier fait autorité si transcription divergente).

| Mesure locale | BM25 de référence | E5-small CPU | BGE-M3 CPU |
|---|---:|---:|---:|
| Recall source@1 |78,95%|97,37%|97,37%|
| Recall source@5 / evidence@5 |86,84%|97,37%|97,37%|
| Recall source@10 |92,11%|100%|100%|
| MRR |0,8351|1,0000|1,0000|
| Questions critiques incomplètes@5 |q100,q101|q100|q100|
| Questions sans réponse avec candidats |0/4|3/4|3/4|
| p95 requête chaude |1,75ms|174,45ms|15594,47ms|
| Chargement local |nonapplicable|28,44s|16,27s|
| Indexation |scan lexical dans la requête|54,47s|42,21s|
| Pic RSS au point de mesure |20,16MiB|824,07MiB|886,01MiB|
| Pic cgroup |nonapplicable|851,93MiB|900MiB|
| Gate ranking critique |HOLD|HOLD|HOLD|
| Gate temps fixé |PASS|PASS|HOLD|

Les trois campagnes finales sont terminées avec exit0 et aucune fuite de source éligible observée : chaque ID retourné appartient au scope courant autorisé,7sources exclues avant encoder. Cela ne remplace pas les testsSQL/HTTP, qui sont également exécutés. Aucun vecteur/texte interdit n'est envoyé à un service; modèles sans réseau. La stabilité est vérifiée sur4passages (premier encodage de requête +3répétitions chaudes); classements de régions identiques. Le p95 s'appuie sur69requêtes chaudes, dont les refus financiers rapides; il décrit ce mélange, pas uniquement les requêtes positives.

La question q100 exige les deux sources contradictoires; les modèles en retrouvent une dans les cinq premières places. MRR1 ne signifie donc ni réponse complète ni absence d'omission. Les3requêtes négatives avec candidats sont couleurRAL absente, garantiePV absente et canari privé sans source autorisée; la requête financière est refusée par le garde existant. Ces candidats ne deviennent jamais des réponses : answer_state resteUNKNOWN. Aucun seuil numérique de similarité n'est ajusté sur ce jeu pour faire disparaître les erreurs.

La phrase H14 traverse deux segments; le gate d'évidence valide uniquement la couverture entière de l'union des régions effectivement classées. Les deux modèles la couvrent dans le top5. E5 compte1916tokens sur le fragment brut, mais217au maximum sur les entrées réellement encodées, préfixes/tokens spéciaux inclus : **aucune troncature dans le banc**; sans cette segmentation, E5 ne pourrait pas traiter tout ce fragment en512tokens. Cette segmentation de qualification n'est pas encore intégrée dans le flux de production.

Le scanBM25 est une référence locale simple : il reconstruit ses statistiques à chaque requête, aucun indexBM25 persistant n'est revendiqué. precision_at_5 est la moyenne sur toutes les questions du nombre de sources attendues distinctes dans les cinq segments, divisée par5 (y compris requêtes négatives); ne pas l'interpréter comme une probabilité de conformité. Les top-k portent sur des **segments**, les doublons de source ne sont pas dédupliqués avant scoring. Le score source est complété par evidence_recall sur les régions requises.

BGE tient physiquement dans le plafond grâce au fonctionnement du runtime, mais avec une pression disque importante (échantillon Docker>=175Go lus à20:53:08UTC). Taille des poids ne vaut pas RAM résidentielle nécessaire. Le cache disque n'a pas été purgé, la machine était chargée, un seul processus neuf par moteur : ces chiffres ne sont ni un benchmark universel ni une mesure à froid disque comparable. E5/BGE ont été évalués avec mêmeCPU2,FP32,batch1,plafond900MiB,versioncoupléeCPU et mêmes fragments. Les lectures disque ne sont pas mesurées de façon comparable pour E5/lexical : seul le coût BGE observé est rapporté.

## Décision technique et piste de codage

**Aucun remplacement actif.** La référence lexicale manque des preuves critiques; les deux modèles ne satisfont ni le cas de contradiction ni le gate sans réponse, et BGE dépasse le budget interactif de2000ms. **E5CPU est le candidat d'étude privilégié sous ces contraintes locales**, pour un rappel identique àBGE et une latence plus faible; il n'est ni admis comme moteur de production ni qualifié sur DCE réels. Les préfixes, la segmentation et le profilCPU font partie du candidat; changer seulement model_id serait incorrect.

La prochaine tranche doit coder un profil de retrieval candidat reproductible (modèle/révision/prétraitement, segmentation source et query/passage distincts) et éprouver contradictions/abstention sur un second jeu synthétique tenu à l'écart. L'index actuel filtre model_id mais ne décrit pas un profil complet révision/préfixes/segmentation; ne pas mélanger des vecteurs de contrats différents sous le même nom. Le moteur actif et ses droits restent inchangés jusqu'aux nouvelles preuves. Une combinaison lexicale/sémantique reste une hypothèse de travail, pas un gain démontré ici.

## Vérifications et limites de livraison

16tests du banc aprèsrouges initiaux et corrections de revue; **45tests knowledge finaux** (0,25s) et **21SQL/HTTP** (6,96s,1avertissementStarlette/httpx) réussis. Ruff globalbackend/scripts vert,mypy626sources vert,diffwhitespace/3SHA verts,detect-secrets3fichiersexit0. Semgrep1.179.0,225règles/2fichiersPython,0finding/0erreurJSON; limites génériques du scanner conservées,aucun upload. Les modèles, métadonnées, rouesCPU et rapports sont horsGit. Le backend applicatif, Web, schéma, migrations et locks n'ont pas changé; les suites globales backend/Web ne sont pas rejouées pour ce script horsproduction. Aucun claim de couverture globale nouvelle.

La revue indépendante a corrigé le gold rectificatif, la preuve H14 au niveau région et la couverture contiguë sans trou; contre-revue finale sans nouveau défaut concret, sans modèle/DB lancés par le reviewer. Les refus matériels/import/écriture intermédiaires sont archivés nonqualifiants; seulslexical.json/e5cpu.json/bgecpu.json sont les mesures finales. La revue automatique d'autorisation a temporairement atteint sa limite pendant l'interruptioncrédits; aucune action refusée n'a été exécutée à ce moment, reprise après rétablissement. Aucun contournement du contrôle.

PGjetable revenu àbaseAlembic0 puis retiré; conteneurs de modèles terminés et retirés nommément,aucun autre service arrêté. Cache public/roues/rapports conservés pour reproduction,aucuneinstallationactive modifiée. Pas deVPS/backendlive/corpusréel/effetP3/export/déploiement/commit/push/GOpublic. A1 nonadmis,A2 génériqueHOLD etNO-GOpublic maintenus.

## Rejouer le banc

Depuis la racine : `.venv/bin/python scripts/qualify_btp_retrieval.py --fixture backend/tests/fixtures/knowledge/btp_retrieval_synthetic_v1.json --engine lexical --output /tmp/lexical.json`. Pour un modèle : mêmes arguments avec--enginee5ou bge et--model-dirpointant vers le répertoire épinglé contenantqualification-manifest.json. Le dossier de poids doit comprendre lesconfig/tokenizer/pooling et poids officiels; aucun téléchargement implicite dans le worker. Charger un modèle lourd sous un conteneur--networknone,--memory900m,--memory-swap900m,--cpus2,timeout600; ne pas lancer directement sur une machine chargée sans plafond. Les rapports de cette campagne conservent le manifeste complet des poids/révisions/hashes. Les rouesTorchCPU ettorchvisionCPU doivent être montées ensemble avant les dépendances de l'image; ne pas remplacer seulementTorch dans un environnementCUDA.

Révisions exactes : BGE`5617a9f61b028005a4858fdac845db406aefb181`,E5`614241f622f53c4eeff9890bdc4f31cfecc418b3`. Sources primaires consultées : [BGE-M3](https://huggingface.co/BAAI/bge-m3),[E5-small](https://huggingface.co/intfloat/multilingual-e5-small),[PyTorchCPU](https://pytorch.org/get-started/locally/),SentenceTransformers/HFHub viaContext7. PréfixesBGEaucun,E5query:/passage:;CPUfp32/L2 et limites réelles contrôlés. ECCévaluation/vérification,Superpowerscadrage/TDD/revue,Graphify(~650tokens d'orientation)/Serena/BasicMemory appliqués. Aucun outilUI nécessaire,aucun Jev/Manus ou fournisseur d'inférence externe activé.

Une sortie CLIexit0/MEASURED signifie que la mesure a terminé, jamais que le moteur a passé ses gates. Les gates détaillés du rapport et les omissions restent obligatoires pour interprétation. Le corpus n’est pas indépendant de son auteur; une revue technique ne remplace pas une lecture métier humaine. Aucune conclusion de supériorité de marché ou de complétude DCE.

Prochaine étape : ESSAIS DCE — coder un profil de retrieval candidat CPU reproductible, avec identité de modèle/prétraitement, segmentation sourcée et encodages requête/passage distincts; qualifier les contradictions et l’abstention sur un second jeu synthétique tenu à l’écart, sans remplacer le moteur actif. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
