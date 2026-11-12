# L04 — dossier multi-formats, rectificatif et reprise — 21/10/2026

## AS-IS et frontière utile

Le parcours douze axes, les traitements humains révisionnés et la revue Patron existent. Cette tranche éprouve ensemble les lecteurs natifs PDF/DOCX/XLSX, la matérialisation, les sources par lot, les actes et leur invalidation. Elle ne constitue ni une admission du corpus ni une mesure de généralisation métier. Le moteur candidat reste inactif; aucun droit, confirmation, porte ou schéma n'est modifié.

**Risques :** un contenu non parcouru déclaré extrait; une preuve historique présentée comme courante; des doublons obsolètes bloquant la reprise; une revue ou un traitement transféré au rectificatif; un retry échoué effaçant le dernier registre.

**Points d'insertion :** projection d'extraction existante et sélection des exigences dans le lecteur DCE partagé. Réutilisation de tous les services, handlers et contrats publics; aucune dépendance nouvelle.

**Plan minimal / preuves :** reproduire les défauts; corriger le statut DOCX et le registre courant; faire passer les originaux binaires dans la chaîne native; traiter/préparer/revoir V1 puis V2; vérifier la conservation historique et la reprise après nouvelle recette d'extraction; revue ciblée, tests appropriés, sécurité, documentation et fermeture des ressources.

## Corrections codées et TDD

1. DOCX contenant un paragraphe et un tableau : régression rouge, état COMPLETED alors que les cellules ne sont pas extraites. Tableau seul : erreur générique EMPTY_EXTRACTED_TEXT. La projection signale désormais DOCX_TABLE_CONTENT_REVIEW_REQUIRED, avec REVIEW_REQUIRED si des fragments existent, FAILED_SAFE sinon. Les paragraphes restent conservés mais ne rendent pas la pièce admissible à l'analyse. Recherche des tableaux dans l'arbre XML déjà parsé par python-docx après les limites ZIP existantes, y compris sous une marque de révision. Aucune cellule inventée ni aplatie dans un faux locator de paragraphe. Recette déterministe version3, sans réécrire les extractions antérieures.
2. Même version, nouvelle extraction puis matérialisation : régression PostgreSQL rouge, six points au lieu de trois. La lecture courante sélectionne le dernier registre NO_SIGNAL ou COMPLETED contenant des lignes du tenant et de la version exacts. Une fausse réussite sans ligne conserve le registre précédent en UNKNOWN; régression existante rouge observée puis corrigée, EXISTS explicitement corrélé au run pour éviter de réintroduire les doublons. Les six lignes durables restent stockées; seuls les trois points du nouveau registre sont affichés. Une tentative FAILED_SAFE ultérieure conserve ces trois points, invalide leurs preuves en UNKNOWN et impose une nouvelle revue. Les conditions de provenance courant/dernière analyse/extraction et le tenant restent contrôlés.

## Scénario reproductible

`backend/tests/db/test_l04_multiformat_rectification.py` construit de vrais fichiers avec les dépendances déjà installées :

| Pièce | Fait couvert | Ancre attendue |
|---|---|---|
| RC PDF | DC1 requis lot2; DC2 dans V2 | page1, partie1 |
| CCTP DOCX | installer des clapets coupe-feu, lot2 | paragraphe1, partie1 |
| Planning XLSX | travaux lot7 du3 au28mai2027 | feuille Planning, cellule B3, partie1 |
| Annexe PGC DOCX | paragraphe + négation dans tableau non lu | pièce non lue, aucune promotion |

Le générateur écrit un manifest avec hashes des octets; aucune liste d'exigences attendues n'est injectée dans les registres métier. Admission et classification SYNTHETIC constituent des préconditions de fixture; elles ne valent pas acte d'admission réelle/Golden. Les sources sont lues depuis le stockage privé, puis extraction→analyse native→matérialisation→synthèse douze axes.

V1 : trois points source/version/hash/locator/lot exacts, applicabilité UNKNOWN, une pièce non lue, analysis_complete=false. Traitements source-liés, PREPARED puis REVIEWED via handlers natifs, retries identiques sans deuxième effet.

V2 : prédécesseur explicite, originaux propres, rattachement de l'Affaire par LinkCaseDceVersion; revue V1 invalidée avant nouvelle analyse, aucune évaluation humaine transférée. Les trois points V2 peuvent être traités puis le dossier préparé/revu à nouveau. Six révisions de revue conservées; les trois snapshots V1 sont inchangés et HISTORICAL.

Reprise sur la même version : une recette d'extraction synthétique distincte invalide les sources précédentes; nouvelle analyse/matérialisation restaure trois points courants et une revue utilisable. Six lignes d'exigences toujours présentes. Une matérialisation FAILED_SAFE injectée comme contre-exemple SQL rend les trois preuves UNKNOWN et la revue REVIEW_REQUIRED.

Les coordonnées et citations attendues sont des assertions indépendantes de la sortie du lecteur; le PDF a aussi été rendu et inspecté. Les pièces DOCX/XLSX sont vérifiées structurellement; aucune qualification visuelle Office ni navigateur n'est déduite de ces tests.

## Vérifications

Preuves locales : `/home/noor/.local/share/smartao-proofs/l04-mixed-20261021/`.

- Deux tests DOCX rouges puis verts; régression SQL six→trois observée puis corrigée.
- 96 tests ciblés finaux verts, dont les trois scénarios SQL, les coordonnées/lots/citations exacts et le refus d’un ancien traitement après rectificatif. Après détection du registre COMPLETED sans ligne par la suite globale, 37 tests synthèse SQL/multi-formats passent avec la correction. Le run global initial est interrompu (2487réussites,2échecs); une assertion historique de version2 mal changée en3 est restaurée. Un redémarrage sur schéma résiduel est écarté; qualification complète relancée sur une nouvelle base vierge smartao_l04_final. Aucun résultat interrompu n’est présenté comme vert.
- Ruff ciblé vert; mypy650 fichiers sans erreur.
- Semgrep1.179.0 :225règles,7fichiers,0finding/0erreur au scan initial. Les deux tests renforcés ont été rescannés :0finding/0erreur. Le lecteur SQL final est aussi rescanné après la correction du registre vide.
- Revue indépendante ciblée : aucun blocage confirmé; convention préexistante de départage created_at/UUID à conserver comme limite de chronologie en cas d'égalité de timestamps.

## Limites et suite métier

L04 reste PARTIAL. Ce scénario de développement contrôle la mécanique multi-formats, pas le rappel sur un DCE arbitraire. La calibration initiale a exposé deux formulations hors grammaire nativev7 : « Le titulaire doit fournir les plans pour le lot2 » et « Le délai d'exécution est de6semaines pour le lot7 ». Elles ne sont pas comptées comme retrouvées; leurs corrections sémantiques et contre-exemples doivent être traités sur développement puis mesurés indépendamment. Les assertions multi-formats utilisent des formulations déjà couvertes, sans changer les anciens jeux gelés ni prétendre constituer un nouveau challenge indépendant.

Les tableaux DOCX restent non lus; les graphes/raster, autres structures Office et l'exhaustivité du corpus ne sont pas qualifiés. L'accord textuel ne prouve ni applicabilité, ni conséquences financières, ni complétude. DPGF non évaluable par RAG. Aucun navigateur, backend live, corpus réel, VPS, déploiement, effetP3, dépôt externe, commit/push ou GO public; A1 non admis, A2 générique HOLD.

## Fichiers et méthode

- Production : `backend/app/modules/dce/application/extraction.py`; `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py`.
- Régressions nouvelles : `backend/tests/domain/dce/test_docx_coverage.py`; `backend/tests/db/test_l04_multiformat_rectification.py`.
- Réutilisation des fixtures et du parcours : `backend/tests/db/test_l04_multilot_pipeline.py` (types de média réels optionnels); `backend/tests/db/test_l04_execution_pipeline.py` (révision de départ de la revue). L'assertion historique d'extracteur2 a été conservée dans son test existant.
- Suivi : plan global, index et fiche des livrables; note Basic Memory du plan synchronisée dans le projet smart-ao-v8, historique intégral conservé. Les anciennes métadonnées de reprise v10 ne sont plus le statut courant.

Superpowers using-superpowers, cadrage borné/brainstorming, TDD, systematic-debugging, requesting-code-review et verification-before-completion; ECC verification-loop. Graphify consulté avant exploration, graphe historique recoupé au code courant. Skills PDF/DOCX/XLSX et Context7 python-docx utilisés pour les originaux et la limite paragraphes/tableaux. Serena non sollicité faute de navigation sémantique nécessaire; Jev/Manus non utilisés pour ces assertions déterministes. Aucun changement UI : OpenDesign/Impeccable et navigateur ne sont pas requis pour ces corrections internes, aucune preuve navigateur nouvelle revendiquée.

Limites de la sélection SQL : l'EXISTS prouve la présence de lignes, pas une complétude de cardinalité face à une corruption partielle arbitraire. Les handlers insèrent normalement le registre dans une transaction atomique; aucun test de perte partielle de lignes ni de départage chronologique avec timestamps égaux n'est déduit de cette recette.


## Résultat final et fermeture

- Backend complet final : **3730/3730,0ignoré**,1warning Starlette/httpx connu,1003,65secondes,exit0. Log `backend-global-qualified.log`; le code final n'a pas changé pendant la qualification.
- Ciblés :96/96 et37/37 (ensembles partiellement recouvrants, ne pas additionner pour annoncer un nombre distinct). Contrats documentaires4/4. Ruff/format ciblés et mypy650 verts. Semgrep1.179.0/225règles,7fichiers puis tests et lecteur finaux rescannés :0finding/0erreur; detect-secrets1.5.0 zéro finding, baseline inchangée.
- Hashes des sept fichiers de code/tests conservés; scénarios, originaux privés, aperçu PDF, logs rouges et JSON de vérification sous le répertoire de preuve.
- Bases `smartao_l04`, `smartao_l04_mixed_checks`, `smartao_l04_final` vérifiées Alembic0 (`cleanup.json`); seul conteneur dédié `smartao-l04-acts-pg-20261020` arrêté. ACL temporaire UID70 retirée, socket700. Aucun serveur UI/navigateur démarré dans cette tranche.
- Plan/index/fiche des livrables et Basic Memory actualisés; HEAD30f2693 et WIP conservés, aucun commit/push. L04 reste PARTIAL; les limites et refus ci-dessus demeurent ouverts.

Prochaine étape : L04 — corriger et qualifier les omissions métier des livrables techniques et des durées explicites, puis éprouver le dossier multi-formats complet sans modifier les portes ni activer de candidat.
