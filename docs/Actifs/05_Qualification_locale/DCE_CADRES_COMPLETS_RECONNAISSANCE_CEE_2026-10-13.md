# ESSAIS DCE — cadres natifs complets et reconnaissance directe

## Cadrage avant lecture

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Quatre cadres divergents ; 12 occurrences altérées UNKNOWN et 28 omissions. Les crops intérieurs contiennent encore des traits continus.

**Risques :** confondre trait et glyphes/négation ; transformer une marge géométrique en exclusion sémantique ; reconnaissance sur plusieurs lignes ; perdre les régions non lues ; modifier I/l/1 ; transférer une lecture au raster altéré.

**Points d'insertion :** qualification privée uniquement ; crops complets depuis l'image originale xref168, occurrence35, PDF/page42 exacts. Aucun changement produit/dépendance/migration/UI. Les cahiers actifs M2-026/027/029 et CT31-02 imposent provenance et inconnu, sans admission par OCR.

**Plan minimal :** (1) reconstruire quatre cadres complets depuis les coordonnées PDF ; (2) partitionner horizontalement toutes les lignes de pixels, avec core8 utilisé uniquement comme locator, jamais suppression ; (3) lire les bandes candidates via reconnaissance RapidOCR sans détecteur et Tesseract PSM7 ; conserver les régions non lues UNKNOWN ; (4) comparer après lecture, vérifier hashes/pixels/reconstruction ; (5) requalifier 12/28 sans transfert, revue/contrôles/docs/miroir.

**Tests à ajouter :** rectangle + NON isolé + ELIGIBLE, négation contre le bord, deux lignes IE3/ou IE4 avec trait vertical. Reconstruction byte-exact de la partition ; aucune région admise ni trait effacé. Tout pixel hors d'une bande lue reste dans une région ancrée non lue, état UNKNOWN.

Méthodes : PDF, Superpowers diagnostic/TDD/vérification/revue, ECC eval-harness. Context7 confirme RapidOCR use_det=False : reconnaissance directe de l'image fournie, sans detect_and_crop. Pas de corpus supplémentaire, backend live, VPS, déploiement, P3, dépôt externe, push ni GO public.

## Preuve exécutée

Source : DCE-03 / CEA Cadarache / CCTP commun indice2 / annexe13 p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, image xref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Les quatre crops complets utilisent les bounding boxes de cadres de référence, remappées vers les pixels de cette image originale, sans resize. Ce mapping décrit ces boîtes ; il ne déclare pas que toute région périphérique est une bordure.

**4 cadres / 14 régions / 5 lignes candidates / 20 lectures directes.** La partition reconstruit exactement tous les pixels RGB de chaque crop, y compris les pixels clairs, les traits et les régions non lues. Coordonnées de chaque région en pixels natifs, crop parent, source/page/xref/occurrence, hashes du crop et des entrées OCR conservés. La marge8 guide la recherche des lignes ; chaque bande exportée conserve toute la largeur, sans effacement latéral.

| Cadre | Bbox native complète | Lignes candidates | Résultat |
|---|---|---|---|
| T90 | [551, 902, 890, 988] | 1 | UNKNOWN / lectures divergentes |
| T88 | [755, 698, 1020, 750] | 1 | UNKNOWN / lectures divergentes |
| T91,T92 | [889, 902, 1228, 988] | 2 | UNKNOWN / lectures divergentes |
| T98 | [976, 1132, 1143, 1184] | 1 | UNKNOWN / lectures divergentes |

RapidOCR est exécuté avec `use_det=False`, `use_cls=False`, `use_rec=True` sur chaque bande candidate ; Tesseract français PSM7 sur les mêmes entrées RGB ou gris/autocontraste. Les recettes sont hashées séparément ; leurs transformations ne sont pas assimilées à des pixels natifs identiques. Les captions attendues servent au grading après toutes les lectures, sans correction I/l/1.

La lecture RapidOCR RGB de T90 devient « Le moteur est de classe IE2 ». Les autres lectures ajoutent des glyphes issus des traits ou conservent lE2/1E2. T91/T92 est bien séparé en deux bandes : lE3/1E3/IE3 restent divergents et la seconde donne notamment `OUIE4` au lieu de `ou IE4`. Aucune normalisation n'est autorisée. T88 et T98 restent divergents à cause des traits latéraux. **0/4 concordances complètes des lignes candidates ; aucune promotion.**

**Séparation sémantique bordure/texte non acquise.** Les neuf régions UNREAD conservent **5 056 pixels d'encre BT601<180**, non lus et non classés. Aucun pixel n'est supprimé ; aucune de ces régions n'est automatiquement appelée bordure. La partition complète ne vaut ni extraction OCR complète ni qualification de tous les mots. Le grade des lignes candidates ne porte explicitement pas sur le cadre entier, qui demeure UNKNOWN/REVIEW_REQUIRED.

## Requalification et contrôles

- Douze occurrences altérées : scopes et render_sha256 inchangés, UNKNOWN/REVIEW_REQUIRED. Les résultats antérieurs restent 35/63 chemins sur neuf variantes préservantes, **28 omissions** ; pas de nouveau rejeu des 17 variantes ni transfert de preuve native. Correspondant CEE conservé, aucune admission source ou éligibilité réelle.
- TDD : **3 tests de partition rouges puis verts** : rectangle et NON isolé, négation au bord, IE3/ou IE4 avec bord vertical. Reconstruction byte-exact et inconnu de toute région vérifiés. **19/19 privés** avec les régressions mapping/sélection précédentes.
- **126/126 tests ciblés produit**, 24,03 s : couverture OCR/topologie/reconstruction découverte/chemins conditionnels. **39 hashes produit inchangés**. Aucun code produit, contrat, dépendance ou schéma modifié.
- Ruff et compilation des trois scripts verts. Semgrep1.179.0, `p/security-audit`, **225 règles / 3 scripts**, zéro finding/erreur/timeout. Un commentaire de grading corrigé après scan ne change pas l'AST ni le comportement analysé.
- Revue indépendante sans OCR : 4 crops/14 régions/5 lignes/20 inputs vérifiés, reconstruction des pixels et hashes conformes ; aucune perte ni faux accord. Elle a identifié le commentaire ambigu de grading, corrigé puis OCR complet relancé sur le script final figé.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-complete-frames/` : `partition.py`, `test_partition.py`, `read_complete.py`, `selection.json`, `readings.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Receipt : 127 références SHA-256, dont mapping/helpers/runtime/modèles précédents, PDF/image, crops et lectures actuels. Depuis le checkout principal : Python `.venv`, tests privés `--noconftest --no-cov`, script `PYTHONPATH=backend` ; runtime local existant, réseau OCR refusé. Essai initial archivé non qualifiant après correction du commentaire ; seul `readings.json` courant qualifie les lectures.

## Limites et suite

Résultat PARTIAL : l'obstacle des bordures est localisé et la seconde ligne IE4 est relue, mais les traits latéraux et les glyphes I/l/1 empêchent une concordance sûre. Ni classification sémantique des bordures ni extraction complète prouvées ; 12 occurrences et 28 omissions maintenues inconnues. Global backend2544/2544/couverture88,24% antérieur non relancé ici, produit inchangé. Pas de UI/migration/backend live/VPS/déploiement/P3/dépôt externe/push/GO public. WIP conservé, non commité. A1 non admis, A2 générique HOLD, NO-GO public.

Méthodes réellement appliquées : PDF, Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion, ECC eval-harness ; Graphify puis vérification des fichiers et Context7 RapidOCR. Ces contrôles prouvent conservation et refus, pas admission Golden ni complétude d'un DCE.

## Correction de méthode — 14 octobre 2026

La marge dite blanche des recettes RGB paddées de cette preuve était **rouge RGB(255,0,0)** : `ImageOps.expand(...,fill=255)` sur RGB. La marge grayscale était blanche. Les hashes, géométries et textes bruts restent exacts ; la description de couleur et la qualification comme essai RGB avec marge blanche sont corrigées. Les refus UNKNOWN demeurent, aucune source n’était admise. Ces lectures ne prouvent pas seules que leurs parasites venaient du PDF. Les fichiers historiques sont conservés sans réécriture ; la comparaison corrigée à coupe identique et sa portée sont dans [Franges/padding et relectures corrigées](DCE_FRANGES_PADDING_RELECTURES_CEE_2026-10-14.md). Pas de relecture globale rétroactive des neuf cadres ni transfert aux variantes.
