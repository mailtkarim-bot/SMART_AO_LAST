# Intention v3 / adaptateur / E5 CPU / SQL — mesure synthétique du 19 octobre 2026

## AS-IS, risques et insertion

HEAD30f2693, checkout principal/WIP préservés. L’adaptateur est qualifié par 24 tests unitaires et 17 PostgreSQL, sans mesure E5 intégrée. Insertion exclusivement dans un nouveau banc ; aucun moteur, profil, factory, API, UI, schéma ou dépendance actif modifié.

## Plan minimal et protocole avant mesure

- [x] TDD du banc : huit échecs sur son absence, onze tests purs et un test SQL verts sur notation séparée retrieval/projection, corruption d’ancres, garde SQL/socket/libpq et gel.
- [x] Nouveau gold synthétique rédigé par relecteur isolé sans accès au candidat/anciens jeux, transcrit avant tout résultat : 15 fragments de contenu, quatre contre-exemples de scope/fraîcheur, 30 questions et 23 clauses de référence. Trois strates : 18 discursives, six ouvertes simples, six fermées appariées. Les paires ne valent pas des preuves indépendantes supplémentaires.
- [x] Revue/contre-revue avant mesure, gel des entrées et du code ; aucune modification du candidat ou du gold après résultat.
- [x] Référence mémoire et SQL : E5 CPU réel épinglé, requête brute et preuves source/contexte, précision/omissions par clause, abstention et invalidation.
- [x] Contrôles et nettoyage exécutés, plan/index mis à jour ; miroir mémoire proposé localement, pas transmis.

Recherche dans tout le corpus courant, sans injection de fragment par question. Les sources/attentes métier proviennent du relecteur ; les ancres UTF8 sont calculées depuis ses citations, jamais depuis une sortie du candidat. Intention de requête et portée de clause source sont distinctes ; pas d’inférence de lot dans une requête dépourvue de lot.

Le banc conserve l’état complet et les omissions même en cas d’abstention sûre. La couverture d’une clause dans le texte récupéré ne compte pas comme projection de cette clause. Notation exacte des régions, sujet, portée, valeur et type ; les paraphrases de source ne sont pas générées par ce banc. Q17 permet la preuve de l’obligation de visite initiale mais pas celle du report ambigu ; aucune conclusion métier de report n’est produite. DPGF exclue du dénominateur évaluable, refus séparé obligatoire.

Budgets fixés avant mesure : CPU2, RAM1200MiB sans swap, timeout600s par exécution, p95 chaud≤2000ms, rappel source@5≥0,90. La fenêtre50 de l’adaptateur et ses seuils restent inchangés. Quatre passages par question ; premier passage distinct des trois répétitions chaudes, dont l’adaptateur réencode toujours les sources. Modèle FP32/L2, préfixes query/passage et runtime vérifiés par le code existant. Deux conteneurs sans réseau ni ports publiés, socket Unix partagé. PostgreSQL CPU1/RAM768MiB/tmpfs512MiB, tête0136.

Un contrôle positif historique, explicitement hors gold et hors métriques, est fixé avant mesure : « Pour préparer notre offre, la visite médicale est-elle obligatoire pour le lot 9 ? ». Il sert à constater un appel effectif E5/SQL si toutes les formulations indépendantes sont refusées avant encodage. Ce résultat ne compense aucune omission du challenge.

Aucun réglage après ouverture, aucune admission automatique ; UNKNOWN, A1 non admis, A2 générique HOLD, NO-GO public. DPGF non évaluable, classification financière SQL non qualifiée. Aucun corpus réel/live/VPS/P3/déploiement/commit/push.

Preuves privées : `~/.local/share/smartao-proofs/context-e5-sql-20261019/`. Basic Memory : résumé local uniquement, envoi toujours en attente de l’autorisation déjà demandée.

## Revue avant gel

La revue du banc et l’auto-relecture par l’auteur du gold ont détecté des modalités sémantiques affaiblies et une précision pouvant ignorer les valeurs erronées. Correction avant toute mesure : obligations conditionnelles restent REQUIRED avec applicabilité UNKNOWN, interdiction de dossier médical FORBIDDEN ; contextes sources cités et ancrés séparément des contextes de requête. La précision/rappel de projection exigent valeur/type exacts ; la preuve complète du contexte est mesurée séparément. Les ancres conditionnelles explicitement liées peuvent couvrir des régions distinctes de la clause. Une seconde régression positive/négative vérifie cette séparation. Une régression rouge/verte empêche de créditer une modalité fausse. Les questions anaphoriques sont rendues autonomes par l’auteur avant gel. Cette passe n’est pas une seconde annotation humaine.

Gel logiciel : 653 fichiers, manifeste privé freeze.json, tous les modules backend/app, scripts de qualification, gold/profil/tests. Modèle et manifeste runtime externes sont vérifiés par leurs hashes épinglés et les fichiers modèle contrôlés par CpuCandidateEncoder. Douze tests purs du banc et un SQL de développement réussis avant ouverture.

## Résultats gelés — échec de couverture, candidat HOLD

Deux exécutions CPU hors réseau terminées exit0, sans OOM : mémoire et SQL rendent exactement les mêmes états, reconnaissances, scores, clauses, contrôles et résultats d’abstention. Le gel de 653 fichiers est vérifié immédiatement après mesure. Lors de la clôture, un seul test SQL est reformatté sans changement AST ; aucun candidat/gold/dépendance de mesure n’est modifié. Le manifeste initial et le manifeste final reproductible restent conservés. Aucun réglage du candidat, du gold ou des seuils après ouverture.

| Mesure | Résultat et portée |
|---|---|
| Questions | 30 : 27 avec sources attendues, deux sans preuve et une financière non évaluable |
| Accès au retrieval sur le challenge | Q07 seulement ; 28 autres questions arrêtées par l’intention, une par garde financière |
| Couverture source des clauses @5 et @10 | **1/35 occurrences (2,86 %)** ; toutes strates ouvertes/fermées simples à 0/6 chacune |
| Projection | **34 absentes, une correspondance structurelle Q07 conservée UNKNOWN**, aucune valeur/type sémantiquement exacts (0/35) ; aucun faux fait connu ajouté |
| Q07 | Source interdisant les variantes retrouvée ; valeur/type non résolus sans lot numérique, contexte de portée générale non prouvé. Cette prudence ne remplace pas la couverture factuelle |
| Sources pertinentes par question | 1/27 questions avec source attendue (3,70 %). La métrique legacy precision_at_5 a un dénominateur fixe et ne remplace pas le bilan par clause |
| Requête et ancres | Requête brute, SHA et ancres retournées exacts ; contexte neutre attendu de Q25 « Pour préparer sa candidature, » absent. Les ancres présentes sont fidèles, pas la couverture de contexte |
| Refus | Q15 financier, Q16 critère absent et Q18 consigne patient : UNKNOWN sans hit. Q17 : absence de conclusion de report, mais obligation initiale non retrouvée ; aucune compréhension du report ambigu revendiquée |
| Source et invalidation SQL | 19 fragments stockés conformes aux textes/hash/page ; six contrôles vrais : fidélité, tenant, Affaire, invalidation, fragment invalidé absent, historique conservé |
| Encodage sur le challenge | 4 appels requête, 60 passages et 12 lectures source : quatre répétitions de Q07, 15 sources éligibles sur 19 ; les quatre contre-exemples ne sont pas encodés |
| Contrôle hors notation | Appel E5 effectif, 15 passages ; **zéro hit typé**, abstention sur la source médicale naturelle. Aucun crédit ajouté au challenge |
| Temps | Exécutions totales conteneur 18,90 s mémoire / 19,01 s SQL. p95 des requêtes chaudes 0,263 / 0,357 ms **dominé par les refus** : ce n’est pas une qualification de latence E5 ; première question 1,07 / 1,25 ms également sans encodage |
| Mémoire | RSS maximal 1021,14 / 1039,28 MiB ; cgroup 1107,12 / **1200 MiB exact**. Pas d’OOM, mais aucune marge RAM prouvée. Pics incluant modèle, validations et cache de pages, pas seulement embeddings |

Les modalités du gold restent indépendantes : une obligation conditionnelle demeure une obligation, avec applicabilité UNKNOWN. Le candidat n’est pas crédité pour une modalité connue manquante. La projection valeur/type et la preuve de contexte relié sont mesurées séparément ; seule une preuve complète serait créditée comme fully_proven. Aucun succès complet ici.

Le défaut dominant est en amont du retrieval : le reconnaisseur fermé ne couvre pas les formulations naturelles indépendantes. Ce résultat ne permet pas de juger la pertinence générale d’E5 ni de conclure qu’un remplacement d’embeddings corrigerait les omissions. Il ne constitue pas une analyse complète de DCE, ni une admission Golden DCE.

La revue des rapports confirme les comptes et les comparaisons. L’auteur indépendant n’a consulté ni candidat ni anciens jeux lors de l’écriture ; sa relecture du gold n’est pas une seconde validation humaine. Pas de revendication de qualification métier réelle.

## Vérifications et limites de campagne

Banc : douze tests purs, un SQL de développement et 56 ciblés réussis. Régression de modalité observée rouge puis verte. Ruff backend/scripts, mypy638, format et diff exécutés. Semgrep1.179.0, 225 règles sur trois fichiers Python : zéro finding/erreur JSON. detect-secrets1.5.0 : 46 signaux de SHA de provenance synthétique exactement triés, baseline et filtres inchangés.

Deux tentatives initiales de suite élargie sans sélection contractuelle correcte ont été interrompues ; l’exclusion du seul répertoire db laissait des fixtures SQL ailleurs. Aucune base par défaut n’a été utilisée : le contrat refuse l’absence d’URL explicite. La suite pure finale utilise `-m 'not db'` ; seul son résultat final est qualifiant. Pas de nouvelle suite backend globale avec DB : le précédent global3543 reste daté de la tranche d’adaptateur, sans extrapolation à ce banc nouveau.

Aucun changement de production, dépendance ou schéma. Les trois conteneurs de preuve sont retirés après vérification de la base finale. Le plan du dépôt porte la prochaine tranche ; Basic Memory reste proposé localement et non transmis en attente d’autorisation.

Suite pure finale : **2692 réussites, 864 désélectionnés, un avertissement, 39,16s, exit0**. Base finale Alembic0 vérifiée ; trois conteneurs dédiés absents.

Prochaine étape : ESSAIS DCE — coder sur un développement distinct une intention candidate v4 séparant acteur, objet et demande d’obligation, avec ancres exactes et contextes possessifs prouvés; couvrir les formulations naturelles simples tout en refusant les demandes multiples ou conditionnelles non qualifiées, puis mesurer sur un nouveau jeu indépendant gelé. Ne pas régler sur le challenge contexte/E5/SQL devenu historique ni activer le candidat. DPGF non évaluable; UNKNOWN préservé, A1 non admis, A2 générique HOLD et NO-GO public maintenus.
