# ESSAIS DCE — segmentation locale T92/T98

## Cadrage avant lecture

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. IE2/IE3 concordants localement ; T92/T98 divergents, sources UNKNOWN/REVIEW_REQUIRED. Douze occurrences altérées/28omissions conservées.

**Risques :** injecter ou deviner le texte attendu, découper un glyphe touchant, omettre NONpâle hors du seuil, confondre composante d'encre et caractère ; admettre une source ou transférer un accord vers une image altérée.

**Insertion :** proof/scripts privés seulement. Deux régions natives déjà qualifiées, retenues par hashes de corps et ancres ; texte attendu absent du segmentateur. Aucun produit, contrat, migration, dépendance ou UI modifié.

**Plan minimal :** projection des colonnes d'encre BT601<180, runs candidats sans nombre de glyphes fourni, groupes selon espaces/horizontalheight ; span et groupes conservant tous les pixels RGB de leurs crops, inventaire complémentaire non lu UNKNOWN ; revue pixel/crop/source/région/hash avant OCR ; lire corps témoin, span et groupes avec marge blanche et deux moteurs ; comparer seulement après, puis requalification12/28sans transfert, revue/tests/docs/miroir.

**Tests :** large espace sans texte attendu, composantes touchantes non scindées, NONsombre isolé conservé, NONpâle invisible au seuil gardé dans parentUNKNOWN, mélange NONpâle/ELIGIBLE ne déclarant pas complet, mauvaismode refusé. Les pixels non retenus par le seuil ne deviennent ni fond ni sans texte ; parent inchangé.

Méthodes : PDF, Superpowers diagnostic/TDD/revue/vérification, ECC eval-harness ; M2-026/027/029 et provenanceCT31-02 conservés. Pas de masque, remplacementI/l/1, backendlive/VPS/déploiement/P3/dépôtexterne/push ou GOpublic ; A1nonadmis,A2génériqueHOLD,NO-GOpublic.

## Régions qualifiées avant lecture

Source originale DCE-03 Cadarache, CCTP commun indice2/annexe13 p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Parents : crops natifs locaux déjà qualifiés, retenus par hashes exacts ; ni mots attendus ni nombre de glyphes transmis au segmentateur. Les IDs T92/T98 servent à sélectionner les ancres et au grading ultérieur, pas à découper.

La projection des colonnes BT601<180 fournit **cinq runs sur T92**, regroupés en **deux régions candidates**, et **trois runs sur T98**, regroupés en une région. Les runs sont des plages d'encre projetée ; ils ne sont pas assimilés à des lettres. Les glyphes touchants ou se recouvrant en projection ne sont pas scindés pour obtenir un nombre attendu.

| Parent natif | Runs de colonnes (bornes exclusives) | WORD / SPAN, bbox relative au parent |
|---|---|---|
| T92,332×18 | [135,147],[149,159],[167,170],[173,182],[185,196] | WORD0=[133,0,161,18],WORD1=[165,0,198,18],SPAN=[133,0,198,18] |
| T98,157×20 | [36,64],[65,85],[87,121] | WORD0=SPAN=[34,0,123,20] |

Groupement par espace au moinsmax(3,hauteur//3), bord local2px, hauteur entière conservée ; crops RGB exacts, sans masque. **Sept rôles de région / six crops uniques** : deuxBASE, deuxSPAN et troisWORD ; T98SPAN/WORD sont le même crop, pas deux preuves indépendantes. Tous disposent de parent/hash et région absolue dans les pixels natifs du JPEG. Les quatre régions latérales UNREAD sont extraites/hashées/UNKNOWN : span+UNREAD reconstruisent exactement tous les pixels du parent. Tous les pixels détectés sombres sont couverts par les WORD ; les pixels plus clairs ne deviennent pas fond par cette constatation.

Préflight PENDING sans OCR, puis revue visuelle indépendante des parents, spans, troisWORD et quatreUNREAD : aucun glyphe visible tronqué ; segmentation recalculée identique et crops/ancres/hashes conformes. Après ce verdict et **avant OCR**, proof.json fixe les deux décisions positives pour ces seules régions. La lecture vérifie l'identité des scopes/crops avec le préflight, les scripts/helpers figés et les pixels parents. Ce fichier reste une preuve technique locale, pas une signature humaine ou une admission.

## Comparaison OCR

**28 appels sur12entrées uniques** : RapidOCR sans détecteur et Tesseract français PSM7, RGBblanc et gris/autocontrasteblanc, pourBASE/SPAN/WORD. Les deux moteurs partagent les entrées de chaque recette ; les lectures de T98SPAN/WORD répètent le même crop. Tous les pixels de marge sont vérifiés blancs et les corps exacts. La référence textuelle n'est chargée qu'après toutes les lectures. WORDS assemble les régions en ordre spatial avec les espaces inférés par le découpeur ; aucun texte attendu n'est injecté.

| Référence | Corps BASE | SPAN | WORDS |
|---|---|---|---|
| T92 | Tesseractgris `oulE4`, divergence | Même divergence | `ou`4/4, puis RapidRGB `IE4`, TessRGB `1E4`, Rapidgris `IE4`, Tessgris `IE4` : UNKNOWN |
| T98 | TessRGB `\| ELIGIBLE`, divergence | **ELIGIBLE4/4** | Même crop, **ELIGIBLE4/4** |

Le texte candidat T98 concorde localement après resserrement spatial, sans substitution. T92 reste divergent : le premier caractère de sa seconde région ne peut être normalisé I/l/1. L'accord de T98 ne prouve ni extraction complète du parent ni éligibilité réelle ni admissibilité de la source ; **whole_parent_complete=false**, UNKNOWN/REVIEW_REQUIRED et admissionfalse conservés.

## Contre-exemples et non-lu

Les tests protègent NONsombre isolé et les composantes touchantes ; le segmentateur n'altère aucun pixel parent. **NONpâleRGB(187,204,212)** peut échapper au seuil180, même à côté d'un mot sombre détecté. Dans ce cas, le parent et les régions hors extraction restent UNKNOWN, et le résultat ne devient jamais complet. Ces contre-exemples prouvent conservation/refus de complétude, pas une reconnaissance OCR exhaustive des négations pâles.

Aux quatre nouvelles régions UNREAD latérales s'ajoutent toujours les neuf régions antérieures5056pixelsd'encre, les bandes/franges/strips conservés et le raccord asynchrone refusé. Aucun non-lu n'est effacé ou déclaré sans texte. Les **douze occurrences altérées et28omissions** restent UNKNOWN/REVIEW_REQUIRED, sans transfert des concordances natives ni nouveau rejeu des17variantes. Source/version/hash/locator et correspondant CEE conservés ; ancienrésultat35/63chemins sur neufvariantes préservantes non promu.

## Vérifications

- TDD : **5 assertions rouges/1verte**, puis **6/6tests** : regroupement depuis pixels, composante touchante, négation sombre, négation pâle, données partielles, modeRGBArefusé. **44/44privés** avec les suites de provenance/coupe/marge antérieures.
- **126/126produit ciblés**,9,49s : coverageOCR/topologie/discovered/conditional. **39hasheslogiciel inchangés** ; aucun changement produit/contrat/migration/dépendance/UI.
- Ruff/compile verts ; Semgrep1.179.0,`p/security-audit`,**225règles/4scripts**,0finding/erreur/timeout, analyse locale/métriquesoff.
- Revue avant/après OCR indépendante sans relancerOCR : régions et28lectures conformes, hashes/preflight/proof exacts, corps/marges/crops reconstruits. Pas de normalisation ni indice de fausse complétude. Une correction de style du lecteur a précédé un rerun complet ; les résultats initiaux sont archivés, seuls les résultats finaux lient le script figé.
- Receipt privé **256référencesSHA-256** : sources/mappings/runtime/modèles/revues précédents, sélection/helpers/préparation/préflight/proof, régions lues et non lues/inputs/lectures/requalification/scan.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-glyph-trials/` : `segment.py`, `test_segment.py`, `prepare.py`, `selection.json`, `preflight.json`, `proof.json`, `read_glyphs.py`, `readings.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout ; tests `--noconftest --no-cov`, préparation puis revue/proof avant lecture `PYTHONPATH=backend`. Aucune dépendance ni modèle ajouté.

## Limites

Qualification PARTIAL : les régions locales sont qualifiées pour cette lecture, T98 concorde, T92 demeure UNKNOWN. Une segmentation glyphique complète lettre par lettre n'est pas prouvée ; runs≠caractères, seuil180 incomplet pour texte pâle. Aucun support générique ni admission/sourcecomplète qualifié. Globalbackend2544/2544/couverture88,24% antérieur nonrelancé, produit inchangé. WIPnoncommité/aucunpush ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublic maintenus.

Skills appliquées : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify et cahiers actifs consultés puis fichiers/preuves exacts vérifiés. Les preuves techniques restent distinctes d'une validation métier humaine ou admissionGolden.
