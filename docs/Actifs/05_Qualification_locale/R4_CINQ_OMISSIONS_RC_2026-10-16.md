# R4 — cinq omissions RC résiduelles — 16 octobre 2026

## Statut

Qualification technique locale acquise sur le périmètre synthétique testé : **2 751 tests backend réussis, 2 avertissements, 1 302,60 s, sortie 0**. A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## AS-IS, risques et insertion

Checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. Les 111 entrées Git préexistantes sont conservées. Les fichiers du détecteur/tests sont encore non suivis : un diff HEAD seul ne couvre pas leur delta. Baseline exacte du détecteur et du reader conservée dans les preuves privées.

Le dossier R4 chaînes laissait cinq occurrences omises : CCAP/CCTP dans une ligne de cellules, CCAP/CCTP après un titre de continuation et CCAP sous un en-tête scoped lot 2. Risques : attribuer la polarité d'une colonne voisine, reprendre un titre sans antécédent, aplatir une négation, inventer la portée lot, déplacer les offsets UTF-8 ou allonger le coût de parsing.

Insertion minimale : `application/document_announcements.py`, `infrastructure/case_dce_reading_reader.py` et leurs deux fichiers de tests. Aucun schéma, migration, dépendance, DTO public, écriture métier ou interface modifié. M2-027/M2-029 : fait/version/locator/portée et inconnu explicites; ni mention ni inventaire technique ne prouvent présence ou complétude.

## Plan et comportements à prouver

- [x] Reproduire les trois formes d'omissions et les contre-exemples de négation/lot.
- [x] Reconnaître une ligne délimitée par `|` seulement si toutes ses cellules sont des noms documentaires complets. La région source est la cellule exacte, sans délimiteur. Aucune sémantique de colonne ou géométrie de tableau PDF déduite.
- [x] Accepter le seul titre explicite `Composition du dossier — suite` (tiret court/long, casse, espaces, deux-points final permis), uniquement avec en-tête déjà prouvé et sans rupture. Le titre reste dans les ancres BRIDGE, l'en-tête original dans HEADING. Toute portée/phrase supplémentaire rompt cette reprise.
- [x] Reconnaître `pour le lot N` dans la composition sans modifier les octets; conserver le numéro cité comme candidat, applicabilité UNKNOWN. Désaccord avec le lot local ou portée locale plurielle/disjonctive : AMBIGUOUS, numéros vides.
- [x] Propager AMBIGUOUS vers REVIEW_REQUIRED dans le reader existant.
- [x] Exercices PDF → extraction → PostgreSQL → projection : source/version/input hash/fragment hash/page/région, répétition stable, tenant étranger refusé et absence de texte privé dans la projection.
- [x] Finir la suite globale, vérifier les empreintes, retirer uniquement la base jetable puis mettre à jour plan/index/Basic Memory.

## Preuves ciblées et revue

Preuves privées : `/home/noor/.local/share/smartao-proofs/r4e-20261015/` (travail commencé le 15, repris le 16). `red.log` : 5 échecs attendus et 103 réussites; les trois formes omises, tableau négatif et désaccord lot étaient rouges. `targeted.log` : 1 échec/35 réussites, claim AMBIGUOUS mais scan encore CANDIDATES_ONLY. Correctif du reader puis `targeted-green.log` : **36 réussites, 40,16 s**. `lot-red.log` : deux portées locales ambiguës rouges; correction conservative. Détecteur final : **112 tests purs réussis** (18 supplémentaires par rapport aux 94 de R4d).

Revue indépendante Superpowers, sans édition ni DB : deux défauts concrets confirmés, portée lot ambiguë et coût quadratique d'espaces dans le titre de continuation. `caption-cost-red.log` : budget deux secondes réellement dépassé avant correction. Quantificateurs possessifs, comme dans le motif OBJECT_GAP déjà installé, puis test vert. Relecture indépendante finale : 112 tests verts; reproduction de 50 000 espaces en 0,053 s; **52 488 combinaisons** whitespace/ponctuation comparées, aucune différence d'acceptation ancien/nouveau motif. Contrôle complémentaire de l’intégrateur persisté dans `caption-differential.json` : 15 552 combinaisons, zéro différence; rejet de 7 900 / 50 000 / 999 950 espaces en 0,034 / 0,223 / 4,961 ms sur cette machine. Ces comparaisons bornées ne sont pas des preuves formelles de complexité. Limite de candidats aussi vérifiée dans la boucle de cellules, sans attendre la fin de ligne.

`measure.py` compare le détecteur avant/après sur la référence **inchangée** `rc_document_announcement_sequences_v1.json`, SHA-256 `1b586c36ba7945be9c916198a08c9dad58e7890197b34bacca3716931eb913d3` : 14 cas, 22 occurrences attendues, **17→22 TP, 5→0 FN, 0→0 FP**. Chaque source et en-tête est reconstruit depuis ses régions originales. Les libellés UNQUALIFIED du fixture restent historiques; leur nouvelle qualification bornée est consignée ici. Référence Codex synthétique, pas Golden humaine ni métrique d'analyse de DCE entier.

## Contrôles et limites

Ruff backend/scripts et mypy 624 fichiers : verts. Semgrep **1.179.0**, `p/security-audit`, **225 règles / 4 fichiers**, 0 finding, 0 erreur; liste effective des quatre chemins vérifiée dans JSON malgré le message générique sur les fichiers Git. Analyse locale, métriques désactivées, aucun upload des résultats. Ces contrôles ne certifient pas l'absence de vulnérabilité.

Une première passe globale a été interrompue intentionnellement pour corriger le coût repéré en revue : 12 réussites, 1 avertissement, 16,38 s, sortie interrompue, **non qualifiante**. Journal conservé `backend-interrupted-review.log`. Seul runner final : session **92320**, journal `backend-global-final.log`; code gelé, empreintes dans `code-sha256.txt`. Base explicite jetable sur loopback port 55439, conteneur `smartao-r4e-proof-20261015`, label `smartao.proof=r4e-20261015`, `SMART_AO_TEST_DISPOSABLE_DATABASE=1`, fixture de restauration C5 non conservée. Aucun runner DB concurrent.

Méthodes réellement appliquées : Graphify pour orientation avant recherches, Superpowers cadrage borné/TDD/revue/vérification, ECC verification-loop/security-review et Basic Memory pour le contexte antérieur. Pas de nouveau comportement de bibliothèque nécessitant Context7; aucune navigation sémantique Serena. Jev/Manus non utilisés : parsing déterministe borné et revue reproductible. Aucune édition visuelle : OpenDesign/Impeccable et preuve navigateur non applicables; aucun test Playwright revendiqué. Le helper PDF et l'extracteur existants sont réutilisés.

Présence/applicabilité/criticité restent UNKNOWN. Les tableaux qualifiés sont les seules cellules textuelles délimitées et non ambiguës : ni tableaux raster, ni multi-colonnes géométriques, ni cellules fusionnées ne sont qualifiés. Les sources ne sont pas promues. MFA, FINANCIAL_PRIVATE, append-only, droits, tenant, retries et contrats P5 inchangés; la lecture répétée/tenant/hash est exercée, pas une nouvelle qualification live de ces sous-systèmes. Aucun corpus réel, backend live, VPS, déploiement, effet P3, dépôt externe, commit ou push.

## Résultat final et limites ouvertes

Suite backend complète finale : **2 751 réussites, 2 avertissements, 1 302,60 s (21 min 42 s), sortie 0**. Les 112 tests purs et 36 tests PDF/SQL sont inclus dans ce global sur les quatre empreintes finales inchangées. Aucun test backend ignoré. Les deux avertissements sont la dépréciation Starlette/httpx et un alias Pydantic `authorization` sans effet dans le contexte de génération de schéma du test de double clic capability-proposal; pas de correction opportuniste de ces avertissements. Le journal final prévaut sur la première passe interrompue.

PostgreSQL jetable : étiquette exacte `r4e-20261015` relue, table Alembic vérifiée à zéro ligne après le global; seul `smartao-r4e-proof-20261015` a été arrêté et retiré. Aucun service live touché. WIP conservé, HEAD et branche inchangés, aucun commit/push. Ruff/mypy/Semgrep/diff et revue décrits ci-dessus; aucun secret ajouté dans les quatre fichiers examinés.

La suite Web et le navigateur ne sont pas rejoués : aucun fichier frontend ni contrat DTO modifié. Leur dernière qualification demeure celle du dossier R4d, sans être présentée comme une preuve fraîche. Les cinq omissions de cette calibration sont corrigées; la qualité des exigences RC hors calibration, des tableaux géométriques/raster et de DCE réels entiers reste à éprouver. Aucune admission, analyse complète ou GO public déduit.

Plan, case, journal et index actualisés; une seule tranche active vérifiée. Basic Memory `smart-ao-v8` synchronisé puis relu : résultat 2751, retrait du conteneur et prochaine étape exacte concordants. Le plan reste l’autorité opérationnelle.

Prochaine étape : R4 — auditer et éprouver la chaîne existante d’analyse des exigences RC sur un jeu synthétique gelé hors calibration, avec négations, portée lot/version, contradictions et rectificatifs; mesurer omissions, faux positifs et ancres sans déduire la complétude; préserver UNKNOWN, A1 non admis, A2 générique HOLD et NO-GO public.
