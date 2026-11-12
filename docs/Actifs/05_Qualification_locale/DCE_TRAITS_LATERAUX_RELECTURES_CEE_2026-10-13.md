# ESSAIS DCE — traits latéraux et relectures natives

## Cadrage

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Cinq lignes candidates dans quatre cadres/14 régions, 20 lectures directes divergentes. Les traits latéraux deviennent des glyphes OCR. Douze occurrences altérées et 28 omissions restent UNKNOWN.

**Risques :** prendre I/l/1 ou NON pour un trait ; accepter la géométrie comme preuve sémantique ; réutiliser une revue sur pixels modifiés ; ignorer les régions non lues ou transférer une preuve native vers une variante.

**Insertion :** preuve privée uniquement ; aucun changement produit, migration, dépendance, UI ou contrat. PDF original p.42, xref168/occurrence35 ; crops natifs complets et régions du checkpoint précédent.

**Plan minimal :** mesurer continuité des colonnes latérales et jonction supérieure dans le cadre complet ; refuser raccord/trait partiel ; borner les recadrages à une revue technique locale indépendante liée au hash RGB et à la région exacte, sans acte humain simulé ni admission ; lire directement RGB/gris via RapidOCR et Tesseract ; conserver les pixels latéraux dans des régions parentes ancrées ; inventorier tout non-lu ; requalifier 12/28 sans transfert, puis revue/contrôles/docs/miroir.

**Tests :** rectangle continu, raccord entrant, bordure interrompue, I isolé sans rectangle, géométrie sans revue, NON ajouté au bord, coupe élargie dans le texte. Aucune lecture attendue n'entre dans le helper ou la revue géométrique. Un candidat géométrique n'autorise jamais seul une exclusion.

Méthodes : PDF ; Superpowers diagnostic/TDD/revue/vérification ; ECC eval-harness. M2-026/027/029 et CT31-02 conservés. Pas de backend live, VPS, déploiement, P3, dépôt externe, push, corpus supplémentaire ou GO public. A1 non admis, A2 générique HOLD, NO-GO public maintenus.

## Résultat local PARTIAL

Source DCE-03 / CEA Cadarache / CCTP commun indice2 / annexe13 p.42 : PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEG xref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Chaque cadre, ligne et recadrage conserve page/région native/crop/hash ; aucun resize avant OCR, aucune substitution I/l/1.

**Quatre recadrages candidats qualifiés techniquement pour cet essai local ; une ligne refusée.** La géométrie exige une jonction supérieure sur au moins90% de la largeur, continuité sur au moins90% de la hauteur du cadre et100% de la ligne, sans colonne latérale partiellement occupée ni encre dans la séparation de3px. Cette règle propose un candidat ; elle ne prouve pas sa sémantique. Une revue technique Codex liée aux pixels RGB/hash/région exacts, contrôlée visuellement indépendamment, est exigée avant son utilisation. Ce fichier local n'est ni une signature authentifiée, ni un acte humain métier, ni une autorisation produit ou d'admission.

| Ligne | Bbox relative au cadre complet, avant → après | Disposition |
|---|---|---|
| IE2 / T90 | [0,22,339,40] → [3,22,338,40] | Candidat local relu |
| Asynchrone / T88 | [0,17,265,41] | Refus : raccord entrant, aucun recadrage ni OCR frais |
| IE3 / T91 | [0,22,339,40] → [5,22,339,40] | Candidat local relu |
| ou IE4 / T92 | [0,52,339,70] → [5,52,339,70] | Candidat local relu |
| ELIGIBLE / T98 | [0,19,167,39] → [5,19,166,39] | Candidat local relu |

La revue visuelle indépendante des quatre cadres et des **six strips** confirme des traits verticaux, aucun mot ni glyphe distinct visible dans ces strips. Elle ne qualifie aucune règle sémantique générale. Les strips sont extraits séparément et conservés ; corps + strips reconstruisent exactement les pixels des quatre lignes parentes. **372 pixels d'encre détectée BT601<180** sont conservés dans ces bandes latérales, hors des entrées OCR ; aucun pixel original n'est détruit.

### Lectures directes

**16 lectures fraîches** : RapidOCR sans détecteur, RGB puis gris/autocontraste, et Tesseract français PSM7 sur les mêmes recettes. La référence attendue est utilisée après toutes les lectures. **Zéro accord complet** sur les trois cadres relus ; asynchrone reste refusé. Les états de source et de texte restent UNKNOWN/REVIEW_REQUIRED.

- IE2 : RapidOCR reste `lE2` ; Tesseract conserve des glyphes parasites et espaces absents.
- IE3 : Tesseract lit `IE3`, RapidOCR `lE3`.
- Deuxième ligne : `OUIE4`, `OU IE4`, `ou IE4`, `oulE4` selon la recette ; aucune correction lexicale.
- ELIGIBLE : trois lectures concordent, Tesseract RGB ajoute `L'` ; pas de sélection de la recette favorable.

Les franges colorées plus claires que le seuil180 restent dans le corps lu : exemples IE2 bord gauche RGB(187,204,212), IE3 RGB(200,217,227). Leur présence est observée ; leur responsabilité dans chaque erreur n'est pas prouvée par cette seule observation. Aucune extension du cut vers ces pixels n'est autorisée par le contrôle de continuité actuel.

### Inventaire non lu et requalification

Les **neuf régions UNREAD précédentes et leurs 5056 pixels d'encre détectée** restent ancrées, conservées et UNKNOWN ; leurs fichiers/scopes/hashes sont repris. Les six strips sont inventoriés séparément comme traits techniquement revus dans ce contexte local ; la ligne asynchrone refusée demeure dans son parent. Le texte du cadre complet n'est pas déclaré extrait.

Les **douze occurrences altérées et les 28 omissions** restent UNKNOWN/REVIEW_REQUIRED. Requalification liée aux hashes des lectures et des résultats antérieurs : 35/63 chemins sur neuf variantes préservantes, sans extraction fraîche des17variantes, sans transfert depuis le crop natif ni promotion de source. Correspondant CEE conservé, aucune éligibilité réelle ou admission Golden DCE.

## Tests et revue

- TDD : quatre assertions rouges initiales puis correction minimale ; bordure interrompue refusée après une rouge spécifique. La revue a démontré qu'une décision REFUSED pouvait passer le garde : régression rouge puis correction exigeant décision positive exacte, reviewer technique, UNKNOWN/admissionfalse. **9/9 tests de cette tranche**, **28/28 privés** avec les preuves mapping/partition/sélection précédentes.
- **126/126 ciblés produit**, 10,70 s : OCR coverage/topologie/discovered/conditional. **39 hashes logiciel inchangés**, aucun produit/contrat/dépendance/schéma modifié.
- Ruff/compile verts. Semgrep1.179.0, `p/security-audit`, **225 règles/3 scripts**, zéro finding/erreur/timeout. Code et résultats restent locaux, métriques désactivées.
- Revue indépendante : images complètes + six strips, hashes/crops/16 entrées OCR, reconstruction exacte et garde décision positive ; aucun défaut supplémentaire. Scripts figés puis lectures relancées après renforcement du contrôle occurrence/hash de ligne.
- Receipt privé : **152 références SHA-256** : PDF/image/mappings/runtime/modèles précédents, revue technique locale, scripts, corps/strips/lectures/requalification/scan. La revue technique lie les pixels et décisions, sans prétendre authentifier une autorité humaine.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-side-trials/` : `side_crop.py`, `test_side_crop.py`, `read_sides.py`, `technical-review.json`, `readings.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout principal ; tests `--noconftest --no-cov`, script `PYTHONPATH=backend`. Essai initial archivé ; les résultats courants correspondent aux scripts finaux. Aucun runtime ou modèle ajouté.

## Limites

Quatre recadrages expérimentaux locaux n'autorisent aucune exclusion sur une autre image, ligne, version ou tenant. Géométrie seule insuffisante ; contre-exemples de glyphes/négation et changement de scope refusés. Les glyphes I/l/1 et les franges claires restent non qualifiés. Globalbackend2544/2544/couverture88,24% antérieur non relancé, produit inchangé. WIP non commité ; aucun UI/backendlive/VPS/déploiement/P3/dépôtexterne/push/GO public. A1 non admis, A2 générique HOLD, NO-GO public maintenus.

Skills appliquées : PDF, Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion, ECC eval-harness ; Graphify consulté et cahiers actifs vérifiés. Les résultats techniques ne valent ni admission source ni validation métier humaine.

## Correction de méthode — 14 octobre 2026

La marge dite blanche des recettes RGB paddées de cette preuve était **rouge RGB(255,0,0)** : `ImageOps.expand(...,fill=255)` sur RGB. La marge grayscale était blanche. Les hashes, géométries et textes bruts restent exacts ; la description de couleur et la qualification comme essai RGB avec marge blanche sont corrigées. Les refus UNKNOWN demeurent, aucune source n’était admise. Ces lectures ne prouvent pas seules que leurs parasites venaient du PDF. Les fichiers historiques sont conservés sans réécriture ; la comparaison corrigée à coupe identique et sa portée sont dans [Franges/padding et relectures corrigées](DCE_FRANGES_PADDING_RELECTURES_CEE_2026-10-14.md). Pas de relecture globale rétroactive des neuf cadres ni transfert aux variantes.
