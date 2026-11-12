# ESSAIS DCE — mapping des images natives CEE Cadarache

## Cadrage avant action

**AS-IS :** checkoutprincipal `codex/reconcile-smartao-20261009`,HEAD `30f26934430095632000a1d82519f61dbb4c6411`,39SHA logiciels conformes au checkpoint2544/cov88,24%,WIP conservé. Douze occurrences UNKNOWN,28omissions ;35/63chemins,69/81concordances,0faux sur17cas. Aucun pixel non couvert n'a été exclu par la tranche précédente.

**Risques :** prendre la mauvaise image/page/occurrence, confondre coordonnées normalisées et pixels, oublier rotation/crop/mask/overlay, transformer un match géométrique en identité de contenu, lier une preuve native aux pixels d'un raster altéré. Aucune source ne devient admise par accord OCR.

**Points d'insertion :** preuve locale de mapping et relectures ; lecteurs produits inchangés tant qu'aucun défaut minimal n'est démontré. Source PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`,page42. Le rendu `get_pixmap(dpi=150,alpha=False)` reproduit exactement le PNGtémoin SHA `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`. Imagesxref168/169 extraites séparément,hashées ; placements exacts duPDF.

**Plan minimal :** (1) tester mapping axisaligné sans rotation,cropoffset,masque ni occurrence concurrente ; refuser toute ambiguïté ; (2) vérifier matrice/bbox/allers-retours,extraire crops natifs du placement unique,avec source/page/xref/occurrence/région/hash ; (3) OCRnatif sans texte attendu,puis comparer ; (4) requalifier les douze occurrences et28omissions en distinguant mapping géométrique etmatch de pixels,aucun transfert aux variantes altérées ; (5) revue,contrôles,dossier/plan/index/miroir.

**Tests :** mappingnominal/bornes,floor/ceil,couverture complète ; rotation/skew/masque/multiplesplacements/outside/sourcehash/dimensions refusés ; identitécanonique exactepixels ; rasteraltéré refusé même si sa géométrie coïncide. Aucun I/l/1 remplacé,aucune liaison attendue injectée.

Méthode : skillPDF,Superpowers diagnostic/TDD/verification,ECC eval-harness,Context7PyMuPDF (transform appliqué à l'image normalisée). Pas deUI/migration/API/dépendanceproduit. A1nonadmis,A2HOLD,NO-GOpublic ;aucunVPS/backendlive/corpussupplémentaire/déploiement/push/P3/dépôtexterne.

## Résultats vérifiés

Source : DCE-03, CEA Cadarache, CCTP commun indice 2, annexe 13, page 42/44, logigramme « Variation de vitesse (BAT-TH-112) ». Les deux images incorporées ont été extraites sans modification. L'image inférieure contenant les neuf cadres est xref 168, occurrence 35, JPEG DeviceRGB 1684 × 1460, sans masque, SHA-256 `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. L'image supérieure xref 169 ne contient pas ces régions. La résolution placée est environ 319 DPI ; la métadonnée 96 DPI ne décrit pas ce placement.

Les neuf mappings sont recalculés depuis la matrice de placement PDF et les coordonnées du rendu 150 DPI. Les régions natives utilisent floor/ceil vers l'extérieur et peuvent inclure une marge. PDF, page, xref, occurrence, matrice, région, image, crop et entrée OCR ont chacun leur provenance et SHA-256 dans les preuves privées. Aucun resize n'est appliqué au crop natif ; les recettes OCR ajoutent une marge blanche de huit pixels, et la troisième utilise gris/autocontraste, avec un hash distinct.

**Témoin de contenu : 9/9 régions canoniques reproduites exactement en RGB.** Le rejeu isolé utilise les opérandes originales du PDF, son clipping et DeviceRGB. La première insertion naïve n'était pas qualifiante (ICCBased et arrondis de matrice produisaient des différences) ; ses diagnostics sont conservés séparément. La preuve finale concerne exclusivement les neuf intérieurs du rendu canonique 150 DPI, pas la page entière ni un raster transformé.

### Relectures natives

27 lectures exécutées : RapidOCR RGB, Tesseract français RGB et RapidOCR gris/autocontraste. Les captions attendues sont consultées après les lectures, seulement pour comparaison. Cinq cadres ont trois accords complets : NON ELIGIBLE, moteur existant, variateur déjà présent, correspondant CEE et moteur neuf. Quatre restent divergents :

| Cadre / tokens | RapidOCR RGB brut | Tesseract brut | RapidOCR gris brut |
|---|---|---|---|
| T90 | Le moteur est de classe lE2 | Le moteur est de classe IE2 | Le moteur est de classe IE2 |
| T88 | Moteur asynchrone? | \| Moteur asynchrone ? | Moteur asynchrone? |
| T91, T92 | Le moteur est de classe lE3 ouIE4 | Le moteur est de classe IE3 / oulE4 | Le moteur est de classe lE3 ou IE4 |
| T98 | ELIGIBLE | \| cu \| | ELIGIBLE |

Aucune substitution I/l/1 ni correction devinée. Un accord entre moteurs n'admet pas la source et ne prouve pas l'éligibilité réelle d'un moteur. UNKNOWN, REVIEW_REQUIRED et la sortie « contacter votre correspondant CEE centre » sont conservés.

### Douze occurrences et 28 omissions

Les douze occurrences des variantes ont un mapping géométrique vers l'image originale, mais **0/12 ont des pixels de cadre identiques au témoin canonique**. Aucun transfert de preuve native n'est autorisé : leur render_sha256 et leur scope d'origine sont conservés. Les douze restent UNKNOWN / REVIEW_REQUIRED.

Requalification par vérification des 17 résultats du dernier rejeu, de leurs hashes et de l'absence de transfert ; aucune nouvelle extraction des 17 rasters dans cette tranche. Sur les neuf cas préservants : **35/63 chemins retrouvés, 28 omissions maintenues** ; zéro faux chemin ou chemin critique interdit sur les 17 cas. Ces résultats antérieurs ne deviennent pas des chemins prouvés sur pixels natifs. `requalification.json` rend cette distinction explicite.

## Contrôles et revue

- TDD privé : échecs initiaux du mapping observés, puis corrections minimales ; régression de l'occurrence 0 observée rouge puis verte. **9/9 tests privés** : nominal, bornes, recouvrement partiel, ambiguïté, masque, skew, dimensions et placement incohérents.
- **126/126 tests produit ciblés** : couverture OCR, topologie, reconstruction découverte et chemins conditionnels. Les 39 hashes logiciels correspondent toujours au checkpoint global antérieur ; aucun code produit ni dépendance produit modifié dans cette tranche.
- Compilation des cinq scripts privée réussie ; Ruff helper/tests vert. Semgrep **1.179.0**, configuration `p/security-audit`, **225 règles / 5 scripts**, zéro finding, zéro erreur et zéro timeout signalé. Ce scan ne remplace pas la preuve géométrique ni les tests.
- Revue technique indépendante sans réexécution OCR : neuf mappings/crops, 27 entrées OCR, neuf témoins de dessin et douze refus recalculés ; aucun défaut critique identifié. Les hashes de script et mapping enregistrés correspondent aux fichiers exécutés.
- Receipt final : scripts, résultats, PDF/rendu, images incorporées, crops/entrées OCR, dessin isolé, modèles RapidOCR, clés caractères, Tesseract/fra et versions SDK liés par SHA-256. Contrôles du diff et références documentaires effectués à la clôture.

Skills réellement appliquées : PDF ; Superpowers using-superpowers, systematic-debugging, requesting-code-review et verification-before-completion, avec cycle TDD ; ECC eval-harness. Context7 a vérifié le contrat de transformation PyMuPDF. UI, navigation navigateur, migration et typage produit inapplicables ici.

## Preuves reproductibles et limites

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-image-mapping/` : `native_mapping.py`, `test_mapping.py`, `prepare_mapping.py`, `verify_draw.py`, `read_native.py`, `mapping.json`, `draw-verification.json`, `native-readings.json`, `requalification.json` et `receipt.json`. Avec le Python `.venv` du checkout principal : exécuter les tests privés puis, dans l'ordre, les scripts de préparation, dessin et lecture. Runtime OCR et modèles sont référencés dans les scripts/receipt. Le dossier contient aussi des diagnostics initiaux explicitement non qualifiants.

Qualification locale PARTIAL : profil sans rotation, décalage de cropbox, masque ou skew ; aucun support générique de ces variantes démontré. Ni les quatre cadres natifs divergents ni les douze occurrences altérées ne sont résolus. La suite globale **2544/2544, couverture 88,24 %** est antérieure et n'a pas été relancée ici ; seules les preuves ciblées ci-dessus sont fraîches. Aucun backend live, UI, VPS, déploiement, P3, dépôt externe, push ou GO public ; WIP préexistant conservé et non commité. A1 non admis, A2 générique HOLD, NO-GO public maintenus.

## Correction de méthode — 14 octobre 2026

La marge dite blanche des recettes RGB paddées de cette preuve était **rouge RGB(255,0,0)** : `ImageOps.expand(...,fill=255)` sur RGB. La marge grayscale était blanche. Les hashes, géométries et textes bruts restent exacts ; la description de couleur et la qualification comme essai RGB avec marge blanche sont corrigées. Les refus UNKNOWN demeurent, aucune source n’était admise. Ces lectures ne prouvent pas seules que leurs parasites venaient du PDF. Les fichiers historiques sont conservés sans réécriture ; la comparaison corrigée à coupe identique et sa portée sont dans [Franges/padding et relectures corrigées](DCE_FRANGES_PADDING_RELECTURES_CEE_2026-10-14.md). Pas de relecture globale rétroactive des neuf cadres ni transfert aux variantes.
