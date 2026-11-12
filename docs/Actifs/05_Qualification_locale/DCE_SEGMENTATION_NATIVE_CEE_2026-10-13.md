# ESSAIS DCE — segmentation et relectures natives CEE

## Cadrage

**AS-IS :** checkout principal, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Neuf mappings natifs prouvés ; quatre cadres divergents (T90, T88, T91/T92, T98). Douze occurrences altérées et 28 omissions encore inconnues.

**Risques :** effacer NON ou une ponctuation en prenant le texte pour une bordure ; substituer I/l/1 ; sélectionner seulement une lecture favorable ; transférer l'OCR natif vers un raster altéré ; confondre une qualification technique avec l'admission de source.

**Insertion :** uniquement scripts et preuves locales privées ; lecteurs produit inchangés. PDF original/page42/xref168/occurrence35, régions/hashes repris de la preuve native précédente. M2-026/027/029 exigent source/version, inconnu explicite et refus de complétude d'une pièce critique non qualifiée.

**Plan minimal :** conserver chaque bande contenant de l'encre détectée (BT601 entier, seuil180), y compris les traits ressemblant à des bordures ; découper uniquement sur les espaces horizontaux ; vérifier couverture et hashes ; lire les bandes via RapidOCR et Tesseract avec paramètres figés ; comparer après toutes les lectures ; requalifier les douze scopes et les 28 omissions sans transfert ; contrôles, plan/index et miroir.

**Tests :** NON séparé de ELIGIBLE, négation orange, trait horizontal conservé, bordure verticale empêchant une fausse séparation, cadre vide inconnu. Un trait ne devient pas une bordure prouvée par la seule géométrie : aucune exclusion sémantique prévue sans preuve indépendante. L'image originale reste intacte ; les régions non lues sont explicitement conservées dans leur parent.

Méthodes : PDF, Superpowers diagnostic/TDD/vérification, ECC eval-harness. Pas de UI, migration, dépendance nouvelle ni effet métier. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Résultats et provenance

Les quatre crops natifs ont été segmentés en **cinq bandes**, puis relus par RapidOCR RGB, Tesseract français RGB (PSM7), RapidOCR gris/autocontraste et Tesseract gris/autocontraste. **20 lectures fraîches**, paramètres figés, sans resize du crop. Chaque bande conserve source PDF/page42/xref168/occurrence35, région native, crop parent et SHA-256 de crop/entrée OCR. Les recettes de gris restent des transformations explicitement hashées, pas une preuve d'identité de pixels avec l'original.

| Cadre | Segmentation / résultat | Décision |
|---|---|---|
| T90 — IE2 | Deux bandes : trait supérieur conservé et texte ; lE2/1E2/IE2 divergent | UNKNOWN |
| T88 — asynchrone | Bord vertical continu : une bande ; Tesseract ajoute `\|` | UNKNOWN |
| T91/T92 — IE3 ou IE4 | Une bande : bord continu empêche de séparer les lignes sans exclusion ; Tesseract perd la seconde ligne en PSM7 | UNKNOWN |
| T98 — ELIGIBLE | Une bande ; Tesseract gris concorde, RGB lit `\| eue \|` | UNKNOWN |

**0/4 accords complets** entre les quatre lectures. Toutes les bandes, y compris celles ressemblant à un trait de cadre, entrent dans la comparaison. Aucun choix opportuniste de recette, aucune substitution I/l/1, aucun effacement de texte. **Zéro pixel de bordure exclu.** La géométrie seule ne qualifie pas la nature sémantique d'un trait.

La conservation vérifiée concerne les pixels d'encre détectés au seuil BT601<180, pas tous les pixels clairs : zéro pixel détecté hors des bandes. Le parent original reste intact et tous les pixels hors bandes demeurent dans ce parent, sans admission ni conclusion de complétude. Une bordure continue peut empêcher une segmentation utile ; le helper refuse de la contourner.

Les douze occurrences altérées gardent leur scope/render_sha256 et UNKNOWN/REVIEW_REQUIRED. Requalification par relecture des preuves du rejeu antérieur, **sans nouvelle extraction des 17 variantes** : 35/63 chemins sur les neuf cas préservants, **28 omissions maintenues**, aucun transfert de preuve native. Aucun source/variant state promu ; correspondant CEE conservé.

## Vérification

- TDD : quatre assertions de segmentation observées rouges puis vertes ; cinq tests initiaux réussis. Revue : défaut de sélection silencieuse fermé par deux régressions SHA absent/doublon rouges puis vertes ; **7/7 tests privés**.
- **126/126 tests produit ciblés** couverture OCR/topologie/reconstruction découverte/chemins conditionnels, 23,26 s. Les **39 hashes produit sont inchangés** ; aucun code, contrat public, migration ou dépendance produit modifié. Compilation et Ruff des trois scripts verts.
- Revue indépendante : bandes, régions, crops, entrées OCR et coverage recalculés sans relancer l'OCR ; aucune perte détectée ni faux accord. Garde sélection vérifiée sur nominal, absent, doublon et copies d'un même SHA. Le rerun final utilise les scripts figés ; les premiers essais sont archivés non qualifiants.
- Semgrep 1.179.0, `p/security-audit` : 225 règles, 18 fichiers listés dont trois scripts Python, zéro finding/erreur/timeout. Chargement initial des règles impossible dans le sandbox ; téléchargement autorisé puis scan local réussi, métriques désactivées. Sortie JSON conservée depuis stdout ; fichiers binaires/PNG hors analyse sémantique.
- Receipt privé lie scripts, sélection, résultats, bandes/entrées OCR, mapping précédent, PDF, images originales, runtime/modèles et versions SDK par SHA-256. La sélection contient uniquement les hashes des crops divergents ; les références textuelles servent au grading après toutes les lectures.

Preuves : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-line-rereads/` (`native_lines.py`, `test_native_lines.py`, `read_lines.py`, `selection.json`, `readings.json`, `requalification.json`, `receipt.json`). Depuis le checkout principal : Python `.venv`, tests privés `--noconftest --no-cov` ; script avec `PYTHONPATH=backend`. Le runtime privé existant suffit, aucune dépendance ajoutée.

## Limites

Qualification locale PARTIAL : les quatre cadres natifs et les douze occurrences altérées restent UNKNOWN/REVIEW_REQUIRED. Les 28 omissions ne sont pas résolues. PSM7 perd du texte sur une bande multilignes : cette divergence est conservée, pas normalisée. La suite globale antérieure 2544/2544/couverture88,24% n'a pas été relancée dans cette tranche, produit inchangé. Pas de UI, backend live, VPS, déploiement, P3, dépôt externe, push ou GO public. WIP conservé/non commité ; A1 non admis, A2 générique HOLD, NO-GO public maintenus.

Skills appliquées : PDF, Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion, ECC eval-harness. Graphify consulté ; navigation sémantique et UI inapplicables. Les tests privés prouvent la conservation et les refus ; ils ne prouvent pas une éligibilité CEE réelle ni la complétude d'un DCE.

## Correction de méthode — 14 octobre 2026

La marge dite blanche des recettes RGB paddées de cette preuve était **rouge RGB(255,0,0)** : `ImageOps.expand(...,fill=255)` sur RGB. La marge grayscale était blanche. Les hashes, géométries et textes bruts restent exacts ; la description de couleur et la qualification comme essai RGB avec marge blanche sont corrigées. Les refus UNKNOWN demeurent, aucune source n’était admise. Ces lectures ne prouvent pas seules que leurs parasites venaient du PDF. Les fichiers historiques sont conservés sans réécriture ; la comparaison corrigée à coupe identique et sa portée sont dans [Franges/padding et relectures corrigées](DCE_FRANGES_PADDING_RELECTURES_CEE_2026-10-14.md). Pas de relecture globale rétroactive des neuf cadres ni transfert aux variantes.
