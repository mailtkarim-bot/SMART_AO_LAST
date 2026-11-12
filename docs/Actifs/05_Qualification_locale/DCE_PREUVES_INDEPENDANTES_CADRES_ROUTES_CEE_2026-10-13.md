# ESSAIS DCE — preuves indépendantes des cadres et routes CEE

## Cadrage avant modification

**AS-IS :** checkout principal SMART_AO_V8, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Les 39 hashes logiciels concordent avec le checkpoint2532tests/cov88,25%. Campagne17rasters :70/81concordances,30/63chemins/33omissions,2/9nominal ; T81 corrigé et JPEG raccord incertain bloqué. Onze occurrences de cadres et des routes restent non qualifiées.

**Risques :** substitution I/l/1, choix du texte attendu dans les références, majorité de moteurs assimilée à vérité, raccord par distance sans contact pixel, mélange de scopes/versions/crops. Une lecture indépendante divergente ne lève pas UNKNOWN. Une variation raster peut avoir réellement perdu une information ; un refus sûr n'est pas une réussite nominale.

**Points d'insertion :** campagne locale de preuves, lecteurs OCR/topologie existants si un défaut minimal est démontré. Tesseract5 sera préparé dans un runtime privé de qualification depuis les paquets du dépôt Ubuntu configuré, SHA vérifiés ; aucune installation système, aucun modèle distant pendant l'analyse et aucune nouvelle dépendance produit sans preuve de nécessité. Il fournit une famille OCR indépendante de RapidOCR pour lire les crops, pas une autorité métier.

**Plan minimal :** (1) lectures natives Tesseract depuis les rasters, recettes fixes/locators/hashes/bruts conservés, comparaison aux captions seulement après ; (2) qualifier les routes depuis l'encre et les contacts, sans références de liaisons fournies ; (3) défaut démontré : test rouge, changement borné, vert et contre-exemples ; (4) requalifier neuf cadres/sept chemins sur mêmes variantes, mesurer omissions/fauxpositifs et refus ; (5) revue, contrôles appropriés, plan/index/miroir.

**Tests à prouver :** accord indépendant réel ; divergence/refus/lecture vide ; négations, déjà, IE2/IE3/IE4, correspondant CEE conservés ; image/hash/scope/region invalides ; deux routes voisines sans contact restent inconnues ; effacements et OUI/NON contradictoires refusés ; références utilisées seulement pour grader ; aucune admission automatique.

Superpowers using-superpowers/systematic-debugging/TDD et ECC eval-harness/python-testing/verification selon les changements démontrés. Graphify consulté (graphe historique, fichiers WIP vérifiés ensuite), Context7 pour le CLI local. A1 non admis,A2HOLD,NO-GOpublic ; pas de backend live,corpus supplémentaire,UI,VPS,déploiement,push,P3,dépôt externe.

## Diagnostic mesuré et insertion retenue

Tesseract5.3.4 préparé localement : cinq paquets SHA vérifiés, extraction `dpkg-deb` sans installation système, dépendances natives résolues, modèles fra/eng locaux. Sur81cadres :60accords,sept des onze occurrences en attente concordent ; quatre divergences I/l/1 restent UNKNOWN. Un accord seul ne promeut aucune source. Les probes RapidOCR détection forcée/aspect corrigent certains crops mais régressent sur le témoin : non adoptées.

Pixel JPEG `(675,1222)` : RGB `(158,188,188)` ; Pillow179,MuPDF182. Le masque actuel<180 perd donc un contact selon la conversion choisie. Plan borné : règle de luminance RGB BT.601 explicite `299R+587G+114B < 1000*seuil`, sans quantisation ni augmentation du seuil, appliquée aux lecteurs de masque existants. Grayscale natif garde son seuil exact. Rejet des formats/canaux non qualifiés. La règle ne peint aucun pixel, ne remplit aucun gap et n'utilise pas les liaisons attendues.

Tests avant code : pont coloré réellement sous180 accepté ; gris180 et pixels RGB au-dessus180 refusés ; gap blanc reste UNKNOWN ; collision/jonction ambiguë refusée ; alfa/hash/scope/bornes inchangés. Versions de lecteurs et hashes de preuves changent pour rendre cette calibration visible. Lectures OCR divergentes et toute route sans contact restent UNKNOWN.

## Corrections prouvées

- Conversion d'encre explicite BT.601 avant quantisation sur les octets RGB, grayscale inchangé. Aucune augmentation des seuils180/190 ; aucun pont peint. Lecteurs de frames, routes, lignes et pointes utilisent la même règle ; versions et digests changent.
- Le contrat de reconstruction reconnaît exactement le nouveau détecteur de pointe v2 et le v1 historique ; tout détecteur inconnu reste refusé.
- La campagne provisoire BT.601 a révélé un faux chemin sur la réduction0.9 : distance au centre du trait4px, distance à ses pixels3px. La garde repose désormais sur les bornes des pixels, rend la route UNKNOWN et conserve la région non résolue. Aucun raccord n'est inventé. La campagne provisoire avec ce faux chemin est non qualifiante.
- Rouge/vert : pont coloré179.03, bande179.503 perdue par arrondi, contrat du nouveau détecteur, deux branches voisines d'un trait épais. Contre-exemples gris180/190exact, blanc, couleur180.216, pointes absentes/concurrentes et gap distant restent refusés. Douze nouveaux cas produit ;186tests ciblés passent.

## Requalification finale

**17cas rejoués après gel des39SHA logiciels :3/9 variantes nominales,69/81 concordances,35/63 chemins,28omissions ; aucun faux chemin ni chemin critique interdit affirmé.** Les chemins progressent de30à35, mais les concordances reculent de70à69. Cette calibration ne clôture pas la robustesse complète.

| Variante | Concordances /9 | Chemins candidats | Omissions autorisées | Faux | Refus |
|---|---:|---:|---:|---:|---|
| identity | 9 | 7 | 0 | 0 | — |
| brightness_0.97 | 6 | 2 | 5 | 0 | — |
| brightness_1.03 | 9 | 7 | 0 | 0 | — |
| contrast_0.95 | 9 | 7 | 0 | 0 | — |
| contrast_1.05 | 8 | 4 | 3 | 0 | — |
| blur_035 | 8 | 5 | 2 | 0 | — |
| jpeg_85 | 6 | 2 | 5 | 0 | — |
| resample_0.9 | 7 | 0 | 7 | 0 | — |
| resample_1.1 | 7 | 1 | 6 | 0 | — |
| erase_NON | 8 | 4 | 0 | 0 | — |
| erase_async | 8 | 1 | 0 | 0 | — |
| erase_centre | 8 | 5 | 0 | 0 | — |
| erase_first_head | 9 | 3 | 0 | 0 | — |
| contradict_T89 | 9 | 0 | 1 | 0 | DIAGRAM_BRANCH_AMBIGUOUS |
| blur_15 | 0 | 0 | 7 | 0 | LABEL_CROP_LIMIT |
| contrast_0 | 0 | 0 | 7 | 0 | LABEL_CROP_LIMIT |
| dpi_300_unqualified | 0 | 0 | 7 | 0 | TOPOLOGY_SCALE_UNQUALIFIED |

Les effacements NON/asynchrone/centre et première pointe ne restituent aucun chemin passant par les nœuds critiques altérés. Après la pointe effacée, seuls les trois chemins non affectés du moteur neuf restent candidats. T89 remplacé par NON est refusé comme ambigu. Flou fort/contraste nul sont refusés par LABEL_CROP_LIMIT dans le harness : absence d'affirmation, pas preuve autonome de refus de l'assembleur. L'échelle300reste non qualifiée.

Le correspondant CEE reste un résultat documentaire distinct, jamais une éligibilité réelle. Une route hors des sept références peut rester non résolue sur le témoin :9/7n'est pas une déclaration de graphe ou de DCE entièrement analysé.

## Disposition des onze occurrences initiales et nouvelles inconnues

Deux occurrences initiales deviennent concordantes (moteur neuf : luminosité1.03 et contraste0.95). Neuf restent inconnues. Trois occurrences auparavant concordantes deviennent UNKNOWN par UNCOVERED_INK : ELIGIBLE luminosité0.97/JPEG85, NON ELIGIBLE contraste1.05. Total final :12occurrences de cadres non concordants. Cette régression est conservée dans la mesure ; aucun pixel n'est ignoré pour retrouver un score. Sur contraste1.05, le pixel nouveauhorsboîte est localisé `(307,1450)` et conservé avec son crop ; sa qualification comme fond/bordure/texte n'est pas acquise.

Tesseract sur les crops du protocole précédent :60/81accords,sept des onze occurrences initiales corroborées et quatre divergences I/l/1. Les quatre conflits ne sont pas résolus par une substitution. Les locators de ces lectures indépendantes peuvent différer des nouveaux frames ; aucune corroboration ne se transfère automatiquement.

| Variante | Tokens | Ancien motif | Motif actuel | Accord Tesseract initial |
|---|---|---|---|---|
| brightness_0.97 | T93, T94 | UNCOVERED_INK | UNCOVERED_INK | oui |
| brightness_0.97 | T91, T92 | REREAD_FAILED | REREAD_FAILED | oui |
| brightness_0.97 | T98 | INK_AND_TEXT_AGREE | UNCOVERED_INK | oui |
| brightness_1.03 | T76, T78, T80 | TEXT_DISAGREEMENT | INK_AND_TEXT_AGREE | oui |
| contrast_0.95 | T76, T78, T80 | TEXT_DISAGREEMENT | INK_AND_TEXT_AGREE | oui |
| contrast_1.05 | T93, T94 | INK_AND_TEXT_AGREE | UNCOVERED_INK | oui |
| blur_035 | T91, T92 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | non |
| jpeg_85 | T90 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | non |
| jpeg_85 | T91, T92 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | non |
| jpeg_85 | T98 | INK_AND_TEXT_AGREE | UNCOVERED_INK | non |
| resample_0.9 | T83, T85, T86 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | oui |
| resample_0.9 | T91, T92 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | non |
| resample_1.1 | T90 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | oui |
| resample_1.1 | T91, T92 | TEXT_DISAGREEMENT | TEXT_DISAGREEMENT | oui |

Les sources brutes et sorties des deux moteurs restent dans readings.json/frame-dispositions.json. La page42du PDF n'a que309caractères natifs et n'expose ni IE3 ni neuf ; deux images incorporées sont présentes. Cette inspection confirme qu'une simple lecture du texte PDF ne fournit pas la contre-preuve des mots manquants. Une éventuelle relecture depuis l'image source devra conserver une provenance et une correspondance de locator démontrées, sans rebinder une preuve ancienne sur un raster altéré.

## Fichiers, provenance et revue

Les cinq modules modifiés sont `diagram_image_reader.py`, `diagram_topology_reader.py`, `diagram_ocr_coverage.py`, `diagram_node_reader.py` et `discovered_diagram.py`, avec quatre fichiers de tests correspondants. Développement dans le worktree du sujet, intégration après186tests et revue ciblée ; neuf fichiers changés,30hérités inchangés. Versions antérieures/diffs conservés soussoftware-before/diffs ; gel39SHA soussoftware-final-hashes.json. Aucun schéma,API métier,dépendance produit ni interface modifié.

La règle s'appuie sur les [coefficients BT.601 documentés par Pillow](https://github.com/python-pillow/pillow/blob/main/src/libImaging/Convert.c) ; le seuil est appliqué à la somme entière avant arrondi. Hypothèse : octets RGB non linéaires de ces rendus, traits axiaux150DPI et ROI fixée. Les autres profils colorimétriques ne sont pas qualifiés.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/independent-rereads/` : runtime/pkgreceipts/modèles/binarySHA/ldd,81crops et lectures Tesseract,probesnonadoptées,campagneprovisoirenonqualifiante,final17PNG/locators/labels/relations/crops,agrégat liéparSHA,dispositions ettestsrouges. Sources et références de chemins ne sont utilisées qu'après extraction pourgrader. Aucun modèle ni DCE envoyé à un service OCR distant.

Revue indépendante :512assertionsgris/RGB,contre-exemplesponts etpointes,distances réelles de traits,17résultats,39hashes,5967ancres et70crops reconstruits ; aucune divergence de scope ouSHA,aucun défautcritique restant identifié dans cette revue bornée.

## Contrôles et limites

- 186tests ciblés,sept tests de crop et huit assertions du vrai grader passent.
- Ruffbackend/scripts etformat1207fichiers,mypy622sources,diffcheck verts.
- Semgrep1.179.0,225règles surneuffichiersproduit/tests :0finding/0erreur ; une règle boto3 hardcoded-token atteint trois fixpointtimeouts dansreconstruction/coverage/topologie. Scan partiel pourcetterègle,aucune preuve générale de sécurité.
- Suite backend complète : **2544/2544**,0échec/0ignoré,29warnings,1637,54s (27min18),408fichiers/102lots disjoints ; couverture **88,24%**,seuil85,50% maintenu. PostgreSQLtmpfs384MiB,127.0.0.1 supprimé etabsencevérifiée danscleanup-receipt.json.

Les28omissions et12cadres inconnus restent ouverts,UNKNOWN/REVIEW_REQUIRED sansadmission. A1nonadmis,A2HOLD,NO-GOpublic ; WIPnoncommité,aucunpush/backendlive/corpussupplémentaire/UI/VPS/déploiement/P3/dépôtexterne.
