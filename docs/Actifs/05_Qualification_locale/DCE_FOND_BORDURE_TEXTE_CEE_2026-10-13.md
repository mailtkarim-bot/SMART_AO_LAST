# ESSAIS DCE — séparation fond/bordure/texte CEE

## Cadrage

**AS-IS :** checkout principal SMART_AO_V8,branche `codex/reconcile-smartao-20261009`,HEAD `30f26934430095632000a1d82519f61dbb4c6411`.39SHA logiciels conformes au checkpoint2544tests/cov88,24%. Douze occurrences de cadres UNKNOWN,28omissions de chemins ;35/63chemins et69/81concordances sur neuf variantes nominales. WIP conservé.

**Risques :** assimiler un pixel orangé à du fond sans preuve, masquer une négation ou un point, confondre absence de contact avec absence de sens, choisir une recette OCR d'après la référence, transférer une lecture à une autre région. Les sources restent non admises.

**Points d'insertion :** preuves locales de composantes et relectures natives ; lecteurs existants seulement si un défaut corrigeable est démontré. Le point non couvert `(307,1450)` de contraste1.05 est isolé sous le masque180 ; son origine fond/glyphe reste indécidable par ce seul constat.

**Plan minimal :** (1) décrire chaque région non couverte, composantes et contacts avec le contour sur les pixels exacts ; (2) relectures des douze cadres depuis chaque crop avec recettes fixes et hashes, sans texte attendu dans OCR ; (3) contre-exemples de NON/ponctuation/coloration proche du fond et preuve de refus lorsque les images ne permettent pas de séparer les origines ; (4) comparer les lectures après extraction, requalifier les28omissions ; (5) revue, contrôles, plan/index/miroir.

**Tests :** composante isolée vs composante reliée à un contour, gris/RGB180strict, hash/scope/locator exacts, négation hors/à l'intérieur des boîtes, pixel ponctuation de même couleur que bruit de fond, lectures vides/divergentes. Aucune exclusion d'encre ni levéeUNKNOWN sans preuve. Aucune substitution I/l/1.

Superpowers using-superpowers/systematic-debugging/TDD et ECC python-testing/verification ; Graphify consulté (graphe historique), vérification des fichiers WIP ensuite. Aucun changementUI/schéma/dépendance produit prévu. A1nonadmis,A2HOLD,NO-GOpublic ;aucunbackend live,corpus supplémentaire,VPS,déploiement,push,P3,dépôtexterne.

## Résultat de la qualification

**Séparation sémantique non qualifiée : aucun pixel non couvert n'est exclu.** La connectivité4voisins décrit une structure, pas une origine fond/bordure/texte. Le pixel `(307,1450)` de contraste1.05 est une composante isolée, RGB `(255,155,100)` ; sa couleur ne suffit pas à prouver qu'il est dispensable. Les autres points non couverts peuvent appartenir à des composantes de plusieurs pixels, sans contact avec la bande de bord. Les57diagnostics recalculés restent UNKNOWN.

Deux images identiques peuvent représenter un bruit de fond ou une ponctuation manquante : ces seules entrées ne permettent pas des verdicts opposés. Les contre-exemples de négation noire/orange et de pixel ponctuation utilisent le vrai lecteur et un OCR simulé omettant l'encre : celui-ci reste refusé par UNCOVERED_INK. Ils prouvent le refus, pas une reconnaissance native d'une négation réelle.

Douze cadres relus :**36lectures fraîches**,recettes fixes RGBscale6 et gris/autocontrast/pad8scale6 surRapidOCR3.9.2,plusRGBscale6/Tesseract5.3.4fra+eng. **0/12accords complets**,7/12avec au moins unelecture concordante. Aucun vote majoritaire,choix depuis la référence ou substitution I/l/1. Tous les bruts,scores,crops etlocators sont conservés ; aucune source promue.

| Variante | Tokens | Motif initial | Lectures concordantes /3 | Verdict |
|---|---|---|---:|---|
| brightness_0.97 | T94, T93 | UNCOVERED_INK | 2 | UNKNOWN / REVIEW_REQUIRED |
| brightness_0.97 | T91, T92 | REREAD_FAILED | 1 | UNKNOWN / REVIEW_REQUIRED |
| brightness_0.97 | T98 | UNCOVERED_INK | 2 | UNKNOWN / REVIEW_REQUIRED |
| contrast_1.05 | T94, T93 | UNCOVERED_INK | 2 | UNKNOWN / REVIEW_REQUIRED |
| blur_035 | T91, T92 | TEXT_DISAGREEMENT | 0 | UNKNOWN / REVIEW_REQUIRED |
| jpeg_85 | T90 | TEXT_DISAGREEMENT | 0 | UNKNOWN / REVIEW_REQUIRED |
| jpeg_85 | T91, T92 | TEXT_DISAGREEMENT | 0 | UNKNOWN / REVIEW_REQUIRED |
| jpeg_85 | T98 | UNCOVERED_INK | 2 | UNKNOWN / REVIEW_REQUIRED |
| resample_0.9 | T83, T85, T86 | TEXT_DISAGREEMENT | 2 | UNKNOWN / REVIEW_REQUIRED |
| resample_0.9 | T91, T92 | TEXT_DISAGREEMENT | 0 | UNKNOWN / REVIEW_REQUIRED |
| resample_1.1 | T90 | TEXT_DISAGREEMENT | 2 | UNKNOWN / REVIEW_REQUIRED |
| resample_1.1 | T91, T92 | TEXT_DISAGREEMENT | 0 | UNKNOWN / REVIEW_REQUIRED |

## Rejeu des chemins

Les17cas ont été rejoués sur le même gel logiciel, après ces lectures sans promotion. Résultat inchangé :**35/63chemins,28omissions,3/9variantes nominales,69/81concordances,0faux chemin/affirmation critique interdite**. Les effacements NON/asynchrone/centre et la contradiction OUI/NON restent refusés ; correspondant CEE et éligibilité réelle UNKNOWN sont conservés. Les28omissions ne sont pas corrigées.

## Provenance et revue

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/foreground-trials/`. Qualification.json etreceipt.json lient crops,script réellement exécuté,helper,références de résultats sources,runtime/modèles Tesseract,versionsSDK etgel39SHA logiciels. Aucune mutation des pixels. Les captions sont comparées seulement après les36lectures. Les ancres des composantes sont exclusives ; chaque point est vérifié dans son cadre.

La première analyse incluait une ligne/colonne au-delà des bornes exclusives et le script avait été reformaté après exécution. Cette preuve initiale est archivée nonqualifiante,avec sonSHA etla raison dansinitial-proof-note.json. Les12cadres ont été relus entièrement surle script corrigé etfigé. La revue indépendante confirme36crops/scopes/hash et57diagnostics ; aucun fond/texte accordé par ce helper.

## Contrôles

- Trois tests de composantes rouges (fonction absente) puisverts ; trois refus de négation/ponctuation :**6/6privés**.
- **126/126tests existants ciblés**,coverage/topologie/reconstruction/chemins ;huitassertions du vrai grader. Rejeu17cas natifs complet.
- Ruff surhelper/tests,compilation des scripts,diffcheck verts. Semgrep1.179.0,225règles/4scripts :0finding/0erreur ; unerègle boto3 hardcoded-token atteint unfixpointtimeout surqualify_frames.py,scanpartiel pourcetterègle.
- **Code produit inchangé :39SHA conformes au checkpoint2544/2544,cov88,24%.** Cette suiteglobale n'est pas relancée ici ; aucune baseDB ni migration requise pour cette qualification privée. Aucun changementAPI/UI/dépendanceproduit ; les scripts sont des preuves locales, pas un nouveau classificateur produit de fond.

## Limites et suite

Distinguer les origines d'un pixel isolé nécessite une information supplémentaire fiable ; la seule luminance/couleur/connectivité et les lectures divergentes ne suffisent pas. Les crops agrandis n'ajoutent pas les détails perdus au raster150DPI. Prochaine preuve : établir un mapping vérifiable vers les images originales incorporées auPDF et lire leur résolution native ; ne pas rebindercette preuve surunrasteraltéré sans contrôle explicite.

A1nonadmis,A2HOLD,NO-GOpublic ;UNKNOWN/REVIEW_REQUIRED sansadmission,WIPnoncommité,aucunpush/backendlive/corpussupplémentaire/UI/VPS/déploiement/P3/dépôtexterne.
