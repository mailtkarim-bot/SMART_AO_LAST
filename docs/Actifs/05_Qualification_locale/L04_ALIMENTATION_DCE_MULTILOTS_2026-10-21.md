# L04 — alimentation DCE synthétique multi-pièces/multi-lots —21/10/2026

## AS-IS, risques et points d’insertion

Les services actifs d’extraction déterministe, d’analyse RC/CCAP/CCTP et de matérialisation alimentent le lecteur de synthèse. La dernière recette utilisait un seul signal RC. Les règles ne constituent pas un analyseur universel des douze axes; une extraction complète ne prouve pas une compréhension complète.

Risque : omission silencieuse, confusion lot1/lot2, négation promue en obligation, preuve ancienne réinterprétée, ou couverture proclamée à partir du seul nombre de pièces. Aucun moteur candidat, confirmation ou porte ne sera modifié. DPGF non évaluable par RAG.

## Plan minimal et critères

- [x] Figer un développement multi-pièces avec RC/CCAP/deux CCTP/planning/PGC/DPGF/bordereau, faits couverts et lacunes explicites; conserver hashes et locators.
- [x] Reproduire les omissions de visites de chantier/site; corriger les règles actives avec version explicite et validation historique inchangée. Régressions médicales, négations, conditions et ancres UTF8.
- [x] Exécuter extraction réelle des originaux texte, analyse et matérialisation sur PostgreSQL jetable; vérifier douze axes, sources, lots distincts, refus de complétude, isolation et invalidation. Ne pas injecter les exigences attendues dans les registres.
- [x] Mesurer un second dossier synthétique indépendant gelé après code, sans réglage après mesure; rapporter les omissions au niveau des faits et des axes.
- [x] Tests ciblés, suite appropriée, types/lint, Semgrep, diff et mise à jour du plan/index/matrice; nettoyage local.

L’admission de fixture de test ne vaut pas admission Golden DCE. A1 non admis, A2 HOLD et NO-GO public conservés. Aucun corpus réel, live, VPS, déploiement, P3, push ou dépôt externe. WIP principal préservé.

## Codage et premières preuves

Les quatre omissions de visites de chantier/site ont été reproduites par quatre tests rouges avant correction. Version active de l’analyseur de règles RC/contrat :6 (`smart-ao-rc-rules`), distincte des profils de retrieval candidats qui restent inactifs. Règles1–5 relues selon leur propre version; aucune substitution d’historique. Les négations et conditions restent UNSPECIFIED, sans confirmation métier implicite.

Un défaut de chaîne plus important a été reproduit sur PostgreSQL : `RecordDceRequirementMaterializationRunHandler` utilisait une copie de correspondance limitée aux types RC. Les signaux CCAP/CCTP faisaient échouer toute la matérialisation par KeyError. Le handler, le service et le lecteur partagent désormais `REQUIREMENT_TYPES`; les contrôles source/type/directive/confirmation restent actifs. Les deux gardes de provenance du lecteur admettent explicitement5et6; les versions non prises en charge restent refusées.

Les simples mentions « DPGF » dans la pièce financière et le bordereau produisaient aussi des signaux d’offre parasites. Dans la nouvelle analyse6 finale, les règles RC excluent les familles financières BPU/DPGF. Une simple mention AE/BPU/DPGF horsRC sans marqueur requis/facultatif ne devient pas une demande d’offre; les demandes explicites d’autres familles restent lisibles. Les sept règles contractuelles gardent leur propre portée. Le premier filtre nonRC était trop large : trois contre-exemples rouges ont révélé la disparition d’un mémoire technique exigé en CCAP/CCTP/OTHER; il a été corrigé avant qualification finale. La famille absente conserve son comportement antérieur, sans preuve d’applicabilité; la classification synthétique fait partie des entrées contrôlées de cette recette.

### Mesure source par source

Deux dossiers distincts de huit pièces texte UTF8, sur lots1/2 puis4/8 : RC, CCAP, deux CCTP, planning, PGC, DPGF vierge et bordereau. Originaux sous `backend/tests/fixtures/dce_l04_multilot/` et `dce_l04_multilot_holdout_v2/`. Chaque manifeste porte SHA256, ligne et citation des32ou33faits. Le jeu finalv2 et les quatre fichiers de production ont été hashés avant sa première mesure; aucune correction après mesure de ce jeu final. Le premier holdoutv1 (lots3/7) est conservé comme historique après la correction développée sur les trois cas de portée distincts; il ne fonde pas la qualification finale. Il est distinct du développement mais rédigé par le même agent : aucune indépendance humaine ni représentativité statistique revendiquée.

| Pièce par dossier | Faits attendus | Signaux présents | Faits métier non interprétés |
|---|---:|---:|---:|
| RC |12|12|0|
| CCAP |7développement/8holdoutv2|5/6|2|
| CCTP lot1 ou4 |4|2|2|
| CCTP lot2 ou8 |4|2|2|
| Planning |3|0|3|
| PGC |2|0|2|
| DPGF et bordereau |hors métrique sémantique|0parasite|DPGF non évaluable par RAG|
| Total |32développement/33holdoutv2|21/22|11|

**21/21 signaux attendus sur le développement et22/22 sur le holdout finalv2,0signal inattendu mesuré;21/32et22/33faits seulement représentés par un signal natif.** Ces ratios65,625%et66,667% ne sont ni une précision de compréhension métier ni un taux de conformité. Les onze absences sont conservées dans les attentes, jamais retirées du dénominateur pour annoncer une analyse complète.

La chaîne PostgreSQL lit réellement les originaux via `DceDocumentExtractionService`, analyse par `DceRcAnalysisService`, matérialise par `DceRequirementsService`, puis compose `read_analysis_dossier` et valide le contrat public. Aucun point attendu n’est inséré manuellement dans les registres d’exigences/risques. Tenant/version admise/scan et classifications sont des préconditions synthétiques de fixture : aucune qualification de collecte, scanner, classification automatique, PDF/OCR ou Docling déduite de fichiers texte.

La restitution vérifie21puis22points, source courante, document/version exacts, SHA document/fragment, ligne native et offsets UTF8; les assertions renforcées vérifient aussi type et axe attendus indépendamment du mapping de production. Trois visites sont restituées par dossier : les deux positives gardent leurs lots candidats distincts; la négation ne devient pas une obligation et sa portée projetée reste UNKNOWN. L’applicabilité métier de tous les points reste UNKNOWN tant qu’aucun acte humain ne la qualifie.

Les huit documents sont extraits, unread_documents=0, mais analysis_complete=false; les axes non alimentés restent NON_EVALUATED. La nouvelle extraction REVIEW_REQUIRED d’un RC retire ses preuves courantes et modifie le SHA du dossier. Relecture identique sans double matérialisation et tenant étranger sans dossier vérifiés.

### Écarts métier restant à coder

| Source du développement | Fait absent comme point métier | Axe attendu |
|---|---|---|
| CCAP ligne6 |délai de paiement de trente jours|CASH|
| CCAP ligne7 |procès-verbal/réserves de réception|RIGHTS|
| CCTP lot1 ligne3 |isolation R4|TECHNICAL|
| CCTP lot1 ligne4 |créneau de livraison|CONSTRUCTIBILITY|
| CCTP lot2 ligne3 |remplacement luminaires LED|TECHNICAL|
| CCTP lot2 ligne4 |maintien alimentation de secours|TECHNICAL|
| Planning lignes1–3 |fenêtre d’exécution, dépendance inter-lots et équipe|CAPACITY|
| PGC lignes1–2 |diagnostic amiante et séparation des circulations|HSE|

Ces faits sont lus comme texte, mais leur traduction en exigences/contraintes utilisables n’existe pas dans la chaîne qualifiée. Leur absence est mesurée ici; la synthèse expose l’absence d’évaluation des axes, pas encore chaque fait manquant sous forme de point critique. Les garanties/pénalités sont des signaux CONTRACT, pas des calculs d’exposition ni un échéancier. Les portées CCAP/CCTP ne sont pas toutes projetées en lots : UNKNOWN conservé, aucun transfert depuis le titre du fichier.

### Vérifications intermédiaires (historique)

382tests purs de régression réussis;4tests PostgreSQL des deux dossiers réussis avant renforcement des assertions, puis74tests SQL/consommateurs réussis avec assertions renforcées sur la version intermédiaire. Gate finalv2 :74réussites/1avertissement, résultat dans strict-sql-gate-v2.log. Suite globale backend en cours, non encore qualifiée à ce stade. Ruff, format9fichiers et mypy650sources verts. Semgrep1.179.0,225règles,9fichiers effectivement scannés,0finding/0erreurJSON; le message générique de fichiers ignorés ne réduit pas ces neuf chemins explicitement vérifiés. Pas de scan exhaustif du dépôt.

Revue indépendante ciblée : aucun défaut production concret; une lacune des assertions de type/axe identifiée puis renforcée. Ni revue humaine métier ni conformité complète déduites. Aucun changement UI/API publique/dépendance/migration; moteur de règles actif corrigé localement, aucun moteur de retrieval candidat activé.

Preuves privées : `~/.local/share/smartao-proofs/l04-multilot-20261021/` (`code-and-holdout-v2-freeze.json`, `clause-coverage-final-v2.json/.csv`, logs rouges/SQL/global, Ruff/mypy/Semgrep). Les compteurs intermédiaires ne supplantent pas le bilan final ci-dessous.

### Méthode et portée des outils

Superpowers : cadrage borné du parcours déjà autorisé, plan interne, régressions rouges puis corrections, revue ciblée avec contre-revue et vérification avant clôture. ECC : verification-loop avec tests/types/lint/scan/diff. Graphify interrogé avant exploration (graphe19320nœuds, réponse bornée/tronquée); code et tests courants utilisés pour les conclusions. Aucune reconstruction globale du graphe ni navigation sémantique Serena nécessaire pour ces quatre fichiers connus. Pas de nouvelle API de bibliothèque ni dépendance introduite; les contrats installés et les usages existants ont été vérifiés dans le dépôt.

Aucune modification visible d’interface dans cette tranche : pas de nouvelle génération OpenDesign/Impeccable ou recette navigateur; leur preuve L04 antérieure reste datée dans son dossier. Jev/Manus non sollicités pour ces régressions déterministes; la revue indépendante de code ne vaut pas approbation métier. Basic Memory : miroir local de la clôture, non transmis; le plan reste la seule autorité de statut.

### Exécution intermédiaire conservée

La première suite globale a été interrompue proprement après2634réussites/2avertissements/1003,80s : elle ne qualifie pas le filtre final. Log `backend-global-historical-interrupted.log`. Une suite globale neuve et un gate SQL finalv2 sont exécutés sur deux bases jetables distinctes; aucun compteur intermédiaire n’est déclaré global vert.

## Bilan final

Chaîne active extraction→analyse→matérialisation→dossier qualifiée sur deux DCE synthétiques de8pièces, lots1/2 et4/8. Correction Python : mapping CCAP/CCTP incomplet du handler (KeyError reproduit), visites de chantier/site omises, faux signaux RC sur pièces classifiées nonRC; version6 avec relecture historique1–5 conservée. Développement21/21et nouveau holdoutv2 22/22signaux attendus restitués avec type/axe/source/version/hash/ligne/offsets,0signal parasite mesuré,11faits métier toujours non interprétés par dossier (32/33faits attendus); L04 PARTIAL, aucune analyse complète déduite. Backend global3697passés/1avertissements/874.99s/exit0;74SQL ciblés et382purs verts. Ruff/format/mypy650/diff verts;Semgrep1.179.0/225règles/9fichiers0finding/0erreur;24SHA publics triés,0secret nouveau nontrié. Revue P2 des assertions corrigée et contre-revue sans autre constat.

Les erreurs intermédiaires sont conservées : quatre omissions positives rouges; trois faux signaux hors famille rouges; KeyError CCAP/CCTP de chaîne reproduit. Les erreurs de montage du test (horodatage synthétique plus ancien que created_at réel, attente de portée sur négation et import de constante renommée) ne sont pas présentées comme des défauts supplémentaires du produit. Les nouvelles assertions de type/axe ont été exécutées dans le gate74tests après ajout; le code de production est identique au gel précédant les deux jeux. Les tests sont recouvrants : leurs nombres ne s’additionnent pas en couverture unique. Aucune mesure de rappel général BTP ou d’exhaustivité déduite.

Prochaine étape : L04 — coder et qualifier l’alimentation du dossier par les prescriptions techniques et contraintes d’exécution, de paiement et de réception actuellement omises : points source/version/lot, conditions et négations, puis traitement/revue Patron dans le parcours existant, sans activation de candidat ni modification des portes.

## Fermeture et reprise

Les deux bases jetables smartao_l04 et smartao_l04_strict ont été vérifiées Alembic0 après les tests; conteneur dédié arrêté, ACL UID70 retirée, répertoire socket700. Aucun serveur backend live ou navigateur ouvert dans cette tranche.36hashes de code/tests/fixtures inchangés depuis le dernier gel; HEAD30f2693 et WIP conservés, aucun commit/push.47tests des contrats documentaires réussis. Les compteurs de tests sont recouvrants; un avertissement Starlette/httpx est conservé.

Plan/index/matrice45familles et miroir mémoire local actualisés; aucune transmission Basic Memory externe. Le programme L04 reste PARTIAL avec les onze faits absents par dossier.

Prochaine étape : L04 — coder et qualifier l’alimentation du dossier par les prescriptions techniques et contraintes d’exécution, de paiement et de réception actuellement omises : points source/version/lot, conditions et négations, puis traitement/revue Patron dans le parcours existant, sans activation de candidat ni modification des portes.
