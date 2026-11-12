# ESSAIS DCE — registre natif neuf cadres et dépendances

## Cadrage

**AS-IS :** checkout principal `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`, WIP conservé. Neuf mappings natifs qualifiés ; correction de marge RGB ancienne ; crops locaux IE2/IE3/T98 concordants, T92 indécidable, raccord asynchrone refusé. Douze occurrences altérées/28omissions maintenuesUNKNOWN.

**Risques :** réécrire une preuve historique ou masquer une lecture défavorable ; transférer l'accord natif au raster altéré ; appeler textuellement couvert un chemin qualifié géométriquement ou une éligibilité réelle ; ignorer un nœud/condition manquant ou lever un verrou grâce à une nouvelle recette plausible.

**Insertion :** preuve locale privée et documentation ; aucune modification produit/contrat/migration/dépendance/UI. Registre neuf cadres source/page/xref/région/hash exacts ; rattachement descriptif aux sept chemins du checkpoint de découverte existant, aucune reconstruction nouvelle guidée par les références.

**Plan minimal :** relire neuf crops natifs avec RGB/gris et marge réellement blanche, recettes figées avant grading ; sélectionner à l'avance les preuves locales additionnelles IE2/T98 déjà qualifiées ; garder T92/refusasynchrone comme verrous explicites ; lier les désaccords aux nœuds/conditions/chemins existants, mesurer couverture du texte et celle des routes séparément sans qualifier de chemin natif ; conserver tous UNREAD/strips/ancres, requalifier12/28 sans transfert ; revue/contrôles/docs/miroir.

**Tests :** désaccord partagé bloque tous chemins dépendants ; référence absente jamais ignorée ; accord textuel n'admet ni source ni route ; jonction inconnue non whitelisted. Aucun mode/lecture favorable choisi après résultats. A1nonadmis,A2génériqueHOLD,NO-GOpublic maintenus.

Méthodes : PDF, Superpowers diagnostic/TDD/revue/vérification, ECC eval-harness. M2-026/027/029 et CT31-02 maintenus ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/push/GOpublic/corpussupplémentaire.

## Registre source et relectures

Source DCE-03 Cadarache/CCTP commun indice2/annexe13 p.42, PDF SHA `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`, JPEGxref168/occurrence35 SHA `af13f5038a3f8ccfd5d6579d2434462cd4624dd63367400b0d6e5159e63c25d6`. **Neuf cadres inventoriés**, chacun source/page/xref/occurrence/nativebbox/crophash, tokenIDs et liaison au nœud de référence vérifiés. Les aliases servent au rattachement descriptif après extraction, jamais d'entrée au moteurOCR.

**36lectures fraîches**, neufcrops natifs historiques relus avec vraie marge blanche8px : deux recettes RGB/gris-autocontraste × deux moteurs RapidOCRdet+rec/TesseractfraPSM6. Les corps et tous les pixels de marge sont vérifiés ; références comparées après les appels. **5/9concordances fraîches à quatrelectures**. Ce sont deux recettes et deux moteurs, pas quatre preuves indépendantes.

Avant ces lectures, protocol-selection.json a figé deux sources locales additionnelles déjà qualifiées : ligneIE2 du checkpointspatial etspanT98 du checkpointglyphes. Leurs hashes et concordances sont revalidés, toutes les lectures fraîches restent visibles même défavorables. **7/9cadres disposent d'une corroboration textuelle locale**, ce qui n'admet aucune source et ne prouve pas un cadre complet.

| Alias du cadre | Quatrelectures fraîches concordent | Corroboration locale | Verrou persistant / support de dépendance textuelle |
|---|---|---|---|
| no — NON ELIGIBLE | Oui | Oui | Support textuel seulement |
| existing — moteur existant | Oui | Oui | Support textuel seulement |
| equipped — variateur déjàprésent | Oui | Oui | Support textuel seulement |
| ie2 — classeIE2 | Non | Oui, crop localprouvé | Diagnostic glyphe/modes de groupe divergent : verrou conservé |
| contact — correspondant CEE | Oui | Oui | Sortie conservée, sans recommandation réelle |
| async — moteur asynchrone | Non | Non | Raccord ambigu, refus maintenu |
| ie34 — IE3 ou IE4 | Non | Non | T92indécidable ; concordanceIE3 seule insuffisante |
| new — moteur neuf | Oui | Oui | Support textuel seulement |
| yes — ELIGIBLE | Non | Oui, span localprouvé | Support textuel seulement, aucune éligibilité réelle |

Les désaccords d'identifiant d'IE2 restent un verrou malgré sa corroboration de ligne : le registre ne les cache pas pour obtenir un meilleur score. **Six nœuds de support textuel**, trois verrous ; tous les neufsemanticstatesUNKNOWN/statusREVIEW_REQUIRED/admissionfalse/whole_frame_completefalse.

## Conditions et chemins : audit descriptif

Les sept chemins sont les candidats du checkpoint de découverte canonique existant, lié par source/hash/scope. Ils ne sont pas reconstruits à partir de routes attendues ni déclarés prouvés sur l'image native. Le registre contient nœuds, conditions et issue documentaire de référence, explicitement distincte d'une éligibilité réelle. Une condition dont le rôle n'est pas listé dans les nœuds est quand même vérifiée ; aucune référence absente ni jonction inconnue ignorée.

Indices0à6 du registre :

| Verrou | Conditions liées | Chemins candidats affectés |
|---|---|---|
| async / raccord non requalifié | asynchrone OUI/NON | 0,1,2,4,5,6 : **6/7** |
| ie34 / T92indécidable | classeIE3ouIE4 | 2,6 : **2/7** |
| ie2 / diagnostics contradictoires | classeIE2 | 1,5 : **2/7** |

Ces impacts se chevauchent : ils ne s'additionnent pas. **1/7chemins a ses dépendances textuelles de cadres corroborées**, six ont des dépendances manquantes. Le seul chemin textuellement couvert est existing→equipped→reject→no ; cela ne prouve ni son labelOUI/NON, ni sa jonction, ni sa direction.

**0/7routes natives qualifiées, 0labelOUI/NON natif qualifié, 0jonction native qualifiée dans cette tranche.** Tous les chemins restent UNKNOWN/REVIEW_REQUIRED. La qualification antérieure sur le renducanonique est conservée dans son périmètre, pas convertie en preuve native. Les deux branches vers CONTACT_CEE_CORRESPONDENT restent visibles malgré les verrousasync/ie2 ; aucune sortie n'est supprimée.

## Inventaire conservé et couverture manquante

Le registre matérialise **25entrées source/page/xref/région/hash**, pas seulement des liens de dossiers : treizeUNREAD (neuf anciennes +quatre glypheslatérales), sixstrips latéraux, sixfranges ajoutées. Crops comparés aux régions de l'asset natif, conversions et hashes/provenances vérifiés. Ces régions se chevauchent et ne constituent pas une partition disjointe du PDF ; aucun total sémantique exhaustif de pixels n'est inventé. Tout resteUNKNOWN, les parents RGB/PDF/JPEG inchangés.

Les **douze occurrences altérées et28omissions** restent UNKNOWN/REVIEW_REQUIRED. La requalification lie le registre et le checkpoint antérieur, sans nouvelle extraction des17variantes ni transfert de preuve native. Les35/63chemins antérieurs sur neufvariantes préservantes ne sont pas diminués par les nouveaux accords natifs. Distinguer les **six chemins avec dépendances textuelles manquantes** dans le registre natif et les **28omissions de variantes** : périmètres différents. Aucune analyse complète ni admissionGolden déclarée.

## Tests et revue

- TDD : quatre rouges puis quatreverts sur propagation de désaccord, nœudmanquant, accordtextuel jamaisadmission/route, jonctionnonwhitelisted ; deux cas supplémentaires verts (condition absente desnodes, étatUNKNOWNtruthyrefusé). **6/6nouveauxtests /55/55privés** avec les preuves antérieures.
- **126/126produit ciblés**,28,29s : coverageOCR/topologie/discovered/conditional. **39hasheslogiciel inchangés** ; aucun produit/contrat/dépendance/migration/UI modifié.
- Ruff/compile verts ; Semgrep1.179.0,`p/security-audit`,**225règles/4scripts**,0finding/erreur/timeout, local/métriquesoff.
- Revue indépendante sansOCR :36inputs/corps/marges etneufaliases/anchors conformes ; auditdépendances recalculé identique ; inventaire25crops convertis depuis l'asset natif et hashes de provenance exacts. Les accords de texte ne prouvent pasOUI/NON/jonctions/directions. Aucun défaut supplémentaire.
- Receipt privé **322référencesSHA-256** : sources/runtime/modèles/mappings/prépreuves, protocoleselectavantlecture, scripts/helpers,lectures/register/inventaire/requalification/scan.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/native-register-trials/` : `dependencies.py`, `test_dependencies.py`, `protocol-selection.json`, `read_frames.py`, `native-readings.json`, `consolidate.py`, `register.json`, `requalification.json`, `receipt.json`, `semgrep.json`. Python `.venv` du checkout ; tests privés `--noconftest --no-cov`, lecteur `PYTHONPATH=backend`, puis consolidation. Recettes sélectionnées à l'avance, sources historiques non réécrites ; aucune dépendance/modèle ajouté.

## Limites et suite

Registre local PARTIAL, couverture d'inventaire9/9, corroboration7/9, supporttextuel6/9, couverturetextuelledechemins1/7 etroutesnatives0/7 : ces niveaux ne sont pas interchangeables. Le raccord asynchrone est le verrou partagé le plus large(6chemins) ; sa prochaine qualification doit séparer glyphes et raccord avec preuves de régions, en conservant les pixels et son refus actuel jusqu'à preuve suffisante. T92 et diagnosticIE2 restent des inconnus liés aux conditions ; aucun libellé inventé.

Globalbackend2544/2544/couverture88,24% antérieur nonrelancé, produitinchangé. WIPnoncommité/aucunpush ; aucunbackendlive/VPS/déploiement/P3/dépôtexterne/GOpublic. A1nonadmis,A2génériqueHOLD,NO-GOpublic. Skills : PDF,Superpowers using-superpowers/systematic-debugging/test-driven-development/requesting-code-review/verification-before-completion,ECC eval-harness ; Graphify,cahiers,fichiers/preuves exacts consultés. Validation technique distincte d'une décision métier humaine.
