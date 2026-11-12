# ESSAIS DCE — sorties natives asynchrone / labels / raccord

## Cadrage avant extraction

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Texteasynchrone4/4,3/7supports textuels,refusgéométrique6chemins etroutesnatives0. Lecteurs produit existants refusent la topologie horsrender150DPI ; aucun spoofDPI autorisé.

**Risques :** injecter une polyligne attendue, copier les longueurs/seuils spatiaux150DPI sur l'image native, assimiler connectivité/frameborder/jonction à une direction, associer un label au mauvais bord et promouvoir une route par le texte.

**Insertion :** proof/scripts privés, pasproduit/contrat/migration/dépendance/UI. AssetJPEG original1684×1460, source/page/xref/région/hash. Régions sorties gauche/basse et crops de labels proposés depuis la vue source, preuve locale avant OCR/géométrie. Aucun chemin/polyline/labeltexte fourni à l'extracteur.

**Plan minimal :** préparer etreviewer régionsRGB natives ; relire labels avec vraie margeblanche ; extraire composantesde pixels issues de runsaxiaux longs, profilsde luminance et longueur locale dérivée de la hauteur native du cadre ; comparer profils/contactscandidats sans direction ; contreT/croisement/gap/flècheinversée ; conserver ambiguïtés etrefusgéométrique,nonlu/IE2/T92/12/28 ; revue/tests/scan/docs/miroir.

**Tests :** Tconnecté sansdirection, gapnonponté, croisementpixels n'atteste ni jonction ni direction, flècheinversée necrée pas uneorientation. Un graphedepixels n'est pas une topologie dirigée ; bordures de cadres etroutes restent explicitement non séparées tant que non prouvées.

Méthodes : PDF,Superpowers diagnostic/TDD/revue/vérification,ECC eval-harness. M2-026/027/029/provenanceCT31-02,UNKNOWN/admissionfalse maintenus. Aucun corpusadditionnel/backendlive/VPS/déploiement/P3/dépôtexterne/push/GOpublic.

## Régions et preuve avant extraction

Source DCE-03 Cadarache/CCTP commun indice2/annexe13/p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`,1684×1460pixels. Fenêtres proposées depuis la vue native, aucun tracé/polyline attendu communiqué à l'extracteur.

| Fenêtre | Bbox native exclusive | Portée |
|---|---|---|
| GEOMETRY_LEFT | [160,665,780,1095] | Sortie latérale, raccords et cadres partiels |
| GEOMETRY_DOWN | [690,740,1090,925] | Sortie basse, bifurcation et cadres partiels |
| LABEL_LEFT | [545,680,650,722] | Texte du label latéral |
| LABEL_DOWN | [910,765,985,811] | Texte du label bas |

Chaque crop est une copie RGB exacte du JPEG, source/page/xref/occurrence/nativebbox/hash. PréflightPENDING sansOCR/géométrie, puis revuevisuelleindépendante : labelsentiers, fenêtresgéométriques volontairementpartielles, sources/coords/hashes conformes. Après ce verdict et **avant extraction**, proof.json lie les quatre fenêtres exactes et la décisiontechniquepositive au hashpréflight. Le lecteur revalide chaque région/script ; aucune source admise ou relation orientée déduite de cette décision.

Les fenêtres ne couvrent pas des routes complètes et contiennent des bordures/textes partiels aux limites. La qualification porte sur ces fenêtres, pas sur l'intégralité des sorties ni sur une topologie.

## Profil natif local et contre-exemples

Le lecteur produit existant exige renderDPI150 ; il n'est pas appelé en falsifiant cette valeur. Prototype local distinct : questionnativehauteur52pixels → minrun26pixels ; profils de luminance BT601 à150/180/210. **Ces150/180/210 sont des intensités, pas desDPI.** La longueur26 provient du cadre natif, pas du18pixels du lecteur150DPI. C'est une proposition locale évaluée, aucune calibration générale ni invariance d'échelle affirmée.

L'extracteur reçoit uniquement pixels, seuil et minrun ; runs horizontaux/verticaux continus, uniondeleurs pixels puis composantes4voisins. Il ne reçoit ni destinations, ni polylignes, ni labels attendus. Aucun gap n'est ponté. Sources/cropsRGBinchangés ; les masques de détection servent aux descriptionsgéométriques, pas à l'OCR ni à effacer l'original.

ContreT/croisement/gap/flècheinversée : **4rouges→4verts**. T/croisementpeuventformer une composante connectée sans qu'orientation ou jonction soient qualifiées. Uneflèche inversée ne change pas ce refusdedirection ; le détecteur ne qualifie aucunepointe. Il s'agit de guards de non-certitude, pas d'un score positif de reconnaissance de flèche.

## Labels et rattachement : résultat PARTIAL

**8lectures de labels sur4entrées uniques**, deuxrecettesRGB/gris-autocontraste × deuxmoteurs RapidOCRsansdétecteur/TesseractfraPSM7. Marge blanche8px et corps exacts contrôlés ; grading seulement après toutes les extractions. Aucune whitelist ni normalisationI/l/1.

| Label | RapidRGB | TessRGB | Rapidgris | Tessgris |
|---|---|---|---|---|
| Gauche | NON | NON | NON | NON |
| Bas | ouI | OUI | OUI | OUI |

Les deux textes concordent après le casefold existant pour le grading ; les sortiesbrutes sont conservées. `ouI`→`oui` est un changement de casse, pas une substitutionl/1→I. **Deux corroborations textuelles natives**, sans admission ni label-vers-branche qualifié.

Six extractionsgéométriques : deuxfenêtres × troisprofils. LEFTdonne2composantes à chaqueprofil,DOWN1. La stabilité de leur nombre ne prouve pas la topologie : **bordures de cadres et traits ne sont pas séparés**. Certaines composantes peuvent contenir des bordures et surfaces colorées, pas seulement des routes.

La distance pixel-à-bbox du label est mesurée après extraction, sans dessiner de route : minima carrésNON4/1/1 etOUI169/169/144, pour150/180/210. Ces proximités ne sont pas des connexions dirigées et ne prouvent pas le rattachement au bon port. Les candidates restent semanticUNKNOWN, relationqualifiedfalse,orientationUNKNOWN,junctionfalse. Aucunpolyligne de référence n'est fourni, aucune association n'est promue par la seule lectureOUI/NON.

**Refusgéométrique maintenu** : 0relationnative de label,0jonction,0direction,0route qualifiée. Les seuils spatiaux150DPI ne sont pas transférés ; même ceprofilnativedoitêtre renforcé avant usagegénéral.

## Registre, couverture et conservation

updated-register.json conserve tous les neufcadres etleurspreuves/inventaire de la trancheprécédente, puis ajoute une entrée native_output_evidence. Lescompteurs8corroborationsde cadres/7supports/3sur7chemins textuels sont inchangés. Deux labels textuellementcorroborés ne changent pas lecompteur0route/OUI-NONrelation/jonctionnativequalifiée. Le raccord reste refusé surles sixchemins,lesinconnusIE2/T92 persistent.

Les28régions conservées,parents/PDF/JPEG etnouvellesfenêtres RGB restent intacts. Les régions sontparfois chevauchantes, pasunecouverture sémantiqueexhaustive. Les **douze occurrences altérées et28omissions** restent UNKNOWN/REVIEW_REQUIRED, sans transfert ni nouveau rejeu des17variantes. Les35/63chemins antérieurs devariantes ne sont pas requalifiés par les labelsnatifs. CorrespondantCEE etsesbranches avecinconnus restentvisibles ; aucuneanalysecomplète ou éligibilité réelle.

## Contrôles

- **4/4nouveauxtests et65/65privés**, aprèsquatreéchecsinitiaux : T,gap,croisement,flècheinversée, avecinvariantsd'orientation/jonctionnonqualifiées.
- **126/126produit ciblés**,9,85s : coverageOCR/topologie/discovered/conditional. **39hasheslogicielinchangés**, aucunproduit/contrat/migration/dépendance/UI modifié.
- Ruff/compileverts ; Semgrep1.179.0,`p/security-audit`,**225règles/4scripts**,0finding/erreur/timeout. Premiercontrôled'autorisationautomatique expiréavantprocessus ; réessaiuniqueautorisé,scanfinaIréussi. Aucuncode/résultattransmis, métriquesoff.
- Revueindépendante avantextraction valide lescrops etleurportéepartielle ; revuedefin vérifieprovenance,8inputs/corps/marges,preuves/hashes etabsence de promotiongéométrique. AucunOCRrelancéparlereviewer.
- Receipt privé **364référencesSHA-256** : sources/runtime/modèles/prépreuves,helpers/préparation/proof,fenêtres/profils/composantes/labels/proximités/registres/requalification/scan. Scriptsfigés avantextraction.

Preuves : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-output-trials/` : `axis.py`, `test_axis.py`, `prepare.py`, `preflight.json`, `proof.json`, `extract_outputs.py`, `results.json`, `updated-register.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv`ducheckout ; tests `--noconftest --no-cov`,préparation/revue/proofavant `PYTHONPATH=backend`extraction. Aucunmodèle/dépendanceajouté.

## Limites et suite

Deuxtextesdelabels concordent ; la proximité à une composante mêlant bordure etroute est insuffisante pour un rattachement. Il faut qualifier la séparation des bordures etdestraits dans ces fenêtres natives avant d'associer labels/ports ou de chercher une direction. Lescomposantes/sourceauxlimites restentincomplètes ; aucunecalibrationgénérale,nativepointes ou routecomplète prouvée.

Globalbackend2544/2544/couverture88,24%antérieur nonrelancé,produitinchangé. WIPnoncommité/aucunpush ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublic. Skills : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify,cahiers/fichiers/preuvesexactsvérifiés. Validationtechnique distincte d'unevalidationmétierhumaine/admissionGolden.
