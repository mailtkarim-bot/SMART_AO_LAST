# ESSAIS DCE — réparation des quatre relectures OCR CEE

## Cadrage et plan minimal

**AS-IS :**2cadres vides,1espace fusionné (« unmoteur »),1apostrophe typographique;7chemins UNKNOWN. **Risques :**corriger les mots à partir des attentes, effacer NON/déjà/ou/classes, sélectionner arbitrairement une lecture, perdre crop/hash/parseur. **Insertion :** lecteur infrastructure `diagram_ocr_coverage.py` et son test existant;pas API/UI/migration/dépendance.

**Diagnostic en lecture seule :** bord blanc seul récupère l’asynchrone;gris/autocontraste puis bord8px récupère NON ELIGIBLE et la question variateur. Variations d’échelle2/4/6 ne résolvent pas « unmoteur »; segmentation naïve en mots coupe des lettres, rejetée. Découpage de lignes depuis les pixels (pas les tokens) relit « vitesse sur un moteur ». Source/ancres/lectures/crops bruts conservés dans probes privées.

**Plan :** crop original conservé; repli gris/autocontraste+bord8px+scale3 uniquement après OCR_EMPTY_TEXT; normalisation limitée apostrophe droite/courbe et espace typographique avant?; si désaccord exclusivement d’espaces ou deux lectures de cadre vides, relecture des lignes dérivées de l’encre, acceptée seulement si toutes les lignes sont lues et texte normalisé concorde avec le primaire; caractères complets concordent aussi avec la lecture de cadre lorsqu’elle était non vide. Rien n’est remplacé depuis un dictionnaire attendu. Lectures du cadre/lignes, régions et hashes stockés;conflit/ligne manquante/limite restent UNKNOWN.

- [x] Rouges/verts pour pixels/crop/hash, apostrophe/punctuation, espace reconstruit, ligne vide/contradictoire,NON/déjà/classes/tenant/version/ordre/retry.
- [x] Source :4relectures/9cadres puis7chemins,comparaison seulement après reconstruction,contre-épreuves sans promotion.
- [x] Revue,228ciblés,backend exhaustif/seuil85,50%,Ruff/mypy/Semgrep/secrets/diff/nettoyage.
- [x] Plan/index/journal puis miroir Basic Memory.

Superpowers diagnostic/cadrage/TDD/revue et ECC verification-loop;WIP local conservé. A1nonadmis,A2HOLD,NO-GOpublic;éligibilité réelle UNKNOWN,REVIEW_REQUIRED maintenu.

## Mesures source et provenance

CCTPC commun CEA Cadarache indice2, annexe13 p42/44, BAT-TH-112. Même ROI `(289,1098,881,1521)`,raster150DPI1275×1650;PDF SHA256 `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`,PNG `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`. Aucune relation,groupe,rôle ou phrase attendue donnée au moteur;référence comparée après extraction/reconstruction.

| Mesure | Avant cette tranche | Qualification actuelle |
|---|---|---|
| Cadres textuels retrouvés | 9 | 9 |
| Concordances candidates | 5 | 9 |
| Lectures vides/divergentes non qualifiées | 4 | 0 sur ces9cadres |
| Chemins candidats requalifiés | 0 | 7/7,0manquant/0faux |
| Éligibilité réelle / admission | UNKNOWN / refusée | UNKNOWN / refusée |

Les3sorties NON/2ELIGIBLE/2CONTACT restent des sorties du document,avec leurs conditions amont et leurs sources;pas une éligibilité réelle. La face fermée par routes et le rectangle composite restent séparés des9nœuds textuels;faceUNKNOWN/11pixels résiduels,aucune promotion automatique. OUI/NON et le brut T89 Iño avec sa relecture antérieure restent conservés.

### Quatre cas corrigés

| Cadre | Lecture précédente | Nouvelle preuve |
|---|---|---|
| NON ELIGIBLE | Vide | Crop renforcé ou lignes issues des pixels;NON conservé |
| Moteur déjà existant | « unmoteur » | Trois lignes lues depuis l’encre;« vitesse sur un moteur »;suite des caractères vérifiée |
| Variateur déjà présent | Apostrophe d’un/d'un | Normalisation typographique U+2019→apostrophe;texte brut intact |
| Moteur asynchrone | Vide | Crop à bord blanc/lecture de ligne;question et source intactes |

Les essais d’échelle2/4/6 n’ont pas corrigé la fusion;les découpes en mots ont perdu des lettres et sont archivées,non utilisées. Appliquer le contraste à tous les cadres a fait régresser IE3/IE4 : essai archivé/non qualifiant;lecture originale retenue pour les succès. Chaque crop garde recette,input_region,SHA256,parseur/version;échec original,previous_readings,original_text,original_failure_code et line_readings conservés dans le digest. Le repli n’altère pas le primaire et n’introduit aucun dictionnaire de mots attendus.

### Contre-épreuves sur la source

- NON retiré :3cheminsUNKNOWN,4restent candidats;141pixels non couverts dans ce cadre.
- « centre » retiré :2cheminsUNKNOWN,5restent candidats;74pixels non couverts.
- OCR IE2 retiré :cadre/nœud maintenu UNKNOWN,2cheminsUNKNOWN,5candidats;257pixels non couverts.
- « déjà » effacé dans boîte inchangée :4cheminsUNKNOWN,3candidats;zéro trou spatial mais désaccord textuel;pas de normalisation de mot métier.

## Runtime et mémoire

Un premier prove long a été interrompu exit137;OOM système confirmé au noyau,non qualifiant. Le détecteur installé utilisait `Det.limit_type=min`/736 et agrandissait fortement les petits crops. Le mode max736 a réduit l’empreinte mais perdu une relecture IE3/4,non adopté. Qualification locale bornée :min384,ONNX1thread,arèneCPUdésactivée,recognition-only pour les petits crops≤80px de hauteur;pas de seuil de confiance réduit. Signature/code installé et Context7 vérifiés. Ce réglage appartient à la factory locale de preuve;aucune configuration OCR générale d’autres documents modifiée. Réseau bloqué pendant la preuve;modèles existants hashés. Toutes les lectures source ont ensuite été réexécutées,avec contrôles et contre-épreuves.

40tests OCR dédiés /228ciblés :nominal,scope/version/hash,déjà/NON/classes,ordre/ligne vide/substitution,parents vides,conservationprevious_readings,limite8lignes,retry,hash/région/crop. Rouge puis vert observés pour nouvelles branches;revue indépendante sans défaut bloquant,importF401 corrigé. Ruff1207/mypy622/scans2fichiers verts;backend exhaustif **2529/2529**,0échec/ignoré,en102lots de4/408fichiers,**couverture88.25%**,seuil85,50% inchangé,1707.40s,29warnings de dépendances. Manifestes/hashes/JUnit,aucunfichier omis/doublonné. BasePGtmpfs384MiB/buffers16/WAL64,localhostsansvolume,retirée/absence vérifiée. BasePGtmpfs384MiB/buffers16/WAL64,localhostsansvolume. Campagne finale exhaustive terminée exit0;OOMsource initial et essais régressifs archivés/non qualifiants.

## Limites

Concordance candidate d’OCR,calibration150DPI/traits axiaux/threshold180/≤8lignes;deux passes de même famille peuvent partager une erreur. Pas de preuve de complétude du DCE,page entière,autresrésolutions/polices/rotations,ni éligibilité réelle. UNKNOWN et REVIEW_REQUIRED restent des états explicites,source non admise. Aucunbackend live,VPS,UI,déploiement,push,effetP3,dépôt externe ouGO public.

Preuves privées `.../dce-structured-projection-20261012/ocr-repair/`: probes(padding/contraste/échelle/mots/lignes),reread,bounded sourcefinal,qualification etcopies immuables,model/crop/parseur/hashes,manifestes/JUnit/couverture.37fichiers hérités préservés,deux fichiers logiciels modifiés localement,WIPnoncommité.

SHA256 qualification finale : `8156291ab4d1a7b5b449c6ceb9ee40775844a888a0cf407e3b655eb5a7040ca9`.


## Finalisation locale

Deuxfichiers concernés : `backend/app/modules/dce/infrastructure/diagram_ocr_coverage.py` et son test `backend/tests/application/test_diagram_ocr_coverage.py`;18nouveauxcas/228ciblés(40OCR) et suiteglobale ci-dessus. SDK/runtime/factory source et recettes hachés;code final/37hérités vérifiés. Semgrep1.179.0 p/security-audit225règles/2fichiers0finding/0erreur,metrics off;Bandit1fichier applicatif/detect-secrets2fichiers--all-files--no-verify sans alerte. Scans ciblés,aucune qualification globale de sécurité. Diffcheck/whitespace nouveaux etdocuments verts;WIPnoncommité,aucunpush.

Superpowers using/diagnostic/cadrage/TDD/plan/revue/verification, ECC verification-loop, Graphify consulté avant exploration, Context7 + code installé pour RapidOCR/Pillow, Basic Memory miroir explicite. Serena sémantique non requise sur ces fichiers précis;Jev/Manus non requis pour les preuves raster bornées. OpenDesign/Impeccable/navigateur/REA inapplicables sans UI ou rétro-ingénierie logicielle. Aucune dépendance ajoutée,API/DB/UI/permission/MFA/P3/P5 changée. Source/version/tenant/hash/région/UNKNOWN etREVIEW_REQUIRED préservés.

**Prochaine étape :** ESSAIS DCE — qualifier la robustesse des neuf relectures et des sept chemins CEE de Cadarache sur variantes raster synthétiques, mesurer omissions et faux positifs, et refuser les ambiguïtés; conserver sources, correspondant CEE, UNKNOWN et REVIEW_REQUIRED. A1 non admis, A2 générique HOLD et NO-GO public maintenus.
