# ESSAIS DCE — question asynchrone / raccord natif

## Cadrage avant lecture

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Registre9cadres/36lectures,verrouasynchrone partagépar6chemins. Raccord entrant ambigu,texte avecparasite de bord,sourceUNKNOWN/REVIEW_REQUIRED.

**Risques :** prendre NON ou I pour un raccord, effacer une négation pâle, qualifier une direction à partir du texte ; lever le refusgéométrique par un accordOCR ou transférer une preuve sur un raster altéré.

**Insertion :** proof/scripts privés ; cadre natif complet T88 et bande déjà ancrée [0,17,265,41]. Aucun code produit/contrat/dépendance/migration/UI modifié.

**Plan minimal :** segmenter depuispixels, proposer composante latérale/texte/nonlu ; préserver partitionRGBexacte et source/page/xref/région/hash ; tests de negation/raccord/preuve ; revuepositive avant OCR ; comparer bandeparent/croptexte avec margeblanche/deuxmoteurs ; mesurer supporttextuel séparément du raccord et de la route, conserver IE2/T92 et12/28 ; revue/contrôles/docs/miroir.

**Tests :** partitionparentinchangé/raccordnonqualifié, NONsansstreakcontinu refusé, NONtouchantconnexion refusé, NONséparé conservé danstexte, preuveabsente/PENDINGrefusée, NONpâle invalide lehashprécédent. La géométrie propose seulement un crop ; chaque utilisation est bornée à une preuve technique locale positive exacte.

Méthodes : PDF,Superpowers diagnostic/TDD/revue/vérification,ECC eval-harness ; M2-026/027/029 et provenanceCT31-02 maintenus. Aucunmasque/substitutionI/l/1,backendlive/VPS/déploiement/P3/dépôtexterne/push/GOpublic ; A1nonadmis,A2génériqueHOLD,NO-GOpublic.

## Séparation et preuve avant OCR

Source DCE-03 Cadarache/CCTP commun indice2/annexe13/p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. Cadrecomplet natif [755,698,1020,750] ; bandeparentnative [755,715,1020,739],265×24. Les scripts vérifient les hashes du cadre et du parent ; chaque région a une ancre native absolue.

La projection existante des colonnes donne une composante latérale sur les premiers7pixels, dont des colonnes occupées sur au moins90%de la hauteur. Le reste des groupes d'encre n'est pas associé à un texte attendu ; tous sont conservés dans le span après cette composante. Il ne s'agit pas d'une règle sémantique générale « trait≠glyphe » : une revue locale précise est indispensable.

| Région | Bbox relative à la bande | Bbox native absolue |
|---|---|---|
| Texte candidat | [27,0,245,24] | [782,715,1000,739] |
| Composante de raccord/bord candidate | [0,0,7,24] | [755,715,762,739] |
| UNREAD entre composante et texte | [7,0,27,24] | [762,715,782,739] |
| UNREAD à droite | [245,0,265,24] | [1000,715,1020,739] |

Les quatre crops reconstruisent exactement tous les pixels RGB du parent, aucun masque ni pixel supprimé. Les régions nontextuelles restentUNKNOWN ; la composante candidate n'est pas une direction, jonction ou raccord qualifié.

PréflightPENDING sansOCR, revuevisuelleindépendante du cadrecomplet,parent etquatrecrops : questionentière,sansglyphevisible/NONperdu dans les régions conservées. Aprèsceverdict etavantlecture, proof.json lie la décisiontechnique positive au hashRGB,parent,régions/préflight. Le lecteur revalide les scripts/helpers, le hash du corps et la proposition exacte ; PENDING/absence/refus ne permettent aucunelecture du nouveaucrop. Artefacttechnique local, pas signature/actehumain ou admission.

## Comparaison fraîche

**8 appels sur4entrées uniques**, deuxrecettesRGB/gris-autocontraste × deuxmoteurs RapidOCRsansdétecteur/TesseractfraPSM7, pourPARENT/TEXT. Marge réellementblanche8px vérifiée partout, corps exacts, texte de référence chargé après les appels. Aucun compte de mots fourni au découpeur, aucune substitutionI/l/1.

| Entrée | RapidRGB | TessRGB | Rapidgris | Tessgris |
|---|---|---|---|---|
| PARENT | Moteur asynchrone? | 1 Moteur asynchrone ? | Moteur asynchrone? | 1 Moteur asynchrone ? |
| **TEXT** | **Moteur asynchrone?** | **Moteur asynchrone ?** | **Moteur asynchrone?** | **Moteur asynchrone ?** |

**Quatrelectures TEXT concordantes**, PARENTtoujoursdivergent. La normalisation existante de whitespace/punctuationpourgrading ne remplace aucuncaractère ; toutes les sortiesbrutes restentdisponibles. Cet accord qualifie seulement le texte local, pas l'ensemble du cadre, une relation ou une propriété d'un moteur réel.

## Impact sur les six chemins

Ancienregistre conservé inchangé ; updated-register.json en constitue une projection locale liée par hash. **Seul le supporttextuel du nœudasync évolue**. L'ancienne raison de refus AMBIGUOUS_CONNECTOR_NOT_REQUALIFIED reste présente, désormais explicitement scopedCONNECTION_GEOMETRY ; connection_refusalretained=true etconnectionqualified=false. Sources/frames/paths restentUNKNOWN/REVIEW_REQUIRED/admissionfalse/wholecompletefalse. Les verrousIE2etT92 demeurent ; aucune sélection favorable pour leslever.

Sixchemins dépendent toujours du raccordasync : indices0,1,2,4,5,6. L'accordtexte supprime leur manque spécifique de texteasynchrone ; seuls les chemins0et4 deviennent entièrement supportés textuellement, les1,2,5,6 restentbloqués parIE2ouIE34/T92. Lechemin3,nonasynchrone,étaitdéjàtextuellementsupporté.

| Mesure | Avant | Après |
|---|---|---|
| Corroborations locales de cadres | 7/9 | 8/9 |
| Nœuds de supporttextuel | 6/9 | 7/9 |
| Chemins sans dépendance textuelle manquante | 1/7 | 3/7 |
| Chemins avec dépendance textuelle manquante | 6/7 | 4/7 |
| **Routes natives qualifiées** | **0/7** | **0/7** |

**Aucun accord texte ne qualifieOUI/NON,unejonction,unepointeouunedirection.** Leurcompteur reste0, et le refusgéométrique du raccord reste applicable aux sixchemins. Les issuesdocumentaires de référence ne deviennent pas deséligibilitésréelles. CorrespondantCEE et ses deuxbranches restent visibles avec inconnusIE2/T92.

L'inventaire conserve les25régions précédentes et ajoute la composante deraccord et deuxUNREAD : **28entréesrégionales**, source/page/xref/région/hash, possiblementchevauchantes, pasune couverture sémantiqueexhaustive. Lesparents/PDF/JPEGsontintacts. Les **douze occurrences altérées et28omissions de variantes** restentUNKNOWN/REVIEW_REQUIRED, sans transfert ni nouveau rejeu des17variantes. Ce28omissions n'est pas lecompteur28régions conservées : deuxpérimètres distincts. Anciendécompte35/63chemins devariantes non promu.

## Tests et contrôles

- TDD : **4assertionsrouges/2vertes**, puis **6/6tests** : partitionintacte,NONsansstreakrefusé,NONtouchantraccordrefusé,NONséparéconservé,preuveabsente/PENDINGrefusée,NONpâle invalide lehashprécédent. **61/61privés** avec les suites antérieures. Aucuncontrôle de couleur ne suffit à déclarer une négation pâle absente.
- **126/126produit ciblés** coverageOCR/topologie/discovered/conditional. **39hasheslogicielinchangés**, aucunproduit/contrat/migration/dépendance/UI modifié.
- Ruff/compileverts ; Semgrep1.179.0,`p/security-audit`,**225règles/5scripts**,0finding/erreur/timeout, local/métriquesoff.
- Revuepré/postindépendantesansOCR : crops/ancres etpartition exacts, huitlectures/inputs blancs/corps conformes,texteinsidecadre,hashes/proof/delta/registre précédent conformes. Refusdu raccord,locksIE2/T92 etsourceUNKNOWN conservés ; aucun défautsupplémentaire.
- Receiptprivé **345référencesSHA-256** : sources/runtimes/modèles/prépreuves,helpers/préparation/préflight/proof,corps/régions/inputs/lectures/projection/requalification/scan. Scriptsfigés avant lecture.

Preuvesprivées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-async-trials/` : `separate.py`, `test_separate.py`, `prepare.py`, `preflight.json`, `proof.json`, `read_async.py`, `readings.json`, `impact.py`, `updated-register.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv`ducheckout ; tests `--noconftest --no-cov`, préparation/revue/proof avantlecture `PYTHONPATH=backend`, puisimpact. Aucunmodèle/dépendance ajouté.

## Limites

RésultatPARTIAL : le texteasynchrone estcorroboré danssoncrop, le raccord etlesroutes ne le sontpas. Seuil180/localrevue ne qualifient aucunautreglyphepâle/tenant/version,imagealtérée. Exclureunecomposante d'uninputOCR n'effaceaucunpixelduparent etneprouvepaslasémantique duparent. Globalbackend2544/2544/couverture88,24%antérieur nonrelancé,produitinchangé. WIPnoncommité/aucunpush ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublicmaintenus.

Skills : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify,cahiers/fichiers/preuvesexactsvérifiés. Validationtechnique distincte d'unevalidationmétierhumaine/admissionGolden.
