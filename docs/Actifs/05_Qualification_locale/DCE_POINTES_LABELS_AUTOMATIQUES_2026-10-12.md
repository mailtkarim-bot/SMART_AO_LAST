# Essais DCE — pointes et labels automatiques CEE — 12 octobre 2026

## Résultat local

Sur les trois références du logigramme CEE « Variation de vitesse (BAT-TH-112) » du CCTP commun CEA Cadarache, indice 2, annexe 13 page 42/44, le détecteur reconnaît les têtes dans les pixels et le qualificateur conserve les textes de branche. Il s’agit d’une qualification guidée par les trois références et les segments Hough précédents, pas d’une extraction exhaustive du diagramme.

| Référence / token | Résultat automatique | Région / contexte |
|---|---|---|
| STRUCT-009 | Pointe candidate `(344,1443)` | Région `[339,1436,348,1444]`, branche OUI, issue documentaire NON ELIGIBLE CEE |
| STRUCT-010 | Même pointe candidate `(344,1443)` | Jonction partagée, branche NON de « Moteur asynchrone? », même issue documentaire |
| STRUCT-011 | Pointe candidate `(757,1471)` | Région `[752,1464,761,1472]`, critère IE3/IE4 vers ELIGIBLE CEE; aucun OUI/NON inventé sur cette arête finale |
| T82 / T87 | Relecture OUI / NON | OCR brut OUI / NON conservé |
| T89 | Relecture candidate OUI | OCR brut Iño conservé; label de la branche asynchrone amont, pas étiquette attribuée à STRUCT-011 |

Les trois observations concernent **deux pointes physiques distinctes**, dont une commune à deux bras. Le source SHA est `263c2dfdea1d010c1b02d6387ab6eef7d8fdab4e1d2fabd32e32ab3bd133ad8d`; le rendu150 DPI SHA est `e2d7b37426d89c8483d9a9260e8dad7d0792c399560b7ac4b17cbf579e788e79`.

Pièce `CCTPC.pdf`, référence `DG/CEACAD/DSTG/STL/GTP/CCTP-22-057`; l’identité et l’origine complète du dossier sont dans la [revue source](DCE_CHEMINS_FLECHES_QUALIFICATION_2026-10-12.md).

## Insertion et contrat

AS-IS : l’extrémité d’un segment Hough n’était pas une reconnaissance de tête; T89 était Iño. Risques : pointe parallèle attribuée au mauvais axe, tête concurrente ignorée, tige/rectangle interprété comme pointe, texte de sortie assimilé à un label, OCR retourné, perte de provenance.

Trois nouveaux fichiers :

- `backend/app/modules/dce/application/diagram_evidence.py` : observations immuables, qualification exacte OUI/NON, OCR brut et relecture séparés, scope/région et SHA/ID/version de parseur obligatoires pour la relecture. Contradiction, texte vide ou sortie ELIGIBLE/NON ELIGIBLE restent UNKNOWN.
- `backend/app/modules/dce/infrastructure/diagram_image_reader.py` : décodage local PyMuPDF, PNG de 20 Mo maximum/25 millions pixels, SHA et dimensions vérifiés avant inférence, alpha refusé, DPI150 explicite. Une tête pleine doit être reliée à une tige centrée, présenter un rétrécissement, correspondre à l’axe fourni et être unique dans la zone de recherche. Pointes parallèles, concurrentes, détachées/inversées, formes non axiales et bords non qualifiés restent UNKNOWN.
- `backend/tests/application/test_diagram_image_evidence.py` :39 cas synthétiques; aucune pièce réelle en fixture.

Les callers fournissent un contexte autorisé source/version/tenant. Ces composants ne résolvent pas l’ownership SQL ou les droits HTTP; aucun endpoint, writer, table, migration, permission ou dépendance nouvelle. PyMuPDF est réutilisé via l’extra document-advanced. Les offsets/seuils sont calibrés pour des têtes pleines axiales150 DPI; aucune validité générique sur toutes les échelles/couleurs n’est revendiquée.

## Relecture OCR locale

Le caller privé reproduit les crops depuis le PDF source à450 DPI, avec leurs rectangles source, SHA et modèles locaux hachés. Le premier essai avec classificateur d’orientation a donné Ino dans les deux zones OUI : ces relectures ont été refusées. Dans ce rendu source connu droit, l’essai séquentiel `use_cls=False` donne OUI/NON/OUI. Il n’existe aucune conversion codée Iño→OUI et aucun changement du mode OCR global. Les deux campagnes restent privées et distinctes.

La sortie conserve les tokens amont bruts, le contexte CEE et la jonction partagée. Les conditions ne sont pas encore assemblées ni évaluées automatiquement. ELIGIBLE concerne le diagramme de financement CEE du document; éligibilité réelle/réglementaire actuelle et candidature ne sont pas déduites. IE2 reste « contacter le correspondant CEE », aucune issue binaire inventée.

## Preuves et gates

TDD :22 échecs initiaux module absent; six contre-exemples de qualification/provenance/échelle/entier extrême, puis tige décentrée, provenance absente et PNG corrompu reproduits avant leurs correctifs. La revue indépendante a reproduit deux P2 (flèche parallèle et seconde tête au bord); les deux tests rouges puis verts ferment ces cas. La seconde revue confirme leur fermeture sans autre finding concret.39 nouveaux +57 du projecteur = **96 tests ciblés réussis**.

Suite backend complète : **2397/2397 réussis**, couverture **88,08 %** (seuil85,50% inchangé), 1216,81s,0ignoré. Deux avertissements connus : Starlette/httpx déprécié et Pydantic Field.alias sans effet. Ruff global passe; format1176fichiers, mypy617sources. Semgrep1.179.0/p-security-audit225règles configurées,3fichiers explicitement analysés,0finding/0erreur, métriques désactivées. Detect-secrets --all-files/--no-verify0finding; Bandit sur2modules0finding/0erreur. Les journaux, XML et hashes du snapshot sont privés.

La campagne globale intermédiaire a été interrompue avant les correctifs de revue (exit130); elle n’est pas qualifiante. La campagne finale utilise le checkout principal et une base PostgreSQL tmpfs fraîche. Les trois fichiers intégrés correspondent au worktree relu;24 fichiers WIP logiciels hérités inchangés. Aucun commit/push.

## Limites maintenues

`PIXEL_HEAD_CANDIDATE`, `SOURCE_LABEL_CANDIDATE` ou `REREAD_LABEL_CANDIDATE` ne constituent ni admission, ni règle métier appliquée. `semantic_state=UNKNOWN`, `REVIEW_REQUIRED`, lot applicable/éligibilité réelle UNKNOWN; A1 non admis, A2 générique HOLD, NO-GO public. Corpus/images/payloads restent hors Git, aucun acte humain simulé, backend live, UI, VPS, déploiement, effet P3, dépôt externe ou export métier/corpus.

Preuves privées : `/home/noor/.local/share/smartao-proofs/dce-structured-projection-20261012/`, notamment `heads-labels-qualification.json` (orientation initiale), `heads-labels-upright-qualification.json` (relecture droit), crops, hashes des modèles, script reproductible, journal global final et scans.

Méthode : Superpowers using-superpowers/TDD/requesting-code-review/verification; ECC verification-loop; Graphify, Context7 pour les APIs PyMuPDF/RapidOCR et Basic Memory. OpenDesign/Impeccable inapplicables sans UI; Jev/Manus non requis pour ce traitement déterministe.

Prochaine étape : ESSAIS DCE — assembler et qualifier les chemins conditionnels du logigramme CEE « Variation de vitesse » de Cadarache (moteur existant/neuf, variateur déjà présent, asynchrone, IE2/IE3/IE4), en conservant les jonctions, la sortie « contacter le correspondant CEE », les sources et UNKNOWN; mesurer les relations manquantes sans conclure à une éligibilité réelle ou à une analyse complète. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

Le conteneur PostgreSQL tmpfs dédié a été retiré après contrôle de son ID, label et absence de volume; reçu cleanup-receipt-heads-final.json conservé hors Git. Plan/index/mémoire mis à jour et miroir relu. Le scan Semgrep se limite aux trois fichiers listés, vérifiés dans paths.scanned; le reste du dépôt est exclu de ce scan ciblé. Aucun PASS de sécurité global n’est déduit.
