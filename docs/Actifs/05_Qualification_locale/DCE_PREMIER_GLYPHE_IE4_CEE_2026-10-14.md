# ESSAIS DCE — premier glyphe T92 / IE4

## Cadrage avant lecture

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. T98 et ou concordants localement ; IE4/T92 conserve1E4/IE4. Deux régions terminales IE2/IE3 servent de comparaisons descriptives seulement. Douze occurrences altérées et28omissions UNKNOWN/REVIEW_REQUIRED.

**Risques :** assigner I depuis une forme ressemblante, oublier que I/l peuvent partager des pixels, rescaler pour obtenir un match, fournir la réponse attendue au moteur ou sélectionner une seule recette favorable.

**Insertion :** proof/scripts privés ; glyphes et groupes natifs de trois régions exactes déjà qualifiées. Aucun produit/contrat/migration/dépendance/UI modifié.

**Plan minimal :** segmentateur pixels existant, dernier groupe spatial et premier run sans étiquette dans l'extracteur ; descriptions RGB et masques BT601 natifs non rescalés, régions/contextes avec source/page/xref/occurrence/hash ; contre-exemples synthétiques I/l/1 ancrés ; revue avantOCR ; relectures sans whitelist, RapidOCR RGB/gris et Tesseract modes7/8surgroupes,10surglyphes ; grade après les appels, conserver UNKNOWN si conflits ; revue/contrôles/plan/index/miroir.

**Tests :** formes identiques sans label, couleurs différentes non cachées, largeur différente non rescalée, trait pâle inconnu et parent inchangé, diagonale1 non transformée en I. Décrire un motif n'autorise jamais sa valeur sémantique ni une substitution.

Méthodes : PDF, Superpowers diagnostic/TDD/revue/vérification, ECC eval-harness ; Context7Tesseract et aide5.3.4installée vérifient les modes7/8/10. Préserver M2-026/027/029/provenanceCT31-02, sourcesUNKNOWN/admissionfalse, nonlu/refusasynchrone et12/28sans transfert. Aucunbackendlive/VPS/déploiement/P3/dépôtexterne/push/GOpublic.

## Préflight et comparaison descriptive

Source DCE-03 Cadarache/CCTP commun indice2/annexe13/p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Trois parents sont les crops natifs locaux déjà qualifiés d'IE2/IE3/T92, sélectionnés par la preuve précédente. Le segmentateur existant reçoit seulement leurs pixels, retourne tous les runs/groupes ; le groupe terminal et son premier run sont retenus géométriquement, sans lui fournir une lettre.

| Parent | Groupe terminal, bbox relative | Premier run, crop relatif |
|---|---|---|
| IE2 | [272,0,303,18] | [273,0,277,18] |
| IE3 | [271,0,303,18] | [272,0,277,18] |
| IE4/T92 | [165,0,198,18] | [166,0,171,18] |

Six crops natifs : trois groupes et trois glyphes candidats. Chaque crop possède région absolue native, parent/source/page/xref/occurrence/hash, descriptionRGB et bbox/maskd'encre détectéeBT601<180. Le masque sert uniquement à une comparaison descriptive ; le crop RGB original reste intact pour l'OCR. Aucun rescale, masque de couleur ni substitution appliqué.

Les masques natifs de T92 diffèrent de ceux des deux références, à leur taille réelle. **Cela ne prouve pas des caractères différents** : seuil, taille et bruitJPEG influencent la description. Aucune valeur de référence n'est transférée vers T92. Le comparateur retourne toujours `inferred_labels=[]`, semanticstateUNKNOWN, même si deux formes concordent.

Trois contre-glyphes I/l/1 sont rendus avec **DejaVuSans24px installé**, font/hash enregistré. Les masques d'encre de I et l sont identiques dans ce contre-exemple ; leurs crops RGB ne sont pas déclarés identiques. Le masque1 diffère. Cette police synthétique n'est pas celle du PDF : le contrôle montre la limite d'une identification par forme, sans prétendre qualifier la typographie native. Un trait pâle sans encre au seuil reste inconnu, pas vide.

PréflightPENDING sansOCR ; revue visuelle indépendante des trois parents/sixcrops et troiscontre-glyphes, nontroncature visible et hashes/ancres/descriptions conformes. Après ce verdict etavantOCR, proof.json enregistre les neuf crops locaux positifs et lie lepréflight. Les scripts/helpers/fonts sont revalidés avantlecture. Aucun caractère natif n'est identifié par ce verdict technique.

## Relectures sans réponse attendue

**42 appels sur18entrées uniques :30natifs et12synthétiques.** RapidOCRsansdétecteurRGB/gris ; TesseractfraPSM7et8surgroupes,PSM10surglyphes. Les modes sont choisis avant les lectures selon le type de région, confirmés par l'aide locale5.3.4 etContext7tessdoc. Niwhitelist de caractères, nicontrainteIE4, nidictionnaire métier ajouté. Marge blanche8px et corps exacts vérifiés pixel par pixel. Références et labels synthétiques n'interviennent qu'après les appels.

| Région | Sorties natives brutes observées |
|---|---|
| Groupe IE2 | Rapid/PSM7 : IE2 ; PSM8 : JE2 |
| Glyphe référence IE2 | Rapid : 1 ; PSM10 : [l |
| Groupe IE3 | Rapid/PSM7 : IE3 ; PSM8 : 1E3 |
| Glyphe référence IE3 | Rapid : I ; PSM10 vide ou (l |
| Groupe IE4/T92 | Rapid : IE4 ; PSM7RGB : 1E4, gris : IE4 ; PSM8 : 1E4 |
| **Premier glyphe T92** | **Rapid : 1 ; PSM10RGB : ll ; gris : !** |

Contrôles synthétiques : Rapid lit1pourI/l/1 ; TesseractPSM10litI,puisparenthèse,puis1. Les sorties de tous les modes sont conservées ; les références IE2/IE3 ne deviennent pas une vérité du glyphe isolé. Les concordances de leurs recettes de lignes antérieures restent des résultats locaux de ce protocole, pas une identification universelle du caractère.

**Décision technique : premier glyphe T92 indécidable avec ces preuves, UNKNOWN maintenu.** Les trois grades de groupe à sixlectures restent divergents ; aucune sélection du seul mode favorable. Tous les crops/textes sources conservent UNKNOWN/REVIEW_REQUIRED, admissionfalse, whole_parent_completefalse. Aucun remplacement1→I, l→I ou caractèresparasites supprimés.

## Requalification et contrôles

Les régions non lues/franges/bandes/strips précédentes restent dans leur inventaire avec sources/hashes exacts, le parent natif est conservé, le raccord asynchrone reste refusé et non relu. Les **douze occurrences altérées et28omissions** demeurent UNKNOWN/REVIEW_REQUIRED, sans transfert de la comparaison ou d'un résultatOCR natif. Aucun nouveau rejeu des17variantes ;35/63chemins antérieurs sur neufcaspréservants non promus. Correspondant CEE et source/version/hash/locator maintenus.

- TDD : **5rouges puis5/5verts**, formes identiques sans label, RGBdifférent malgré masqueidentique, largeur différente non rescalée, traitpâle/parentintact, diagonale1nontransformée. **49/49privés** avec les suites antérieures.
- **126/126produit ciblés**,10,18s : coverageOCR/topologie/discovered/conditional. **39hasheslogiciel inchangés** ; aucun code/contrat/dépendance/migration/UI produit modifié.
- Ruff/compile verts. Semgrep1.179.0,`p/security-audit`,**225règles/4scripts**,0finding/erreur/timeout, local/métriquesoff.
- Revuepré/post indépendante sansOCR : neufcrops,18inputs/42lectures/corps/marges conformes, hashes/preflight/proof/font exacts ; référence aprèslecture, aucunwhitelist/substitution, zero promotion/transfert. Pas de défaut supplémentaire.
- Receipt privé **294référencesSHA-256** : source/runtimes/modèles/mappings/prépreuves précédents, helpers/préflight/proof/font/crops natifs+synthétiques/inputs/lectures/requalification/scan. Scripts figés avant lectures.

Preuves : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-first-glyph-trials/` : `describe.py`, `test_describe.py`, `prepare.py`, `preflight.json`, `proof.json`, `read_first.py`, `readings.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout ; tests privés `--noconftest --no-cov`, préparation/revue/proof avantlecture `PYTHONPATH=backend`. La police est locale existante ; aucun modèle/dépendance ajouté.

## Limites et décision de suite

La barrière de non-substitution est qualifiée ; la lettre ne l'est pas. Le glyphe isolé perd son contexte et les formes peuvent être ambiguës ; cette recette n'est pas une règle métier d'énergie ni une admission source. Il est inutile de transformer une ressemblance ou un mode choisi en certitude. Les preuves natives doivent maintenant être consolidées cadre par cadre avec leurs recettes/marges validées et les désaccords indécidables reliés aux conditions/chemins concernés, sans déclarer une analyse complète.

Globalbackend2544/2544/couverture88,24% antérieur nonrelancé, produitinchangé. WIPnoncommité/aucunpush ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublic. Skills : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify,cahiers/fichiers/preuves exacts etContext7Tesseract utilisés. Aucune validation humaine simulée.
