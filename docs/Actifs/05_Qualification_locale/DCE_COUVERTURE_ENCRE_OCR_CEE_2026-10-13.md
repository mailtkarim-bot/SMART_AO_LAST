# ESSAIS DCE — couverture encre/OCR des cadres CEE

## Cadrage et plan

**AS-IS :** groupes candidats retrouvés, mais cadres sans OCR invisibles et mots manquants dans une boîte non détectables par containment seul. **Risques :** perdre NON/déjà/IE3-ou-IE4/contact, valider des pixels couverts avec un texte faux, absorber une grille composite. **Insertion :** nouveau lecteur infrastructure de couverture et tests; reprise de strokes, validation PNG/scope et regroupement existants; aucune UI/API/migration/dépendance.

**Plan minimal :** (1) détecter les rectangles fermés dans le raster indépendamment des tokens; distinguer rectangles composites/nesting; (2) mesurer l’encre intérieure non couverte et conserver les cadres sans OCR en UNKNOWN; (3) requérir une relecture OCR indépendante traçable et une concordance textuelle stricte pour conserver une qualification texte candidate; aucune relecture reste UNKNOWN; (4) requalifier chemins et mesurer omissions/contre-épreuves sans relations de référence injectées; (5) revue, tests globaux par lots, scans, documentation et miroir. La concordance de deux OCR n’est pas la vérité lexicale ni l’éligibilité réelle.

- [x] Tests rouges : cadre sans OCR, négation perdue hors/dans boîte, groupe incomplet, région/tenant/version/hash, relecture absente/contradictoire, nesting/composite, retries/ordre.
- [x] Lecteur minimal et ciblés verts.
- [x] Source Cadarache p42 : raster/hash/frame/crop/parseur/OCR brut; contre-épreuves et chemins.
- [x] Revue/contrôles/suite backend exhaustive/couverture85,50% inchangée/nettoyage PG.
- [x] Plan/index/journal/Basic Memory.

Superpowers cadrage/TDD/plan/revue + ECC verification-loop. Aucun push/déploiement/VPS/effetP3/dépôt externe. A1 non admis,A2 HOLD,NO-GO public;UNKNOWN/REVIEW_REQUIRED et originaux conservés.

## Source et mesures locales

CEA Cadarache CCTPC indice2, annexe13 page42/44, logigramme inférieur « Variation de vitesse » BAT-TH-112. ROI fourni `(289,1098,881,1521)` et raster150DPI1275×1650. Cadres/phrases/rôles attendus jamais injectés dans la détection ou la relecture; comparaison aux références seulement après construction.

- Source PDF SHA256 : `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`.
- Raster SHA256 : `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.
- Dix régions rectangulaires fermées découvertes : neuf cadres textuels et une face fermée par les routes. Un rectangle composite IE2+IE3/4 est conservé séparément, exclu des cadres atomiques. La face de routes reste UNKNOWN, avec11pixels de pointes non couverts; elle ne devient pas un nœud textuel automatique.
- Les neuf cadres textuels ont zéro pixel intérieur sombre non couvert par les boîtes OCR (calibration détaillée ci-dessous). Cela ne prouve pas leurs mots : cinq concordances candidates, quatre lectures vides/désaccords.
- Les sept chemins géométriques et leurs conditions restent retrouvés, mais **sept chemins UNKNOWN, zéro chemin avec texte requalifié**, zéro faux chemin qualifié. Cette preuve ajoute une barrière lexicale aux anciens candidats; l’historique de qualification géométrique reste intact.

### Concordance indépendante par cadre

| Cadre raster | Caption OCR primaire | Relecture contrôlée | Résultat |
|---|---|---|---|
| [304, 1445, 382, 1484] | NON / ELIGIBLE | Lecture vide | REREAD_FAILED |
| [442, 1114, 584, 1168] | J'installe un variateur de / vitesse sur un moteur / déjà existant? | J'installe un variateur de vitesse sur unmoteur déjà existant? | TEXT_DISAGREEMENT |
| [442, 1196, 584, 1250] | Le moteur existant est / déjà équipé d'un / variateur de vitesse? | Le moteur existant est déjà équipé d’un variateur de vitesse? | TEXT_DISAGREEMENT |
| [518, 1364, 677, 1404] | Le moteur est de classe IE2 | Le moteur est de classe IE2 | INK_AND_TEXT_AGREE |
| [526, 1452, 670, 1504] | Contacter votre / correspondant CEE / centre | Contacter votre correspondant CEE centre | INK_AND_TEXT_AGREE |
| [598, 1328, 758, 1364] | Aucun token | Lecture vide | NO_OCR |
| [614, 1268, 738, 1292] | Moteur asynchrone? | Lecture vide | REREAD_FAILED |
| [677, 1364, 836, 1404] | Le moteur est de classe IE3 / ou IE4 | Le moteur est de classe IE3 ou IE4 | INK_AND_TEXT_AGREE |
| [718, 1114, 862, 1168] | J'installe un variateur de / vitesse sur un moteur / neuf? | J'installe un variateur de vitesse sur un moteur neuf? | INK_AND_TEXT_AGREE |
| [718, 1472, 796, 1496] | ELIGIBLE | ELIGIBLE | INK_AND_TEXT_AGREE |

### Contre-épreuves sur la même encre

- Retrait du token NON :141pixels non couverts dans le cadre NON ELIGIBLE, UNKNOWN; aucune promotion d’ELIGIBLE.
- Retrait de « centre » :74pixels non couverts dans la sortie correspondant CEE, UNKNOWN.
- Retrait de tout l’OCR IE2 : cadre conservé depuis les traits,257pixels non couverts, nœud UNKNOWN; aucune disparition silencieuse.
- Retrait de « déjà » dans sa boîte inchangée : zéro trou géométrique, mais désaccord avec la relecture contenant « déjà »; UNKNOWN. La qualification nominale de ce cadre était déjà UNKNOWN du fait de l’apostrophe typographique; cette contre-épreuve ne revendique pas un nouveau chemin perdu.
- Test synthétique de NON perdu dans une boîte inchangée : pixels couverts mais texte contrôlé NON ELIGIBLE différent, qualification refusée. Sans adaptateur, relecture vide/échec ou texte excessif, UNKNOWN conservé.

## Provenance et corrections de revue

Première version : la concordance acceptait un hash/caption fournis par le caller, défaut P1 reproduit. Cette entrée déclarative a été supprimée après un test rouge/vert. Le lecteur produit lui-même chaque crop depuis le PNG validé (inset2px, agrandissement3× Lanczos), calcule le SHA256 des octets PNG réellement envoyés et appelle le `RapidOcrAdvancedExtractionAdapter` existant. Les tokens primaires ne sont jamais transmis au moteur. Le paramètre accepte seulement l’adaptateur concret de confiance configuré côté système, ou None; aucun body/acte métier externe n’est ajouté. Les traces gardent modèle/hash, parseur/version, crop/hash, échec et brut. Une relecture déclarative, un adaptateur arbitraire ou un hash client ne peuvent qualifier le texte.

RapidOCR local, modèles existants PP-OCRv6, ONNX threads1, classe d’orientation désactivée pour ce crop droit seulement; réseau bloqué par audithook. Relecture indépendante comme nouvelle exécution sur un crop : même famille de moteur que l’OCR primaire, erreurs communes encore possibles. Concordance candidate ≠ vérité lexicale ni validation métier.

Rouges/verts observés : lecteur absent; ordre des traits; rectangles composites; fermeture à coin disjoint; refus des relectures déclaratives.22tests dédiés /210ciblés verts; revue P1 corrigée et revérifiée. Ruff1207fichiers,mypy622sources verts. Semgrep1.179.0,225règles configurées/2fichiers,0finding/0erreur; Bandit et secrets ciblés sans alerte. Suite backend exhaustive finale : 2511/2511,0échec/ignoré,couverture88.22%,1718.71s, 20avertissements de dépendances par lots.51lots/408fichiers disjoints,manifestes/hashes/JUnit,couverture cumulée et gatefinal85,50% inchangé. PostgreSQL tmpfs borné768MiB/buffers32/WAL128/checkpoint30s, sans volume/localhost, retiré et absence vérifiée; aucun runtime de production modifié.

## Limites et suite

Pixels <180, traits axiaux≥18px/≤3px, guard intérieur2px, boîtes OCR dilatées1px, reconnaissance de région sans OCR fondée sur encre centrale à6px des bords : calibration bornée150DPI. Le résidu de bord est toujours conservé dans les régions UNKNOWN; ce guard ne qualifie pas le texte. Cadres cassés/arbitraires, texte pâle hors seuil, mauvais encodage et erreurs communes aux deux OCR restent non qualifiés. Ni analyse complète de la page/DCE, ni admission Golden, ni éligibilité réelle. Le ROI et l’OCR primaire sont préexistants; la découverte de toute la page reste ultérieure.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/ink-coverage/`; source-final-controlled.log,qualification et copie immuable,reread-final/crops/modèles,manifestes/JUnit/couverture en cours. Version initiale non liée archivée/non qualifiante. 37fichiers logiciels hérités inchangés; deux nouveaux fichiers intégrés, WIP non commité, aucun push.

SHA256 qualification contrôlée : `824721c591771cd13b731e6ed80d73bb1dca50a3bab2dab05b82c296410cc476`.


## Clôture de la qualification locale

Fichiers : `backend/app/modules/dce/infrastructure/diagram_ocr_coverage.py` et `backend/tests/application/test_diagram_ocr_coverage.py`;aucun fichier hérité changé. Calibration/provenance/refus/échecs/ordre/retry et garde NON couverts par22tests dédiés;210ciblés et2511tests globaux réussis. Semgrep1.179.0 security-audit225règles/2fichiers0finding/0erreur,metrics off;Bandit1fichier applicatif/detect-secrets2fichiers--all-files--no-verify0alerte,scans ciblés sans qualification globale de sécurité. Ruff1207/mypy622,diffcheck et nouveaux fichierswhitespace vérifiés.

Superpowers using/brainstorming/TDD/plan/revue/verification, ECC verification-loop, Graphify avant recherche locale, Context7 + code installé pour raster/Pillow/RapidOCR, Basic Memory miroir explicite smart-ao-v8. Pas de navigation sémantique Serena requise sur ces fichiers précis. Jev/Manus inapplicables à la preuve raster déterministe; OpenDesign/Impeccable/navigateur/REA inapplicables sans UI ni rétro-ingénierie logicielle. Aucune dépendance ajoutée;aucun backend live,VPS,déploiement,effetP3/dépôt externe ouGO public.

La qualification des lacunes est close localement, **la concordance OCR de4cadres et les7chemins restent UNKNOWN**.Les avertissements de dépendances sont consignés dans les logs de chaque lot; aucun warning n’est masqué. L’analyse complète et l’éligibilité réelle ne sont pas prouvées.

**Prochaine étape :** ESSAIS DCE — corriger et requalifier les quatre relectures OCR vides ou divergentes des cadres CEE de Cadarache, puis réévaluer les sept chemins avec preuves pixel/crop/parseur et sans lever UNKNOWN sans preuve; conserver sources, correspondant CEE et REVIEW_REQUIRED. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
