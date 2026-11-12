# Essais DCE — chemins de flèche candidats — 12 octobre 2026

## Conclusion

DCE-03 désigne le dossier **CEA Cadarache — petits contrats de travaux d’entretien, contrats cadres2027–2031**. La pièce examinée est `CCTPC.pdf`, **CCTP commun à tous les lots**, référence `DG/CEACAD/DSTG/STL/GTP/CCTP-22-057`, indice2. Elle provient de `Accord-Cadre Patrimoine Centre CADARACHE /DCE.zip` → `Documents Communs CCTPC CCTG Procédure OS.zip`. Sa page42/44 contient l’annexe13 « Logigramme CEE ». Les trois références concernent le diagramme **Variation de vitesse (BAT-TH-112)**.

La relecture technique Codex de la page complète confirme les trois relations documentaires : OUI du moteur existant déjà équipé → NON ELIGIBLE; NON de « Moteur asynchrone? » → NON ELIGIBLE; sur la branche asynchrone OUI, classe IE3/IE4 → ELIGIBLE. `T89` se lit visuellement **OUI**; le texte brut OCR **Iño** est conservé. Les deux premières branches convergent effectivement vers un tronçon descendant commun.

**Pertinence selon M2-026/027/029 :** ces essais vérifient la lecture de conditions techniques/environnementales et d’un financement CEE, les négations, les branches et leur provenance. « ELIGIBLE » désigne le résultat du logigramme CEE du document, pas l’admissibilité d’une entreprise à la consultation. Les préconditions amont doivent accompagner chaque résultat. La branche IE2 demande de contacter le correspondant CEE; aucun résultat binaire ne peut être inventé. Aucune éligibilité d’un moteur réel ou validité réglementaire actuelle n’est qualifiée.

La relecture technique source est qualifiée sur ces trois références. Les sorties du détecteur existant restent `SOURCE_PATH_CANDIDATE`/`UNKNOWN` tant que la reconnaissance automatique correspondante n’est pas prouvée. Le dossier reste `REVIEW_REQUIRED`, sans admission Golden DCE ni conclusion de complétude. Cette revue est un acte technique IA, aucun acte humain n’est simulé.

## Portée et méthode

- Source privée DCE-03, page 42 sur 44, SHA-256 `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`.
- Rendu complet à 150 DPI, dimensions et pixels relus depuis le PDF; SHA-256 du rendu `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.
- OpenCV 5.0.0 : Canny seuils bas/haut 30/100, puis `HoughLinesP` (`rho=1`, `theta=pi/180`, `threshold=18`, `minLineLength=35`, `maxLineGap=3`). Les segments candidats sont rapprochés des ancres OCR source/cible et réunis par intersection orthogonale. Une région de preuve par relation borne le tracé; les ambiguïtés de score à 2 points ou moins sont refusées.
- Les coordonnées ci-dessous sont celles du rendu complet. Les extrémités et la pointe sont des candidats géométriques calculés depuis les segments détectés et les ancres de texte; le détecteur ne prouve ni la forme d’une tête de flèche, ni sa sémantique.

## Trois relations examinées

| Référence | Ancres texte et contexte | Chemin candidat (pixels du rendu) | Écarts source / cible / jonction | Qualification |
|---|---|---|---|---|
| `STRUCT-009`, région `[290,1180,590,1490]` | `OUI` (`T82`); question `T83/T85/T86`; cible `NON ELIGIBLE` (`T94/T93`) | `(401.5,1223) → (345,1223) → (345,1436)` | `1 / 13 / 0 px` | Chemin géométrique candidat; label OCR OUI ancré; sémantique UNKNOWN |
| `STRUCT-010`, région `[290,1240,750,1490]` | `NON` (`T87`); question `Moteur asynchrone?` (`T88`); cible `NON ELIGIBLE` (`T94/T93`) | `(539,1280) → (345,1280) → (345,1436)` | `0 / 13 / 0 px` | Chemin géométrique candidat; label OCR NON ancré; sémantique UNKNOWN |
| `STRUCT-011`, région `[680,1360,850,1510]` | Critère `Le moteur est de classe IE3` / `ou IE4` (`T91/T92`); cible `ELIGIBLE` (`T98`); aucun label OUI/NON rattaché dans cette région | `(757.5,1404) → (756,1404) → (756,1463)` | `3 / 13 / 0 px` | Chemin géométrique candidat; aucun label de branche inventé; sémantique UNKNOWN |

Les chemins `STRUCT-009` et `STRUCT-010` ont des bras d’entrée distincts et convergent vers un segment cible partagé. Le sélecteur a trouvé un candidat unique dans chacune des trois régions selon son seuil; aucune relation n’a été refusée dans ces trois références. Cela ne signifie pas que l’ensemble du logigramme est complet ou que toutes ses branches ont été détectées. Le texte OCR `T89` (`Iño`), visible en amont de `STRUCT-011`, n’est pas utilisé pour produire une étiquette `OUI`.

## Implémentation et preuves

- `backend/app/modules/dce/application/structure_projection.py` conserve une projection pure, immuable et liée au tenant/document/version, au PDF, au rendu, à la page et aux régions. Elle refuse les identifiants de relation dupliqués même si l’ordre des IDs diffère, ainsi que les chemins de longueur nulle. Aucun endpoint, writer, migration ou effet métier n’est ajouté.
- `backend/tests/application/test_dce_structure_projection.py` : deux nouveaux tests de régression ont d’abord échoué sur les IDs réordonnés et le chemin nul, puis les **57 tests ciblés** ont passé. Ils couvrent aussi scope/hash étrangers, régions, coordonnées, ordre, convergence, négation, `UNKNOWN` et ambiguïtés.
- Suite backend complète sur le checkout principal et PostgreSQL jetable tmpfs : **2358/2358**, couverture **88,05 %** (seuil 85,50 %), 2 avertissements connus Starlette/httpx et Pydantic `Field.alias` sans effet. La première mesure dans le worktree a rapporté 46,22 % à cause des sources importées depuis l’installation éditable du checkout principal; elle n’est pas retenue comme couverture. La mesure qualifiante est celle du checkout principal.
- Ruff global : vérifications réussies; format : 1173 fichiers déjà formatés. Mypy : 615 sources sans erreur. Semgrep 1.179.0, `p/security-audit`, 225 règles sur 2 fichiers, 0 finding/0 erreur; métriques désactivées. Detect-secrets : 0 finding sur les 2 fichiers. Bandit sur le module : 0 finding, 0 test ignoré.
- Le projecteur reste un composant candidat sans caller HTTP/SQL vérifié pour exposer ces données. Les annotations visuelles et sorties détaillées sont dans `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/three-arrow-candidates.json` et les artefacts privés associés. Aucun PDF, image, texte de DCE ou manifeste d’annotation n’est ajouté au dépôt.

## Limites et statut conservé

Aucune lecture métier humaine n’a validé les associations ou leur orientation. Les ancres OUI/NON sont des résultats OCR situés, pas des décisions d’éligibilité. La pointe candidate est l’extrémité de la polyligne détectée, pas une reconnaissance certifiée de la tête de flèche. Les faux négatifs du détecteur, les segments manquants et l’exhaustivité du diagramme n’ont pas été qualifiés.

`semantic_state=UNKNOWN`, `business_eligibility=UNKNOWN`, `lot_applicability=UNKNOWN`, `admission_granted=false`, `REVIEW_REQUIRED`. A1 non admis, A2 générique HOLD et NO-GO public maintenus. Aucun corpus réel, backend live, UI, VPS, déploiement, push, effet P3, dépôt externe ou export exécuté.

Méthode appliquée : Superpowers systematic-debugging, TDD, requesting-code-review et verification-before-completion; ECC verification-loop; Context7 pour le contrat OpenCV; revue géométrique locale et Basic Memory. Graphify/Serena ont servi au contexte de reprise; Jev, Manus, OpenDesign et Impeccable n’étaient pas pertinents à ce changement sans UI.

## Historique — fiche de revue humaine préparée, puis demande retirée

**Correction de périmètre du12/10 :** l’Owner demande à Codex de décider de la pertinence des résultats selon le cahier des charges pendant les essais. La demande d’attestation humaine ci-dessous est donc retirée comme prérequis à la lecture technique. Elle reste une trace historique non exécutée; ses PENDING ne constituent plus un blocage du travail logiciel.

La requête locale `human-review-request.json` lie le PDF source, la page42, les trois images exactes et les quatre propositions ci-dessous. Son SHA-256 est `126d9a5af8646c10e70da7f96e451bc9c992380f2cc4f3c4ba5a8af0f9efd40a`. Les trois PNG ont été comparés octet pour octet à un nouveau rendu de la même page avec leurs rectangles PDF et300DPI : concordance3/3. Les extraits2 et3 ont été présentés dans la conversation pour revue.

| Item | Proposition soumise au lecteur humain | Décision |
|---|---|---|
| R009 | La branche OUI du moteur déjà équipé d’un variateur de vitesse rejoint NON ELIGIBLE. | PENDING |
| R010 | La branche NON de « Moteur asynchrone? » rejoint NON ELIGIBLE via le tronçon partagé. | PENDING |
| R011 | Le moteur de classe IE3 ou IE4 rejoint ELIGIBLE. | PENDING |
| T89 | Le texte imprimé à l’ancre T89 est OUI; le texte brut OCR reste Iño. | PENDING |

La dernière proposition est une lecture visuelle technique proposée, encore non validée humainement. Aucun nom, rôle métier, date de décision ou confirmation n’est rempli à la place du lecteur. Son retour doit identifier les items validés/corrigés/incertains et son nom/rôle; l’acte sera lié à cette requête exacte et daté à réception. La qualification portera seulement sur ces relations documentaires; l’éligibilité réelle d’un moteur, l’applicabilité d’un lot, les autres branches et l’admission Golden restent hors de cet acte.

Vérifications de cette préparation : source SHA relue, page/crops3/3 exacts, requête hachée, décisions vides et statut PENDING; aucun code modifié ou test backend rejoué pour cette seule préparation documentaire. UNKNOWN/REVIEW_REQUIRED restent actifs.

## Revue technique clôturée après correction de périmètre

La page complète a été rerendue et son SHA vérifié. Le titre/indice/page ont été relus dans le PDF natif. Les trois relations et la lecture visuelle T89=OUI sont consignées dans `codex-technical-review-20261012.json` hors Git, avec `reviewer_kind=AI_ENGINEERING_REVIEW` et `human_act=null`. La requête humaine précédente est explicitement supersédée; aucun retour humain n’est inventé.

La lecture source est pertinente pour les axes périmètre technique, environnement/réglementation et financement de M2-026; M2-027 impose source/version/locator, applicabilité et inconnu explicites; M2-029 interdit une conclusion de dossier complet lorsque des pièces critiques restent illisibles/non extraites. Ces exigences n’imposent pas un visa humain sur chaque preuve technique d’ingénierie. Les décisions humaines engageantes et l’admission Golden restent distinctes.

Contrôles : rendu source SHA exact, lecture de la page complète,3relations et1label relus, acte technique explicite sans acte humain, un seul marqueur actif et diff-check. Aucun code modifié ni suite backend rejouée pour cette correction documentaire; les résultats2358/2358 et88,05% restent ceux du snapshot logiciel testé précédemment. Méthode : Superpowers pour la reprise, ECC living-docs-governance pour la correction datée du statut, Graphify pour les autorités, PDF/PyMuPDF pour les preuves; aucun workflow d’envoi externe, UI ou déploiement.

Prochaine étape : ESSAIS DCE — automatiser et qualifier les pointes de flèche et les étiquettes OUI/NON sur les trois références CEE de DCE-03 page 42, avec contre-exemples synthétiques, conditions amont, provenance et OCR brut conservés; refuser les ambiguïtés sans promotion automatique des sources. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Suite de cette preuve : [pointes et labels automatiques CEE](DCE_POINTES_LABELS_AUTOMATIQUES_2026-10-12.md). Le plan global porte seul le statut et la prochaine étape actuels.
