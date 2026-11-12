# ESSAIS DCE — frontière spatiale frange/glyphe

## Cadrage avant toute lecture

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Marge RGB désormais blanche ; quatre recadrages/24lectures contrôlées divergentes. Couleur seule incapable de distinguer frange et NONpâle. Douze occurrences altérées/28omissions restent inconnues.

**Risques :** agrandir une coupe à partir du texte attendu ou effacer une négation pâle ; confondre la revue technique d'un crop exact avec une règle générale/admission ; lever des états sur une variante à partir de pixels natifs différents.

**Insertion :** scripts/proofs privés ; aucun code produit, dépendance, schéma, contrat ou UI modifié. SourcePDF/page42/xref168/occurrence35 et cadre natif complet conservés.

**Plan minimal :** proposer uniquement deux pixels supplémentaires sur les côtés déjà revus ; conserver verticalement la région exacte, refuser pixels d'encre sombre ajoutés ; extraire les nouvelles bandes et le corps, reconstruire le parent ; revue spatiale et visuelle indépendante avant OCR ; preuve locale liée aux hashes et décision explicite, jamais géométrie/couleur seules ; lire ancien/nouveau crop avec même vraie marge blanche, RAWRGB/gris ; inventorier le non-lu, requalifier12/28 sans transfert ; revue/contrôles/docs/miroir.

**Tests :** candidat borné, NONsombre au bord, NONpâle invalidant preuve de pixels précédente, absence/preuvePENDING refusées, côté non revu immobile, coupe différente de la preuve refusée. Le garde n'authentifie pas une signature humaine ; le fichier de preuve est un artefact technique local revu. Une preuve nouvelle doit précéder toute lecture du nouveau crop.

Méthodes : PDF, Superpowers diagnostic/TDD/revue/vérification, ECC eval-harness. Cahiers M2-026/027/029, provenanceCT31-02 et UNKNOWN maintenus. Aucun masque de couleur, remplacementI/l/1, corpussupplémentaire, backendlive/VPS/déploiement/P3/dépôtexterne/push/GOpublic.

## Qualification avant OCR

Source : DCE-03 Cadarache, CCTP commun indice2/annexe13 p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, image xref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Les coordonnées ci-dessous sont relatives au crop natif complet, lequel possède sa région/hash source ; chaque asset conserve aussi sa région en pixels natifs de l'image originale.

| Ligne candidate | Ancienne coupe | Nouvelle coupe locale |
|---|---|---|
| IE2 / T90 | [3,22,338,40] | [5,22,336,40] |
| IE3 / T91 | [5,22,339,40] | [7,22,339,40] |
| ou IE4 / T92 | [5,52,339,70] | [7,52,339,70] |
| ELIGIBLE / T98 | [5,19,166,39] | [7,19,164,39] |

La proposition est limitée à2px sur chaque côté déjà recadré, sans déplacement vertical ni création d'un nouveau côté. Tout pixel d'encre BT601<180 dans une bande additionnelle refuse le candidat ; ce seuil n'est pas une preuve suffisante pour les glyphes pâles. Le changement de pixel/hash invalide la preuve locale ; seule une revue technique positive exacte peut autoriser l'essai. Ce garde vérifie la portée d'un artefact local, pas une signature humaine authentifiée.

**Préflight sans OCR**, quatre décisions PENDING, six bandes ajoutées et corps extraits/hashés, reconstruction byte-exact des anciennes coupes. Revue visuelle indépendante des cadres complets, corps et bandes : aucun mot ni glyphe distinct visible dans ces bandes, continuité avec les franges latérales précédentes confirmée. Les décisions PENDING sont refusées par le garde. Après ce verdict et avant OCR, `proof.json` enregistre les quatre décisions positives avec date14/10,hashdupréflight et portée source/région exacte. La lecture revalide cette preuve et le helper/script de préparation figés.

**Six bandes additionnelles, 224pixels RGB conservés**, aucune suppression de l'image parent et aucun masque de couleur. La conclusion spatiale est propre à ces quatre images/coupes ; elle ne constitue pas une règle générale trait/glyphe ni une admission de source. Une négation pâle ajoutée au bord modifie le hash et interdit la réutilisation du verdict précédent, même si elle échappe au seuil180.

## Comparaison fraîche à marge blanche

**32 lectures**, ancien et nouveau crop relus dans la même exécution : chacun RapidOCR sans détecteur RGB, Tesseract français PSM7 RGB, RapidOCR gris/autocontraste et Tesseract gris/autocontraste. Vraie marge blanche8px vérifiée sur tous ses pixels, corps identique à sa recette ; aucune autre transformation ni remplacementI/l/1. Référence comparée après toutes les lectures.

| Texte local candidat | Ancien crop | Nouveau crop |
|---|---|---|
| IE2 | Aucun accord complet | **4/4 concordent : Le moteur est de classe IE2** |
| IE3 | Rapid lE3 / Tesseract IE3 | **4/4 concordent : Le moteur est de classe IE3** |
| ou IE4 | Espacement/glyphes divergents | 3lectures `ou IE4`, Tesseractgris `oulE4` : UNKNOWN |
| ELIGIBLE | Parasite vertical TesseractRGB | Parasite vertical encore présent : UNKNOWN |

**Deux lignes sur quatre concordantes**, contrezéro avant ; **un texte de cadre candidat sur trois entièrement concordant (IE2)**, contrezéro avant. Ce grade ne concerne que les régions lues : il ne déclare pas une extraction complète du cadre, une éligibilité CEE réelle ou une source admise. IE3/ouIE4 groupé reste divergent. Toutes les sources et projections conservent UNKNOWN/REVIEW_REQUIRED, admissionfalse.

Les sixstrips initiaux372pixels d'encre et les neufrégions UNREAD5056pixels d'encre restent conservés ; les six nouvelles bandes s'ajoutent à leur inventaire, pas à une liste de pixels détruits. Le raccord asynchrone reste refusé et n'est pas relu. Les douze occurrences altérées et les **28omissions** restent UNKNOWN/REVIEW_REQUIRED, sans transfert ni nouveau rejeu des17variantes. Résultats antérieurs35/63chemins sur neufvariantes préservantes et correspondant CEE conservés ; aucun chemin promu à partir du texte natif concordant.

## Contrôles

- **6 assertions rouges/1verte**, puis **7/7régressions** : coupe bornée, NONsombre, NONpâle changeant pixels, preuve absente/PENDING, côté non revu immobile, coupe horspréflight. **38/38privés** avec les suites mapping/sélection/partition/traits/padding.
- **126/126produit ciblés**,10,47s : coverageOCR/topologie/discovered/conditional. **39hasheslogiciel inchangés** ; aucun code produit, contrat, dépendance, migration ou UI modifié.
- Ruff/compile verts. Semgrep1.179.0,`p/security-audit`,**225règles/4scripts**,0finding/erreur/timeout, analyse locale/métriquesoff.
- Revue finale indépendante sansOCR :32inputsOLD/NEW reconstruits, marges/corps/crops/hashes conformes ; corps+bandes reconstruisent les anciens crops, preuve liée aupréflight déjà examiné avant lecture. Aucun défaut supplémentaire.
- Receipt privé **223référencesSHA-256** : sources/runtime/modèles/mappings/revues précédents, helper/scripts depréparation/lecture, préflightPENDING etpreuvepositive séparés, corps/bandes/inputs/grader/requalification/scan. Référence et captions ne sont jamais fournies au découpeur.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-spatial-trials/` : `spatial.py`, `test_spatial.py`, `prepare.py`, `preflight.json`, `proof.json`, `read_spatial.py`, `readings.json`, `line-grades.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout ; tests privés `--noconftest --no-cov`, préparation puis revue/proof avant `PYTHONPATH=backend`lecture. Le fichier de preuve reste technique local ; aucune validation métier humaine simulée. Aucune dépendance ou modèle ajouté.

## Limites

Qualification PARTIAL : quatre coupes exactes prouvées pour l'essai ; deux lignes concordantes mais `ouIE4`/`ELIGIBLE` divergents, régions non lues/refusasynchrone maintenus. Aucun support générique d'une frange/négation pâle nouvelle. Globalbackend2544/2544/couverture88,24% antérieur nonrelancé, produit inchangé. WIPnoncommité,aucunpush ; aucun backendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublic maintenus.

Skills appliquées : PDF, Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion, ECC eval-harness ; Graphify et cahiers actifs consultés, fichiers et preuves exacts revalidés. Les contrôles prouvent une portée technique locale, pas l'admission Golden ou la complétude DCE.
