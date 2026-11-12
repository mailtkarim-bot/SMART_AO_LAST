# ESSAIS DCE — franges et correction de marge OCR

## Cadrage

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Quatre recadrages candidats/16lectures divergentes, un raccord refusé ; sources et hashes inchangés. La reprise révèle que la marge RGB annoncée blanche dans les essais privés était rouge : Pillow `fill=255` produit RGB(255,0,0). La marge grayscale reste255/blanche. Les résultats et hashes bruts antérieurs sont conservés, mais leur qualification comme comparaison RGB avec marge blanche est invalide.

**Risques :** attribuer au PDF un artefact ajouté par le harness ; masquer une négation pâle ou normaliser I/l/1 ; extrapoler une concordance sur une recette corrigée à une source entière ou un raster altéré.

**Insertion :** nouvelle preuve locale privée, aucune modification du produit. Lecteur produit `diagram_ocr_coverage` utilise la marge en grayscale, non touché par ce défaut RGB. Images/coupes/revue techniques exactes du checkpoint précédent conservées.

**Plan minimal :** regression rouge→verte sur vraie marge blanche et conservation de pixels ; comparer RGB marge rouge témoin, RGB marge réellement blanche et gris marge blanche, à coupe native identique ; contrôler couleurs et corps des entrées ; inventorier les franges sans masque ni extension du cut ; contre-exemple de négation pâle ; corriger les affirmations historiques de marge sans réécrire les résultats ; requalifier 12/28 sans transfert, revue/contrôles/docs/miroir.

**Tests :** paddingRGB blanc, paddinggray blanc, NON pâle au bord intact. Un choix de couleur seul ne peut qualifier trait vs glyphe : le même RGB de frange peut être utilisé dans une négation, qui doit rester intacte. Tout masque et toute extension de coupe sont refusés faute de preuve sémantique.

Méthodes : PDF, Superpowers diagnostic/TDD/revue/vérification, ECC eval-harness ; Context7 Pillow et observation de Pillow12.3.0 installé. M2-026/027/029, provenance CT31-02, UNKNOWN et admissionfalse maintenus. Aucun backendlive/UI/VPS/déploiement/P3/dépôtexterne/push ou GO public.

## Résultats vérifiés

Source originale DCE-03 Cadarache/CCTP commun indice2/annexe13/p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Les quatre crops, leurs coupes et la revue technique locale antérieure sont inchangés. Corps de chaque entrée OCR conservé byte-exact ; aucune extension de coupe, aucun masque de frange.

**24 lectures fraîches : 16 avec marge blanche réelle et8 avec marge rouge témoin.** RapidOCR sans détecteur et Tesseract français PSM7, mêmes pixels de corps/recadrage, recettes RGBblanc/RGBrouge/grisblanc définies avant lecture. Les quatre bords de chaque entrée sont vérifiés pixel par pixel ; le corps RGB ou grayscale est exactement celui de sa recette. Le grader blanc utilise indices0/1/4/5 exclusivement, la référence est comparée après toutes les lectures. Aucun choix de résultat favorable.

| Corps | RGB blanc (Rapid / Tesseract) | RGB rouge témoin (Rapid / Tesseract) | Gris blanc (Rapid / Tesseract) |
|---|---|---|---|
| IE2 | lE2 / parasites et lE2 | lE2 / parasites et IE2 | lE2 / parasites et lE2 |
| IE3 | lE3 / IE3 | lE3 / IE3 | lE3 / IE3 |
| ou IE4 | ouIE4 / ou IE4 | OUIE4 / OU IE4 | ou IE4 / oulE4 |
| ELIGIBLE | ELIGIBLE / \| ELIGIBLE | ELIGIBLE / L'ELIGIBLE | ELIGIBLE / ELIGIBLE |

Les textes complets bruts et scores sont dans `readings.json`. **Zéro accord complet blanc** sur les trois cadres relus ; asynchrone toujours refusé, aucune lecture fraîche de son raccord. Le contrôle isole l'effet de la marge sur cette exécution (notamment casse/parasites), sans prouver qu'elle explique toutes les erreurs. I/l/1 ne sont pas remplacés.

## Séparation frange/glyphe : refus qualifié

Diagnostic seulement : luminance entière180000≤299R+587G+114B<235000 etG−R≥10,B−R≥10. Ce critère de bleu pâle retrouve respectivement1019/979/227/0pixels dans les quatre crops ; il touche aussi des glyphes. Le contre-exemple synthétique **NON RGB(187,204,212)** contient66pixels satisfaisant ce même critère. La couleur seule ne peut donc établir une classe « bordure ». Le0 sur ELIGIBLE ne prouve pas l'absence de frange verte : ce diagnostic vise seulement le bleu pâle.

Aucun de ces pixels n'est masqué ou reclassé sémantiquement. Les crops/inputs et le contre-exemple ont source/région/hash explicites ; la négation pâle au bord est conservée byte-exact dans les tests. Ces contre-exemples prouvent la conservation des pixels, pas la reconnaissance OCR fiable de toute négation. **Séparation sémantique non prouvée**, franges et glyphes restent UNKNOWN, pas de normalisation de texte ni nouvelle coupe.

## Correction historique et requalification

Les quatre dossiers d'images natives, segmentation native, cadres complets et traits latéraux reçoivent une correction append-only de leur description de paddingRGB. Les vieux scripts/inputs/hashes/textes restent inchangés ; seules les comparaisons explicitement annoncées « marge blancheRGB » sont invalidées comme telles. Géométrie/conservation/refus ne sont pas annulés. La preuve produit et le rejeu des17variantes utilisent du gris avant ce padding ; le lecteur produit `diagram_ocr_coverage` n'est pas touché. Les neuf cadres originaux ne sont pas tous relus dans cette tranche : l'accord5/9 historique n'est pas transformé en accord corrigé.

Les neuf régions non lues (5056pixelsencre), les sixstrips conservés (372pixelsencre) et le raccord asynchrone refusé restent dans leurs parents/ancrages exacts. Les **douze occurrences altérées et les 28omissions** restent UNKNOWN/REVIEW_REQUIRED, sans transfert natif ni nouveau rejeu des variantes. Résultats antérieurs35/63chemins sur neuf cas préservants, source et correspondant CEE conservés ; aucune source promue/admission.

## Contrôles et limites

- Régression paddingRGB rouge observée **1échec/2réussites**, puis **3/3tests** verts après `fill="white"` : RGB,grayscale,NONpâle conservé. **31/31privés** avec les preuves mapping/partition/sélection/traits précédentes.
- **126/126produit ciblés**,10,09s : couverture OCR/topologie/discovered/conditional. **39SHA logiciel inchangés** ; aucun code,contrat,migration,dépendance produit modifié.
- Ruff/compile verts ; Semgrep1.179.0,`p/security-audit`,225règles/3scripts,0finding/erreur/timeout. Analyse locale,métriquesdésactivées.
- Revue indépendante :24inputs reconstruits,hash/couleur des quatre bords/corps conformes,indices du grader blanc exacts,coupes inchangées. Elle confirme l'erreur historique de couleur et la nécessité de corriger les descriptions ; aucune promotion ni fiabilité complète déclarée.
- Receipt privé **183référenceshashées** : PDF,image,runtime,modèles,mappings/revue précédente,crops/strips,code/marges/counterexample,lectures/requalification/scan. Scripts figés avant lectures ; sources historiques préservées.

Preuves : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-fringe-trials/` : `fringe.py`, `test_fringe.py`, `read_fringe.py`, `technical-review.json`, `readings.json`, `fringe-diagnostic.json`, `counterexample-pale-NON.png`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout ; tests privés `--noconftest --no-cov`, script `PYTHONPATH=backend`. Diagnostic décrit sa formule ; il ne constitue aucun filtre produit.

Résultat PARTIAL. Suite globale2544/2544/couverture88,24% antérieure nonrelancée ici, produit inchangé. Ni franges/glyphes ni extraction complète qualifiés. WIP noncommité ; aucunUI/backendlive/VPS/déploiement/P3/dépôtexterne/push/GO public. A1nonadmis,A2génériqueHOLD,NO-GOpublic. Skills réellement appliquées : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify puis contrôles locaux,Context7Pillow. Contrôles techniques distincts d'une admission ou validation métier humaine.
