# Profil de retrieval CPU candidat — 16 octobre 2026

## Cadrage autorisé / plan

AS-IS : adaptateur BGE actif encode indifféremment query/passage, index persistant filtre model_id; le banc précédent a montré le besoin de segmentation et d'identité de prétraitement. E5CPU est candidat, pas moteur admis. Checkout principal codex/reconcile-smartao-20261009,HEAD30f26934430095632000a1d82519f61dbb4c6411,WIP conservé. Risques : vecteurs incompatibles, perte de contexte/texte, source périmée ou étrangère, score pris pour preuve, calibration sur les attendus, modèle/cache non vérifié.

Insertion minimale : profil pur immuable identifié par SHAcanonique, service candidat additif réutilisant RetrievalChunk/Scope et InMemoryVectorIndex, port d'encodages distincts et adaptateur E5 local vérifié. Aucun raccord dans la factory active, API, indexSQL, UI ou migration. L'index candidat est éphémère, pas une qualification de persistance segmentéeSQL.

Décisions avant second jeu : CPU/FP32/L2/batch1/threads2, E5small384dimensions/max512tokens,révision etmanifestes poids/runtime épinglés, query:/passage: explicites. Segments1000caractères au plus, recouvrement150caractères, frontières espaces et intervallesUTF8 exacts; zéro troncature acceptée. Seuil expérimental0.85, inscrit dans l'identité du profil, non interprété comme probabilité ni preuve d'absence. UNKNOWN reste l'état de réponse métier pour tous les résultats. Les signaux rectificatif/annulation/remplacement effectivement retrouvés déclenchent REVIEW_REQUIRED, pas une résolution juridique des contradictions.

Le service relit la source actuelle avant index/recherche puis avant retour, refuse tout changement de snapshot, filtre tenant/Affaire/version/confidentialité avant encodage, limite128sources/512segments, vérifie dimensions/normes et efface les snapshots incompatibles. Encodeur verrouillé pour éviter deux charges concurrentes lourdes; encodagequery/passages sans mutable role. Aucun cache global partagé entre profils.

- [x] TDD : identité/configinvalides, régions/reconstruction, scope/source modifiée, refus et encodages distincts, profils/vecteurs incompatibles, doubles/retries/concurrence pertinents.
- [x] Coder profil/service/encodeur CPU additifs et CLI de qualification reproductible, sans remplacement actif.
- [x] Figer un second jeu synthétique hors calibration avant mesures; garder les attendus hors encodeur. Rappel source/région@5>=0.90, critiques intégralement retrouvées, aucune source interdite, aucun candidat pour cas sans réponse, UNKNOWN obligatoire. Contradictions : sources opposées retrouvées et REVIEW_REQUIRED; aucun choix de fait applicable. Aucun réglage du seuil/règles après résultats du second jeu.
- [x] Mesurer E5CPU sur900MiB/CPU2/600s sans réseau; conserver omissions et refus explicites, pas de promotion si un gate échoue.
- [x] Revue, suites pertinentes/backend global, lint/types/secrets/diff et Semgrep; plan/case/journal/index actualisés. Synchronisation Basic Memory vérifiée à la fermeture.

Superpowerscadrage/TDD/plan/revue et ECCrégression/vérification; contrat interne typé, aucune machinerie OpenAPI ajoutée. OpenDesign/navigateur non applicables : aucun changement UI. A1nonadmis,A2génériqueHOLD,NO-GOpublic;aucunVPS/live/corpus réel/push/P3/déploiement.

## Preuves acquises avant suite globale

14rouges initiaux→14verts, puis régressionscachemutable/profilmodifié,périmètremodule/assetnonlisté et deuxcoursesdechargement/manifestecorrigées après échecs observés. **27tests candidat/CLI/architecture**, **71knowledge ciblés**, typage629sources et Ruffglobaux verts. Le profilJSON et les manifestes publics sont dansops/retrieval-candidate; README de reproduction sans activation. L'index candidat reste uniquement en mémoire.

La revue indépendante a fait corriger les poids modifiés durant la construction, la doublelecture de manifeste(hash/parse), et le gate de revue : les sources qui déclenchent un marqueur sont désormais attribuées; un rectificatif hors sujet ne valide pas un conflit implicite. Les modèles et manifestes sont hachés localement, les modules/chemins et actifs ajoutés sont refusés; contrôles avant/après encodage. Les archivesCPU et versions identifient le runtime choisi mais n'attestent pas chaque binaire installé; les montagesCPU de qualification proviennent des roues vérifiées de la campagne précédente.

Jeu2 gelé :16sources,12questions,empreinte `434fe288275f66bbadc37da06cdff0cd7477acf59fe79f622f136fc60299c433`. Lesrègles0.85/recouvrement150/versionv1 étaient figées avantmesure,aucun ajustement sur les scores du jeu2. Profil : `candidate-e5-v1:404d675940fadc943991dd1e67575ce6d2eaafc291d97cc9a53eda5ef3c63a77`. Modèle réel terminéexit0,sansréseau,900MiB/CPU2/600s,conteneur dédié retiré après archivage.

| Gate / mesure du jeu2 | Résultat |
|---|---|
| Recall source@1 |87,5%|
| Recall source@5 / evidence@5 |100% /100%|
| Preuves critiques manquantes@5 |aucune|
| Cas sans réponse avec candidats |0sur4|
| Scope/source et answer_stateUNKNOWN |PASS|
| Faux signaux de revue inattendus |aucun|
| Marqueurs de revue attendus |HOLD :h-visit-conflict|
| p95 requête chaude |23,19ms|
| Pic RSS |861712KiB (841,52MiB)|
| Piccgroup |900MiB|

Le rappel porte sur8questions positives, dont deux attendent deux sources; l'abstention porte sur4cas négatifs(financier compris). Les36requêtes chaudes incluent des refus rapides et de courtes questions; cette latence n'est pas directement comparable à l'ancienjeu ni au coût à froid disque. Quatre répétitions stables,pas de nouvelle preuve de généralisation. Le signal rectificatif est correctement attribué pourh-deadline. Pourh-visit-conflict, les deux textes sont trouvés mais leur opposition ne déclenche pas une revue justifiée : le détecteur ne couvre que des marqueurs explicites, pas une contradiction sémantique implicite. **Le candidat resteHOLD et admitted=false.** UNKNOWN n'est jamais transformé en fait applicable; aucun réglage sur ce jeu pour obtenir artificiellement unPASS.

Suite backend globale finale achevée : 2881 réussites, 3 avertissements, 1428,75 s, exit0, sur PostgreSQL jetable candidat port55441. Code/jeu/profil figés dans `~/.local/share/smartao-proofs/candidate-profile-20261016/code-before-heldout-sha256.txt`,rapportheldout.json conservé. Aucun autre modèle en cours.

## Contrôles complémentaires pendant le global

Semgrep1.179.0 :225règles/11fichiers examinés,0finding/0erreurJSON; limites génériques d'analyse(partielle selon langage) conservées,aucun upload/métriquesoff. Lintglobalbackend/scripts et typage629sources verts. Aucun fichier de code modifié après mesure du jeu2.

Détection de secrets :15alertesHexHighEntropy sur lesrévisions/checksums publics des troismanifestes. Chaque valeur a été rapprochée de la révisionofficielle, des poids hachés ou des empreintes demanifeste et rouesCPU déjàvérifiées. Triageprécis `is_secret:false` ajouté à `.secrets.baseline`,aucunfiltre/plugin désactivé,aucuneancienneentrée changée. Preuvespublic-checksum-triage.json/secrets-audit-result.json horsGit. Le hook de précommit refuse une baseline canonique non indexée; aucun staging n'est effectué sans instruction de livraison. Le même moteur de scan est exécuté en lecture de contrôle avec une copie privée de la baseline :0finding nouveau nontrié,15fauxpositifs publicsclassés. Cela ne prétend pas à unPASS du hook de commit tant que la baseline reste nonindexée. Changement de configuration de contrôle, pas du profil/algorithme de retrieval.

## Fermeture technique locale — 16/10/2026, 22:59 UTC

Profil CPU candidat codé et qualification locale bornée exécutée : 27 tests candidat/CLI/architecture, 71 knowledge ciblés et backend global 2881 réussites/3 avertissements/1428,75 s/exit0. Jeu2 : rappel source/région@5=100%, 0 candidat sur 4 cas sans réponse, p95 chaud23,19ms; conflit implicite visite non détecté, candidat HOLD/admitted=false. Aucun réglage sur ce jeu. Ruff/mypy629/diff/13SHA verts; Semgrep1.179.0/225règles/11fichiers/0finding/0erreur; 15checksums publics triés sans filtre désactivé ni staging. Contre-revue indépendante sans nouveau finding. PostgreSQL jetable vérifié Alembic0 puis arrêté, conteneurs candidat absents. Aucun moteur actif/API/UI/schéma/lock modifié, aucun commit/push/live/corpus réel/P3/déploiement/GO public. WIP préservé, HEAD30f2693 inchangé.

Les 71 tests ciblés incluent les nouveaux tests : les comptes ne sont pas additionnés. La contre-revue a rejoué séparément les 26 nouveaux tests candidat/CLI. Le backend global a été exécuté avec --no-cov : aucune nouvelle mesure de couverture. Les 3 avertissements (Starlette/httpx, alias Pydantic export_id et X-CSRF-Token) sont conservés, sans modification hors périmètre. Aucun test Web/navigateur rejoué : interface inchangée. Aucune migration ajoutée; nettoyage de la base confirmé avant arrêt.

Fichiers : knowledge/domain/embedding_profile.py, application/candidate_retrieval.py, infrastructure/candidate_embeddings.py; CLI scripts/qualify_candidate_retrieval.py; trois modules de tests, fixture heldout_v2, ops/retrieval-candidate et triage précis .secrets.baseline. Le moteur actif et son port ne sont pas remplacés.

Invariants démontrés dans le périmètre candidat : filtration tenant/Affaire/version/confidentialité avant encodage, source relue avant retour, refus snapshot/profil incohérent, régions UTF8 et hashes exacts, retry stable et concurrence entre scopes, réponse UNKNOWN sans effet métier ni admission automatique. La preuve ne couvre ni les DCE réels entiers, ni une garantie générale d’abstention, ni la contradiction implicite, ni la persistance SQL des segments. Pic mémoire sous plafond900MiB : ce seul essai ne prouve pas une marge d’exploitation suffisante.

Outils : Graphify et Serena pour orientation; Context7 pour les contrats SentenceTransformers; Superpowers cadrage/plan/TDD/revue/vérification et ECC ai-regression-testing/verification-loop. Basic Memory reste le miroir du plan. Jev/Manus non sollicités : pas de jugement externe nécessaire à cette preuve déterministe; OpenDesign/Impeccable et navigateur non applicables sans modification visible.

Prochaine étape : ESSAIS DCE — coder sur les cas de développement une détection candidate des contradictions implicites RC, reliée aux couples de sources et à leur portée lot/version; distinguer opposition, négation et rectificatif, préserver UNKNOWN, puis qualifier sur un nouveau jeu synthétique gelé sans activer le moteur candidat. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
