# SMART AO — Revue globale métier, code et conception — 14 octobre 2026

## 1. Décision d’ingénierie

**Recommandation : poursuivre le logiciel existant par des capacités métier complètes, avec preuves partielles par capacité et une intégration finale par Affaire.** Les choix d’outils servent ces capacités. Le prochain travail n’est plus une comparaison d’embeddings isolée : fermer d’abord les défauts de contexte/source et d’assemblage, puis les lacunes qui empêchent les résultats attendus.

Cette revue répond à la demande Owner de relire tout le cahier, d’affronter l’existant et de proposer la suite. Elle révise le pilotage; elle ne réduit ni les douze axes ni les exigences différées. Les recommandations de conception sont candidates, dérivées du Freeze v3.1; aucun nouvel effet métier ou droit n’est créé. Le plan global reste la seule autorité de statut et de prochaine étape.

### Lecture et périmètre vérifiables

| Document actif | Lecture intégrale réalisée | Rôle de lecture |
|---|---|---|
| Master métier v3.1 | 1–5932, 430 chapitres identifiés | Revue amont 1–3000; aval 3001–5932, portions tronquées reprises |
| Cahier technique v3.1 | 1–4607, 381 chapitres identifiés | Amont 1–2300; aval 2301–4607, portions tronquées reprises |
| Product Freeze v3.1 | 1–978, 106 chapitres identifiés | Codex intégrateur, trois blocs contigus |
| Référentiel dépendances WORK_PROPOSAL | 1–1969 | Revue dépendances, avec actualisations et configurations |

La lecture est répartie et consolidée par Codex, pas une simple inspection des tables des matières. Le [registre des 917 chapitres](REVUE_GLOBALE_CHAPITRES_2026-10-14.csv) conserve source, identifiant, lignes, titre et lecteur. Ce nombre désigne des chapitres, pas des comportements livrés, des tests ou 917 verdicts individuels de conformité. La [matrice des 45 familles](REVUE_GLOBALE_CAPACITES_2026-10-14.csv) reprend le classement fonctionnel existant et distingue les constats frais des familles non requalifiées individuellement.

**Snapshot :** checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP inclus dans la lecture. Empreintes de 1218 fichiers code/tests/cahiers/configuration conservées hors Git dans `/home/noor/.local/share/smartao-proofs/global-review-20261014/source_manifest.json`. Le graphe existant de 19320 nœuds a servi d’orientation; le code actuel a ensuite été lu. Il ne constitue pas une photographie fraîche de tous les changements.

**État de maturité :** socle conséquent de sécurité, versions, actes humains, finances déclarées, partenaires, P5 et passation. La couverture métier automatique et l’assemblage des outputs acheteur restent incomplets. La première tranche A du cahier peut être manuelle et sourcée; il ne faut ni la reconstruire ni présenter les automatismes partiels comme équivalents à toute la promesse.

## 2. Ce que le cahier exige réellement

PF31-01/03/04 et M31-01/03 prescrivent : source/version → constat → applicabilité humaine → engagement → impact/hypothèses → condition Patron → offre exacte → contrat attribué → événement → action/preuve → réception/sortie → REX. Le point de valeur est de comprendre ce qui sera vendu, ce qui a été accepté et ce qui change.

M2-026/027/029 ajoutent trois obligations distinctes : douze axes métier; chaque risque avec source, portée, conséquences, responsable, action et preuve; une complétude documentaire visible. Lire tous les fichiers ne garantit pas que ces résultats soient produits. Retrouver un paragraphe ne prouve pas une obligation ni un prix couvert.

PF31-09 fixe les reports : calcul juridique/calendaire validé, sanctions quantitatives, règlement/DGD, cash portefeuille, assurance/HSE automatisés et MIRP avancé. Le détail demeure dans le cahier et dans la matrice; son report n’autorise pas à masquer le risque ou à fabriquer une conclusion. Le socle minimal par Affaire demandé par R09 reste nécessaire : ressources critiques/périodes et cash prudent, même sans ERP ni portefeuille avancé.

## 3. Constats prioritaires recoupés dans le logiciel

### RG-01 — Priorité 0 : résultats de recherche sans garde complète de contexte

`web/src/features/dce/useDceKnowledge.ts:17,65` stocke les résultats sans clé session/Affaire et accepte une réponse sans garde de séquence; la lecture DCE a déjà une clé et une séquence (`:21–38`). `web/src/app/App.tsx:525` recharge la lecture; `DceKnowledgePanel.tsx:127` peut rendre les anciens résultats quand une nouvelle lecture est disponible.

**Preuve fraîche : deux tests React synthétiques échouent** — ancien résultat après changement de scope; réponse tardive après changement d’Affaire. Ils ont été exécutés sur le hook réel, conservés dans `search_scope_reproduction.test.tsx` et leur log privé; le fichier de lancement temporaire a été retiré. Aucune fuite d’un backend réel ni faille d’autorisation serveur n’est revendiquée.

**Insertion minimale :** étendre le mécanisme déjà présent aux résultats, requête et états de recherche; vérifier le contexte exact et les réponses discordantes. Tester également deux réponses hors ordre, changement DCE/acteur, erreur tardive et indisponibilité. Priorité avant toute qualification de pertinence.

### RG-02 — Priorité 0 de qualification : source RAG ancienne encore sélectionnable

`backend/app/modules/knowledge/infrastructure/dce_source.py:54–57` sélectionne toutes les extractions COMPLETED d’une version, sans exclusion de l’ancienne après nouvelle extraction à revoir. `vector_index.py:89–103` sélectionne les vecteurs par tenant/Affaire/version/modèle/classification, sans revalidation de l’extraction courante. L’analyseur RC dispose déjà d’une garde contre les extractions ultérieures (`dce/application/analysis.py:303–375`; régression `test_dce_rc_analysis.py:226`).

**État : risque statique à reproduire en PostgreSQL jetable, pas incident de production prouvé.** Fermer lecteur de source et recherche sur index ancien; une réindexation seule ne suffit pas. Tests : nouvelle extraction partielle/refusée, timestamps égaux, ancienne source indexée, rectificatif, autre tenant et version; aucune source devenue inadmissible ne contribue au résultat.

### RG-03 — Priorité 1 : extras de l’image backend non composés

`ops/docker/backend.Dockerfile:32–54` effectue des `uv sync` successifs avec des extras différents. La CI demande plusieurs extras (`.github/workflows/ci.yml:128`), tandis que les tests ops vérifient surtout des chaînes de commande (`test_preprod_ops_contract.py:394`). [uv synchronise exactement la sélection](https://docs.astral.sh/uv/concepts/projects/sync/) : les extras précédents peuvent être retirés.

**Preuve complémentaire :** dry-run hors réseau avec uv hôte 0.11.21 et l’extra calendar propose 141 désinstallations, dont Docling, RapidOCR, ONNX, Sentence Transformers et Boto3. Rien n’a été désinstallé ou téléchargé. Le plan propose aussi une installation/un téléchargement; il ne prouve pas qu’une synchronisation réelle hors réseau aboutirait. Le Dockerfile utilise uv 0.12.1 : son image finale n’a pas été construite dans cette revue.

**Insertion :** une synchronisation avec l’union des extras explicitement demandés; tests de sélection combinée et imports dans l’image finale sans chargement de modèle. OCR seul importe PyMuPDF (`advanced_extraction.py:208`), mais son extra ne le déclare pas (`pyproject.toml:39`) : fermer cette dépendance ou refuser explicitement la configuration, après choix de licence.

### RG-04 — Priorité 1 : signaux lexicaux et confirmation ne couvrent pas les analyses attendues

`dce/application/analysis.py:109–239,448–519` porte des motifs typés RC/CCAP/CCTP. `requirements.py:217–225` matérialise PENDING_HUMAN_CONFIRMATION/SOURCE_SIGNAL_ONLY. Confirmation humaine et relations risque–exigence existent. Ces contrats ne réalisent pas une analyse complète des prestations, interfaces, constructibilité, impacts et douze axes.

Étendre les observations candidates existantes avec portée lot/site/phase/conditions, valeurs exactes ou UNKNOWN et liens de preuves. Aucun signal ne devient par défaut conformité, applicabilité ou coût. La pertinence se mesure par type sur références séparées de la calibration; pas une regex par phrase attendue.

### RG-05 — Priorité 1 : couverture documentaire privée et carte métier non consolidées

Le CLI privé `scripts/qualify_dce_completeness.py:350–358` distingue couverture documentaire et sémantique. Le read model DCE (`dce/application/queries.py:76–87`) ne porte pas le même registre d’extraction/omissions. Le dossier Patron (`decision/application/patron_dossier.py:19–36,87–143`) projette contexte, inconnus, risques et conditions; la surface `PatronDecisionPanel.tsx:284–320` affiche compteurs/JSON et conditions, pas une consolidation explicite des douze axes.

Concevoir une projection centrale dérivée des registres existants : éléments réellement traités, non lus, portée revue, conséquences et actions. Montrer les résultats paginés et leurs sources. Ne pas créer une seconde vérité ni douze nouveaux écrans. Toute future conception visuelle suit PF31-11, OpenDesign Local Codex et Impeccable.

### RG-06 — Priorité 1 : entrée financière bornée et capacité/cash incomplets

`pricing/application/import_preview.py:92,98` lit caches de formules et onglet actif. L’import réel en lignes SALES existe; il ne démontre pas restitution fidèle de tous les onglets, formules, styles/protections et postes d’un cadre acheteur. Conserver original et expliciter toute feuille/cellule non traitée.

OR-Tools dispose d’un service, de runs persistés et d’une projection visible dans `web/src/app/App.tsx:1092`; les besoins/offres (`optimization/application/resource_assignment.py:19–35`) portent des unités, sans qualification temporelle complète des ressources. Le conflit d’une même équipe promise à deux chantiers n’est pas démontré par ce solveur seul. Les cycles de paiement sont des faits/revues prudents; une courbe de financement minimale par Affaire reste à établir.

**Contre-audit important :** l’alerte initiale « marge 0 % exposée pour vente nulle » a été écartée. Les primitives portent un 0 de protection de division, mais `scenario_handler.py:84–85` refuse le scénario et `scenario_reader.py:116` masque l’historique en UNKNOWN; `declared_margin.py` protège la couverture. Ne pas rouvrir ce défaut comme incident UI courant.

### RG-07 — Priorité 1 : offre/paquet/passation plus étroits que la cible acheteur

C10 possède origine exacte, hashes relus, transmission et P5/export revalidés : les tranches CT31-39..43 sont fermées localement et ne sont pas à recommencer. Mais `preparation/application/document_content.py:34–72` produit une trame dont la contribution reste à rédiger. `submission/application/service.py:214–228` exporte exactement `manifest.json` et `technical-response.md`; son manifeste (`:646–679`) peut référencer d’autres entrées sans exporter leurs octets.

La signature est liée au paquet global (`submission/application/signature_service.py:147`), pas à une matrice d’exigences de signature par pièce. La preuve externe reste une déclaration partielle. Il faut qualifier l’assemblage acheteur complet, ses formats/canaux et pièces exactes; conserver dépôt humain et contrôles P5, sans étendre ce ZIP par simple copie non revue.

La passation B1 est réelle et vérifie WON, P5 et version; la comparaison offre/contrat demeure correctement UNKNOWN (`case_handover_handler.py:223`). Étendre les écarts et obligations transmises plutôt que changer cet état par défaut.

## 4. Les douze axes : attendu, existant et prochain delta

| Axe | Socle réel examiné | Delta pour une sortie utile | Priorité de programme |
|---|---|---|---|
| Commercial | BOAMP, scoring expliqué, qualification humaine, Affaire | Critères sourcés et coût d’étude; aucune probabilité de succès inventée | Maintenir et intégrer |
| Candidature | Exigences, confirmations, bibliothèque/version/preuves, propositions C10 | Couverture par titulaire/lot/validité/document, visite/questions/critères exacts | Analyse prioritaire |
| Technique | Fragments, familles, observations et risques | Prestations/performance/site/phase, valeurs exactes, ambiguïtés et contradictions | Analyse prioritaire |
| Constructibilité/logistique | Risques, impacts et conditions humains | Accès/phasage/coactivité/levage et MIRP reliés à moyens/coût/délai/question | Verticale A |
| Contrat | Baseline/dérogation/impact/revues et signaux | Hiérarchie, version, applicabilité humaine et conséquence reliées | Verticale A puis B/C |
| Prix/marge | Import, contribution/scénarios exacts, catégories inconnues protégées | Coût couvert par obligation, feuilles/cellules traçables, double compte évité | Verticale A |
| Cash/garanties | Déclarations privées, cycles/revues/rejets | Échéancier prudent par Affaire, pic/date/causes, garanties et scénarios séparés | Minimum R09 puis portefeuille différé |
| Capacité | Solveur/runs/projection et preuves entreprise | Périodes, compétences, engagements concurrents et workflow source→calcul | Minimum R09 |
| Partenaires | Offres, prix, périmètres et comparaisons manuelles raccordées | Pièce exacte, inclusions/exclusions, transport, validité, disponibilité et couverture | Verticale A |
| HSE/assurance/réglementaire | RegulatoryProfile versionné, pièces et actes humains | Prérequis/personne/preuve/impact; règle/applicabilité revue, escalade explicite | Minimal déclaratif; automatisation spécialisée différée |
| Documents/engagements | Préparation, plan C10, contrôles/hash/P5 | Réponse substantielle, engagements mesurables et toutes pièces acheteur exactes | Verticale A/offre |
| Droits/réception/sortie | Événements, C1–C5, actes droits/réserves/obligations/paiement/REX | Contrat gagné et écarts; actions/preuves/REX typés, dates déclarées distinctes de calculées | B puis C; calcul juridique validé différé |

Le socle manuel peut fournir une valeur réelle et doit rester disponible lorsque l’IA est indisponible. Il ne remplace pas la qualification des capacités automatiques attendues. Chaque axe conserve son statut partiel et sa couverture; aucun score unique ne compense une lacune critique.

## 5. Dépendances : décisions proposées selon leur mission

| Famille | Position | Condition de fiabilité/optimalité |
|---|---|---|
| FastAPI/Pydantic, SQLAlchemy/psycopg/Alembic/PostgreSQL | Conserver | Corriger contrats/intégration; pas de nouveau langage ou stockage sans besoin mesuré |
| Sécurité/crypto/MIME/ClamAV | Conserver sous régression | Least privilege, step-up, panne scanner, absence de fuite; pas d’optimisation qui baisse les contrôles |
| pypdf/FontTools, python-docx/openpyxl | Conserver et enrichir précisément | Pages/cellules/formules/locators, original et limites; ne pas déclarer métré ou analyse plan universels |
| Docling | Qualifier son apport structuré | Garder page/table/cellule/bbox disponibles dans [DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/), actuellement réduit en Markdown/lignes; prouver gain sur tableaux avant routage PDF supplémentaire |
| RapidOCR/ONNX | Conserver comme candidat local | Modèles épinglés, budgets, couverture/négations/refus, cache hors réseau; OCR ne prouve pas toutes les relations |
| PyMuPDF/rendu PDF | Décision de licence à fermer | [AGPL ou commercial](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright). [pypdfium2](https://github.com/pypdfium2-team/pypdfium2#licensing), déjà transitive, candidat pour rendu; prouver géométrie/provenance et licences embarquées avant substitution |
| Torch/Sentence Transformers | Qualifier distribution CPU | `device=cpu` ne retire pas CUDA/NVIDIA du lock/install. Résolution Torch/Torchvision CPU cohérente selon [guide uv officiel](https://docs.astral.sh/uv/guides/integration/pytorch/); mesurer disque/chargement/RAM |
| BGE-M3, lexical et E5-small | Comparer après RG-01/02/03 | Segmentation, prétraitement question/document, version/hash, jeu BTP hors calibration; pertes, faux passages, abstention, CPU/RAM/p95; aucun vainqueur encore mesuré |
| Reranker / modèle génératif | Ajouter seulement pour gain prouvé | Contrat/adaptateur interne à qualifier; port à ajouter seulement si nécessaire et absence vérifiée. Sorties candidates sourcées, abstention et coût; aucune activation distante implicite |
| OR-Tools | Conserver | Les contraintes métier et sources sont le chantier; une solution OPTIMAL ne prouve pas calendrier/disponibilité omis |
| React/Vite/TypeScript/pnpm, Docker/proxy | Conserver et qualifier image réelle | Node hôte 22.23.1 compatible avec Babel8; patch Node du digest image à vérifier. Pas d’upgrade arbitraire |
| Stockage, HTTP/connecteurs, SMTP/calendrier, outils qualité/backup | Conserver/qualifier selon usage | Contrats synthétiques, intégrité/idempotence, restauration et sécurité; aucun contact ou envoi réel |

« Gratuit et léger » signifie priorité sans API facturée et licence compatible, avec ressources réellement mesurées. Cela n’annule ni CPU, stockage, maintenance ou hébergement. Pas de nouvelle dépendance pour une capacité déjà disponible; pas de gros modèle ajouté pour masquer un contrat de source incorrect.

L’inventaire détaillé de toutes les déclarations reste dans [la revue dépendances](../06_Dependances_et_exploitation/Dependances/REVUE_DEPENDANCES_ET_PREUVES_PARTIELLES_2026-10-14.md). Cette revue globale ajoute l’impact métier et les défauts d’assemblage. Licences/vulnérabilités de toutes les transitives ne sont pas déclarées qualifiées.

## 6. Conception recommandée et nouvelles pistes de codage

### A. Chaîne documentaire avec routage mesuré

Réutiliser ingestion/extraction/observations existantes. Le pipeline conserve l’état par document/page/région et la portée lot/version, puis produit des candidats sourcés. Texte natif, tableaux structurés et OCR ont des critères d’admission distincts; le coût d’un moteur avancé est payé là où le besoin le justifie. Une branche structurée Docling n’est promue qu’après comparaison. Les documents critiques non lus restent visibles même si d’autres résultats sont utiles.

### B. Compréhension métier candidate et validation

Distinguer détection (signal), valeur/condition extraite, revue d’applicabilité, obligation/engagement et conséquence. Réutiliser Requirement, confirmations, risques, A1, partenaires et profils métier. Conserver le texte brut/locator; un modèle peut proposer et rapprocher, mais ne signe ni n’efface UNKNOWN. La contradiction garde ses deux sources et les raisons de comparaison; ni silence d’une DPGF ni absence de résultat de recherche ne prouve une exclusion.

### C. Carte métier dérivée et quatre couvertures séparées

Une projection par Affaire/lot/version rassemble les registres autorisés : douze axes, conséquences, questions/actions/preuves/conditions. Couverture documentaire, besoins pour le prix, engagements de l’offre et couverture économique demeurent distinctes. La projection ne possède pas les données des contextes et ne duplique pas leur vérité. Rendre l’évidence accessible; ne pas afficher une somme partielle comme total couvert.

### D. Contrats financiers déterministes et données d’entreprise

Coût/cash/capacité exigent les données de l’entreprise : le DCE seul ne donne pas coût de revient, disponibilité des équipes ou trésorerie réelle. Les relier aux profils/sources et postes existants; déclarations et UNKNOWN d’abord, calculs exacts après entrée validée. Ajouter periods/ressources critiques et échéancier minimal R09 plutôt que fabriquer une certitude depuis OR-Tools ou un LLM.

### E. Offre fidèle et continuité A→B→C

Réponse technique substantielle à partir d’exigences et preuves entreprise, puis registre de ce qui est promis : KPI/moyens/fréquence/responsable/coût/preuve. Qualifier toutes pièces du pli, leurs signatures et version exacte avec P5. Après gain, revoir humainement les écarts offre/contrat, transmettre conditions et responsabilités; un événement retrouve ce qui a été vendu et ses nouvelles conséquences. Réutiliser B1/C1–C5 plutôt que créer un nouveau graphe/ERP.

## 7. Plan de codage ordonné, sorties et tests

| Tranche | Insertion principale | Livrable rejetable indépendamment | Régressions et sortie requise |
|---|---|---|---|
| **R0 — contexte de recherche** | useDceKnowledge + tests existants | Résultats/requête/états liés au contexte courant | Deux rouges déjà reproduits → verts; autre Affaire/session/rôle, réponse discordante/hors ordre, erreur tardive; aucune ancienne source rendue |
| **R1 — fraîcheur des sources RAG** | dce_source, vector_index, mécanisme analysis réutilisé | Une extraction devenue inadmissible ne contribue plus, même depuis ancien index | Rouge PostgreSQL jetable, nouvelle extraction à revoir/failed, timestamp égal, rectificatif, tenant; aucun modèle requis |
| **R2 — image/extras et profil CPU** | Dockerfile, tests ops, manifests ciblés seulement si nécessaire | Combinaisons d’extras reproductibles et dépendance OCR explicite | Rouge sélection effective (aucun/rag+advanced/OCR/advanced+OCR/tous), sync unique, imports image finale sans modèle; licence et profil CPU qualifiés séparément |
| **R3 — complétude intégrée** | extraction/handlers/queries + lecture existante | Toutes pièces connues et étapes/status consultables, source/locator et omissions | Archives/limites/formats, texte partiel, scanner/worker indisponible, retry; aucune annonce complète avec pièce critique non traitée |
| **R4 — analyses candidates et pertinence** | analysis/requirements/confirmations/profils existants | RC puis clauses CCTP/CCAP, lot/site/phase/conditions, faits normalisés ou UNKNOWN | Références sources exactes, négations, rectificatifs, tableaux, contradictions, corpus hors calibration; comparaison moteurs nécessaire par mission |
| **R5 — carte/constructibilité/prix/partenaires** | patron_dossier, A1/conditions, imports prix et comparaisons | Douze axes consultables, obligations reliées à coûts/hypothèses/question/action | Feuilles/formules/limites, coût inconnu≠0, devis expiré/périmètre incomparable, double compte, FINANCIAL_PRIVATE; scénario PF31-04A complet |
| **R6 — capacité/cash minimaux** | optimization, resolution_reader, pricing existants | Ressources datées et courbe prudente par Affaire, hypothèses visibles | Même équipe simultanée, qualification manquante, paiement retardé/attendu≠constaté, budget/infeasible/timeout; aucun GO automatique |
| **R7 — réponse et pli complet** | preparation, source exacte C10, signature/submission | Contributions substantielles et toutes pièces acheteur exactes | Engagement non chiffré, pièce requise absente, signature par pièce, formats/canal, hash changé, privés exclus, UNKNOWN/retry; maintenir acquis CT31-39..43 |
| **R8 — contrat gagné/passation/changement/REX** | B1/C1–C5, paiement/réception/REX | Conditions vendues retrouvables dans contrat puis événement et preuve | Différences offre/contrat, condition rouverte, responsable absent, événement rejoué, paiement/réception/droit distincts, réemploi REX gouverné |

La séquence n’impose pas de traiter les douze axes avec le même moteur. Les preuves partielles sont reliées à la sortie métier et réutilisées dans la recette d’intégration. Aucun mandat pour coder neuf tranches simultanément; un seul travail actif. R0 est suffisamment bornée pour commencer depuis les régressions reproduites; les autres gardent leur audit d’insertion/migration/contrat avant implémentation.

Pour toute modification de comportement : test rouge significatif, changement minimal, vert, suite liée, diff/lint/types et Semgrep adapté après tests. Pour schema : upgrade/contraintes/existing-data/downgrade autorisé/ré-upgrade/transaction/tenant/concurrence/rollback sur base jetable. Pas de test miroir d’implémentation pour remplacer la preuve fonctionnelle. La preuve image réelle est un gate distinct du test de sélection shell.

## 8. Objectif concurrentiel vérifiable

[JOOC](https://www.jooc.ai/) annonce analyse/synthèse, contradictions, connaissances et rédaction pour maîtrise d’œuvre. Son application n’a pas été testée ici; aucune limite d’un concurrent n’est inventée. SMART AO vise principalement PME de travaux et continuité de l’engagement. C’est une cible de différenciation, pas une supériorité déjà acquise.

Pour démontrer un avantage, comparer sur mêmes tâches/dossiers autorisés : omissions critiques, exactitude valeur/source/portée, faux positifs, inconnus préservés, délai pour une décision exploitable, qualité du mémoire, fidélité du pli et continuité après attribution. Ajouter scénario chantier/changement et données entreprise; un benchmark de résumé seul ne teste pas notre proposition. Aucun téléversement ou compte/contact concurrent sans autorisation adaptée.

Critères internes M31-08 : zéro violation d’invariant, toutes relations critiques annotées retrouvables, toutes sources critiques localisées et aucun cas attendu UNKNOWN transformé en certain. Publier erreurs/dénominateurs; aucun rappel universel déduit d’un petit corpus. Temps inférieur au traitement manuel et facilité de revue sont des cibles mesurées, pas le chiffre public d’un concurrent copié comme résultat.

## 9. Preuves exécutées et limites

- Lecture intégrale répartie et recoupement code/tests/configuration; Serena activé pour navigation, Graphify consulté; Basic Memory utilisé comme miroir/historique, code actuel prioritaire.
- **49 tests ops/autorité/schema/pureté knowledge passés, 0,26 s**, plus **1 test de primitive prix, 0,06 s**. Ce dernier prouve le 0 de division protégé et ne démontre pas un défaut de parcours après revue des guards.
- Revue amont : **28 tests purs passés, 0,34 s** (knowledge doubles/index, RegulatoryProfile, couverture RC); pas de vrais embeddings ni DB.
- **2 régressions React rouges reproduites, 26 ms de tests**. C’est une preuve de défaut du hook sur données synthétiques; aucun correctif produit effectué dans cette revue.
- Dry-run uv exact, hors réseau : plan de 141 désinstallations, sans mutation; manifest de 1218 empreintes sans divergence avant rédaction. Contrôles documentaires et relecture miroir après mise à jour.

Méthodes : Superpowers using-superpowers/brainstorming/dispatching-parallel-agents; ECC product-capability pour la synthèse, production-audit amont, change-impact/research-ops pour dépendances. Writing-plans consulté pour dimensionner les tranches; ce dossier est une revue et roadmap, pas neuf plans d’implémentation détaillés ni architecture nouvelle approuvée. Manus/Jev non utilisés : revues locales ciblées avec code accessible; aucun besoin de transmettre du corpus. OpenDesign/Impeccable non exécutés : aucune maquette, édition de composant ou direction visuelle nouvelle. Les prochains changements visibles les exigent.

Non exécutés : suites globales backend/web, build image, migrations/runtime PostgreSQL, Semgrep nouveau, navigateur, modèles réels, benchmarks concurrentiels, audit offensif, licences/vulnérabilités transitives exhaustives et exploitation. Les 26 erreurs de setup PostgreSQL de la précédente revue ne sont pas considérées réparées ni nouveaux échecs métier ici. Les preuves historiques demeurent datées, pas remplacées par les tests légers.

A1 non admis, A2 générique HOLD et NO-GO public. Aucun backend live, corpus transmis, VPS, déploiement, effet P3, dépôt externe, validation humaine inventée, commit ou push. Le rollback ancien binaire avec schema3 garde ses restrictions; aucune nouvelle qualification runtime ici. Le résultat de cette revue est un delta professionnel de codage, pas une déclaration de maturité commerciale.

**Relecture indépendante du dossier :** passe bornée dépendances/preuves effectuée; localisation de l’extra OCR corrigée et hypothèse de port LLM/reranker existant retirée. Aucun runtime supplémentaire ni validation humaine déduit de cette relecture.

## Suite locale — R0/R1/R2 clôturées le 14 octobre 2026

Les constats RG-01 et RG-02 ont été reproduits puis corrigés, le message de lecture tardif aussi. RG-03 est corrigé et l’image finale qualifiée pour composition/imports; profilCPUoptimal/licencePDF restent ouverts. Backend2569/web541+4ignorés, contrôles/revue et imports verts. Voir [la clôture locale](../05_Qualification_locale/R0_R1_R2_CONTEXTE_SOURCES_DEPENDANCES_2026-10-14.md). Le plan activeR3; cet audit conserve sa valeur datée, pas un défaut courant sur ces gardes désormais closes.
