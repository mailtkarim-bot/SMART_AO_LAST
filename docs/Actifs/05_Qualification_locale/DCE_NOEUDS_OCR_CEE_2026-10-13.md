# ESSAIS DCE — découverte des nœuds OCR/raster CEE Cadarache

## Cadrage et plan minimal

**AS-IS :** les routes et directions candidates sont extraites, mais les neuf groupes OCR et leurs rôles étaient fournis. **Risques :** fusionner deux cadres, perdre une négation ou un mot de sortie, inventer une entrée après une relation inconnue, mélanger source/tenant/version. **Points d’insertion :** nouveau lecteur infrastructure `diagram_node_reader.py`, décodeur applicatif `discovered_diagram.py`, leurs deux fichiers de tests; aucune API, migration, dépendance, UI ou effet métier.

**Choix :** sonder les tokens OCR individuellement avec le lecteur de cadres existant, puis les regrouper par cadre unique et rattacher les tokens restants seulement à un cadre découvert les contenant de façon unique. Réutiliser les limites et validations raster existantes. Les sorties suivent le vocabulaire documentaire déjà utilisé par l’assembleur; les autres textes restent conditions candidates. Les entrées sont déduites des questions de la bande supérieure (chevauchement réel des captions), sans arête entrante parmi les directions qualifiées; toute route UNKNOWN touchant un nœud invalide toujours sa qualification. Les nœuds d’entrée fournis par les anciens appels gardent leur contrat.

- [x] Lire index/plan/CDC M2-026/027/029, vérifier Git, graphe et miroir; comparer35fichiers hérités entre checkout et worktree.
- [x] Observer rouge puis vert pour regroupement sans seeds et entrées sans rôles; contre-exemple rattachement d’une ligne basse après omission source.
- [x] Requalifier source et mesurer groupes/liaisons/conditions/chemins après reconstruction uniquement; contre-épreuves OCR manquant et T89 brut.
- [x] Revue indépendante, ciblés/global backend, Ruff/mypy, Semgrep/secrets/Bandit, diff et intégration contrôlée.
- [x] Actualiser plan/index/journal et miroir Basic Memory sans admission.

**Tests attendus :** groupes multiligne/négation/contact; cadres ambigus; illisible; ordre déterministe; limites/échelle; refus tenant/source/version/render; route entrante inconnue interdisant la fausse entrée.

## Limites persistantes

ROI inférieur fourni `(289,1098,881,1521)`, raster150DPI et OCR préexistant : ce lecteur ne découvre pas encore les zones de logigramme de toute une page, ni les cadres sans token OCR, ni la complétude de l’OCR depuis l’encre. La sortie documentaire ELIGIBLE n’est jamais une éligibilité réelle. UNKNOWN, REVIEW_REQUIRED, sources et provenance conservés; A1 non admis, A2 générique HOLD, NO-GO public.

## Source et résultat documentaire borné

CCTPC commun CEA Cadarache indice2, annexe13, page42/44 : « Variation de vitesse » BAT-TH-112. PDF original et raster sont hors Git. OCR brut de la page, puis sélection des tokens entièrement contenus dans le ROI inférieur fourni; aucun identifiant de token attendu, aucun groupe/rôle/endpoints/chemin attendu dans la découverte.

- PDF SHA-256 : `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`.
- Raster150DPI1275×1650 SHA-256 : `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.
- Scopes tenant/document/version/page et ancres source/raster strictement vérifiés. OCR brut T81 `iño` et T89 `Iño` conservé; les relectures OUI restent des observations réutilisées avec hash de crop/parseur/version, jamais un remplacement silencieux du brut.
- Référence consultée pour comparaison seulement après découverte, topologie, directions et reconstruction. Sorties documentaires candidates distinctes des conditions et de l’éligibilité réelle.

| Mesure après reconstruction | Attendu | Retrouvé | Manquant | Parasite |
|---|---:|---:|---:|---:|
| Groupes textuels (ensembles exacts de tokens) | 9 | 9 | 0 | 0 |
| Relations dirigées et étiquettes | 12 | 12 | 0 | 0 |
| Combinaisons de conditions (nœud/texte brut/branche) | 8 | 8 | 0 | 0 |
| Chemins complets documentaires candidats | 7 | 7 | 0 | 0 |

Les5tokens sans groupe sont les5labels de branche, pas5nœuds perdus. Trois jonctions extraites des pixels conservées;7directions par pointe et5par convention de port question,1trait isolé UNKNOWN. Les7chemins donnent3sorties NON,2ELIGIBLE,2CONTACT, sans éligibilité réelle.

### Groupes découverts (rôles après reconstruction)

| ID local | Caption OCR brute regroupée | Rôle candidat | Cadre raster |
|---|---|---|---|
| ocr-node-00 | NON / ELIGIBLE | OUTCOME | [304, 1445, 382, 1484] |
| ocr-node-01 | J'installe un variateur de / vitesse sur un moteur / déjà existant? | ENTRY | [442, 1114, 584, 1168] |
| ocr-node-02 | Le moteur existant est / déjà équipé d'un / variateur de vitesse? | CONDITION | [442, 1196, 584, 1250] |
| ocr-node-03 | Le moteur est de classe IE2 | CONDITION | [518, 1364, 677, 1404] |
| ocr-node-04 | Contacter votre / correspondant CEE / centre | OUTCOME | [526, 1452, 670, 1504] |
| ocr-node-05 | Moteur asynchrone? | CONDITION | [614, 1268, 738, 1292] |
| ocr-node-06 | Le moteur est de classe IE3 / ou IE4 | CONDITION | [677, 1364, 836, 1404] |
| ocr-node-07 | J'installe un variateur de / vitesse sur un moteur / neuf? | ENTRY | [718, 1114, 862, 1168] |
| ocr-node-08 | ELIGIBLE | OUTCOME | [718, 1472, 796, 1496] |

## Contre-épreuves et corrections

- Première qualification : le token T96 « centre » n’obtenait aucun cadre individuellement; deux chemins CONTACT restaient UNKNOWN. Régression synthétique rouge/verte : rattachement uniquement à un cadre déjà découvert contenant le token de manière unique.
- Revue P1 : un token NON dans deux cadres imbriqués était rattaché à tort au cadre extérieur. Régression rouge/verte; `ambiguous_nodes` distingue plusieurs cadres d’un cadre absent; ambiguïté conservée et état texte UNKNOWN propagé au cadre concerné. Ni NON ni ELIGIBLE ambigu ne deviennent une sortie qualifiée.
- Route entrante retirée : ancienne inférence créait4fauxchemins. Régression rouge/verte; inférence limitée à la bande supérieure des questions du layout descendant. Mesure finale :4chemins manquants,0faux. Un léger décalage OCR d’un pixel est couvert par une autre régression rouge/verte; les deux entrées restent candidates.
- T89 sans relecture :6chemins candidats manquants,0faux; le brut Iño et UNKNOWN persistent.
- T96 retiré :2chemins candidats manquants,0faux; la sortie correspondant CEE n’est pas affirmée.

La frontière de validité reste étroite : cadres axiaux avec texte OCR à150DPI,32tokens maximum, captions/questions et flux descendant. Une absence dans l’OCR brut peut empêcher de découvrir un cadre ou une négation; le lecteur ne prouve pas encore la couverture de toute l’encre du texte. Les résultats ne déclarent jamais une analyse complète ni une admission des sources.

## Preuves et vérification finale

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/node-discovery/` (`prove.py`, `qualification.json`, copies immuables hachées, contre-épreuves incluses, `source-final.log`, contrôles et hashes). Suite globale finale : **2489/2489**, aucun échec/ignoré, 19 avertissement(s), 1457.25s, couverture **88.16%** (seuil85,50% inchangé). PostgreSQL tmpfs dédié retiré après contrôle identité/label/absence de volume/localhost et absence finale vérifiée.

SHA-256 de la qualification finale : `05fa96a505157134c43947f6277ee193b7090ac6946165d168b0dc783f52a621`.

## Méthode et outils employés

Superpowers using-superpowers/brainstorming (cadrage borné), writing-plans/executing-plans (plan et preuve persistante), test-driven-development (rouges/verts), requesting-code-review (revue indépendante et corrections), verification-before-completion; ECC verification-loop (types/lint/tests/couverture/scans/diff). Graphify consulté avant recherche locale; code WIP ensuite vérifié directement car graphe antérieur. Basic Memory explicitement routé smart-ao-v8, miroir du plan seulement. Context7 et CLI installés consultés pour pytest-cov append/rapport agrégé; aucune dépendance ajoutée.

Pas de navigation sémantique Serena nécessaire pour les fichiers précis concernés. Jev/Manus non requis pour ce regroupement géométrique et vocabulaire documentaire fermé. OpenDesign/Impeccable/navigateur inapplicables sans changement UI; REA inapplicable à ce code source disponible et à cette extraction de document. Aucune qualification live/de production, aucun déploiement/VPS, effet P3, dépôt externe, push ou GO public.


### Gates locales finales

- TDD rouge/vert observé pour regroupement, entrée sans rôles, ligne basse, ambiguïté imbriquée, liaison entrante absente et décalage OCR1pixel. **21nouveauxcas /188ciblés** (17lecteur nœuds,22décodeur,30topologie,23assemblage,39pointes,57projection).
- Backend entier : **2489réussites**,0échec/0ignoré;cov88.16%,1457.25s. 19avertissements Starlette/httpx et Pydantic répétés par lots; aucun seuil diminué. Deux campagnes volontairement interrompues pour corrections de revue et une campagne arrêtée par OOM système à63% sont conservées (`backend-global-interrupted*.log`, `backend-global-oom.log`) et ne valent pas PASS. La suite finale exhaustive est exécutée en lots disjoints de8fichiers (manifestes/hashes/JUnit), couverture cumulée via pytest-cov et seuil final85,50% appliqué après tous les lots. Aucune configuration/seuil du dépôt n’a été changé; contrôle de couverture par lot différé au gate agrégé. Le PostgreSQL jetable est borné768MiB,shared_buffers32MiB,WAL128MiB/checkpoint30s,BLAS/OMP1thread pour réduire la pression mémoire; aucun runtime de production modifié.
- Ruff global `backend scripts`,format1205fichiers,mypy621sources : verts; `git diff --check` vert, whitespace des nouveaux fichiers vérifié.
- Semgrep1.179.0 `p/security-audit`,225règles configurées,5fichiers Python explicitement analysés,0finding/0erreur,métriques désactivées; Bandit3fichiers applicatifs et detect-secrets5fichiers (`--all-files --no-verify`) sans alerte. Ces scans ciblés ne qualifient pas tout le dépôt ni une exploitation live.
- Revue indépendante : ambiguïté P1, fausse entrée et jitter P2 reproduits/corrigés/revérifiés; aucun nouveau défaut bloquant identifié dans le delta. 32fichiers hérités inchangés;5fichiers logiciels intégrés avec hashes comparés depuis le worktree géré. Aucun changement de dépendance,API,schéma ouUI. WIP non commité, aucun push.
- Tenant/document/version/page/source/render stricts; déterminisme, provenance, OCR brut, négations, labels, correspondant CEE et états inconnus conservés. Aucune commande humaine, autorisation P3/P5, export ou admission n’est produite par cette extraction candidate.

**Prochaine étape :** ESSAIS DCE — qualifier la couverture OCR des cadres CEE de Cadarache depuis l’encre raster, détecter les mots, négations ou cadres sans texte manquants et requalifier leurs chemins sans affirmer une analyse complète; conserver sources, correspondant CEE, UNKNOWN et REVIEW_REQUIRED. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
