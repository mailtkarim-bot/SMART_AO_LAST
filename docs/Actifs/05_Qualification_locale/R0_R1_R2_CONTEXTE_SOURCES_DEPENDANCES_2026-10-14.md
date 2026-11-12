# R0–R2 — Contexte DCE, sources courantes et composition des extras

**Date :** 14 octobre 2026. **Statut : CLÔTURE TECHNIQUE LOCALE R0/R1/R2.** Corrections et régressions ciblées vertes; backend complet2569/2569, web541/4ignorés, image locale et imports hors réseau qualifiés. Cette clôture ne vaut ni admission du corpus, maturité métier complète ni GO public.

## AS-IS, risques, insertion, plan minimal, tests

Checkout principal `/home/noor/PROJECTS/BTP/SMART_AO_V8`, branche `codex/reconcile-smartao-20261009`, HEAD `30f26934430095632000a1d82519f61dbb4c6411`. WIP préexistant conservé. La [revue globale](../00_Pilotage_et_audits/REVUE_GLOBALE_METIER_CODE_CONCEPTION_2026-10-14.md) identifie trois défauts prioritaires avant la qualification des moteurs métier.

- **AS-IS :** résultats de recherche sans clé/génération; ancienne extraction COMPLETED sélectionnable après refus ultérieur; synchronisations uv exactes successives; moteur de rendu PDF absent de l’extra OCR seul.
- **Risques :** résultat/message d’autre contexte, source obsolète remise en circulation, suppression de preuves historiques, extras précédents retirés, flag OCR activé sans son rendu.
- **Insertion :** hook DCE et tests existants, deux adaptateurs knowledge, tests PostgreSQL dédiés, Dockerfile/extras/lock et tests ops. Aucun nouveau moteur, migration, endpoint ou pouvoir humain.
- **Plan minimal :** reproduire chaque comportement rouge; clés/tokens et refus de réponse; même ordonnancement conservateur que RC appliqué au lecteur et à l’index; une sync avec union explicite des extras; tests consommateurs, contrôles, scan, image locale et suites appropriées.
- **Tests :** contexte Affaire/session/rôle/DCE, réponse discordante/hors ordre/erreur/reset/édition; extraction refusée ou remplacée (timestamp égal compris), index ancien sans réindexation, tenant, changement de version applicable; cinq sélections d’extras et renderer OCR déclaré.

## R0 — contexte exact, requête et réponses tardives

`web/src/features/dce/useDceKnowledge.ts` lie résultats et recherche au scope authentifié/Affaire/DCE connu/requête normalisée. La génération est invalidée au changement de contexte, à l’édition, au reset, lors d’une nouvelle recherche et au démontage. Réponse case/query/version discordante refusée; succès ou erreur ancien n’altère plus la recherche actuelle. Aucun appel ni champ API ajouté.

La revue indépendante a aussi relevé un message tardif préexistant de `loadReading`. Deux nouveaux rouges ont été reproduits et la même discipline de token/cleanup appliquée à la lecture. Une lecture d’un ancien scope ne modifie plus résultats, chargement ni message courant.

**Preuves :** 13 rouges initiaux → 19 verts, puis 2 rouges de lecture → **21 verts**. Tests réels du hook React avec API synthétique; aucune donnée réelle ni recette navigateur revendiquée. Première suite web complète : 539 réussites/4 ignorés; suite finale : **541 réussites/4 ignorés** (66 fichiers, 130,41 s). Typecheck, lint et build web finaux verts; avertissement bundle >500kB conservé, sans augmentation de seuil. Aucune modification de HTML/CSS ou direction visuelle; OpenDesign/Impeccable ne sont pas des preuves de ce correctif interne.

## R1 — fraîcheur avant indexation et avant classement

`knowledge/infrastructure/dce_source.py` expose un prédicat SQL de dernière extraction COMPLETED. Toute extraction plus récente, ou un refus à timestamp égal, empêche le repli sur l’ancienne source. Les extractions COMPLETED à timestamp égal suivent l’ordre UUID déterministe déjà utilisé par l’analyse RC.

`knowledge/infrastructure/vector_index.py` revalide fragment/extraction/version/tenant/Affaire et version actuellement applicable à chaque recherche, avant classement. Aucun ancien vecteur ou fragment n’est supprimé : historique et append-only restent conservés. Pas de réindexation obligatoire pour que le refus devienne effectif; aucune promotion de source.

**Preuves :** **19 rouges PostgreSQL → 19 verts**; sélection élargie DCE/knowledge/API/index : **79 réussites**, avertissement existant Starlette/httpx. Les tests couvrent séparément source et index pour REVIEW_REQUIRED, FAILED_SAFE, UNSUPPORTED, REJECTED_LIMIT, remplacement COMPLETED, timestamp égal, tenant et version applicable. Upgrade et downgrade sont exercés par les fixtures sur la base dédiée. Ruff/format et mypy ciblé verts; architecture/ops élargis : **91 réussites**.

Base utilisée exclusivement : conteneur jetable `smartao-r1-r2-proof-20261014`, PostgreSQL 16 local, port loopback 55439, jeu synthétique. Une connexion initiale bloquée par le sandbox a été rejouée avec l’autorité locale adaptée. Le budget de verrous initial était insuffisant pour le downgrade : il a été relevé uniquement dans ce conteneur. Aucun de ces incidents de préparation n’est compté comme défaut métier ni PASS. La répétition correcte a observé les rouges, verts et rollback réels.

## R2 — union des extras et dépendance OCR

`ops/docker/backend.Dockerfile` accumule les extras demandés et appelle `uv sync --frozen --no-dev --no-editable` une seule fois. Les extras non demandés ne sont pas activés; aucun `--all-extras` ou `--inexact`.

L’extra `document-ocr` déclare PyMuPDF avec la contrainte déjà utilisée par `document-advanced`. Aucun nouveau paquet/version ajouté au graphe; `uv.lock` n’ajoute que deux relations. Ce changement ferme une dépendance de rendu existante, pas la décision de licence SaaS. PyMuPDF AGPL/commercial reste à examiner avant gel public, conformément à la revue globale.

**Preuves :** cinq profils exécutent la vraie sélection shell du Dockerfile avec installateurs/ownership remplacés : base, rag+advanced, OCR seul, advanced+OCR, tous. Quatre profils combinés et le renderer étaient rouges; **6 tests verts**, puis **49 tests ops verts**. `uv lock` réseau de métadonnées publiques résout 195 entrées; `uv lock --check --offline` vert. `uv pip check` : 192 distributions compatibles. Les tests shell démontrent la sélection effective, pas les imports dans l’image finale.

La construction de preuve locale `smartao-r2-proof:20261014` avec les sept extras est **réussie**. Image `sha256:f166f5db31a5d51ca9d4d4b2a273fcab31acf8a6faeab2c928caf2975bfe4a4c`, taille Docker3204644774octets (environ2,98Gio), utilisateur `smartao`. Pas d’application lancée ni déployée.

Probe dans cette image : réseau `none`, Hugging Face/Transformers offline, script synthétique seul monté read-only, budget1536MiB. **8/8imports réussis** : SentenceTransformers5.7.0, Docling2.137.0, RapidOCR3.9.2, PyMuPDF1.28.2, Boto3 1.43.78, HTTPX0.28.1, aiosmtplib5.1.2, icalendar7.3.0. Torch2.13.0+cu130 réalise une opération native CPU correcte; sa compilationCUDA13.0 demeure. Aucun modèle ou document n’a été chargé. Cette preuve ferme l’assemblage demandé, pas la pertinence de chaque moteur ni un profil CPU optimal. La distribution CUDA et la décision de licence PDF restent au programme de qualification séparé.

## Contrôles et clôture restant à consigner

- Suite backend globale sur PostgreSQL dédié : **2569 réussites en 1522,66 s**, journal privé `backend-full.txt`. Avertissements Starlette/httpx et alias Pydantic existants; aucune couverture globale fraîche revendiquée (run sans `--cov`).
- Suite web finale après garde lecture : **541 réussites/4 ignorés**, journal privé `web-full.txt`. Une exécution intermédiaire a eu deux échecs App (C09/404); les contrôles avant/après et le rejeu final passent sans modification de test, assertion ou timeout. Le log intermédiaire est conservé (`web-full-transient-failures.txt`). Aucun défaut produit n’est déduit d’un timeout transitoire.
- Image locale/imports : build et probe **verts**, journaux `backend-image-build.txt`/`image-imports.txt`; probe conservée dans `image-import-probe.py` avec versions réelles et opération CPU.
- Semgrep 1.179.0 : 225 règles sur 7 fichiers ciblés, zéro finding lors de la première passe; première erreur de téléchargement corrigée par accès au seul registre. Passe finale après garde lecture également verte; absence de finding ≠ preuve de sécurité exhaustive.
- Relecture indépendante finale R0/R1/R2 : aucun défaut important confirmé; message de lecture préexistant corrigé et relu. La revue ne remplace pas les tests ni la qualification de l’image.
- Ruff global `backend scripts` vert; mypy application vert sur 622 sources; types/lint/build web verts, diff sans whitespace.
- Retour Alembic à base confirmé (tableversion vide), puis seul le conteneur PostgreSQL jetable créé pour la preuve a été supprimé. Aucun service existant modifié ou arrêté. Image locale conservée, aucun commit/push.

## Limites et invariants

Tests synthétiques locaux uniquement; aucun modèle réel, corpus envoyé, backend live, VPS, déploiement, effet P3, dépôt externe ni validation humaine inventée. Droits/MFA/FINANCIAL_PRIVATE, tenant, append-only, provenance, UNKNOWN et retries restent dans leurs contrats existants. Ces corrections ne qualifient pas une analyse entière, un Golden DCE, un benchmark concurrent ou un profil CPU optimal.

A1 non admis, A2 générique HOLD et NO-GO public maintenus.

## Fichiers et clôture

Code : `web/src/features/dce/useDceKnowledge.ts`, `backend/app/modules/knowledge/infrastructure/dce_source.py`, `vector_index.py`, `ops/docker/backend.Dockerfile`, `pyproject.toml`, `uv.lock`. Régressions : hook existant, `backend/tests/db/test_knowledge_source_freshness.py`, `backend/tests/ops/test_backend_dependency_selection.py`, adaptation des anciens contrôles ops. Aucun nouveau package/version, schéma, API, droit, source promue ou design visuel.

Reprise : R0/R1/R2 closes **dans ce checkout avec WIP**; ce code n’est pas encore commité. Le plan global fixe R3 : couverture documentaire réellement consultable par lot/version et pièces critiques non lues visibles. Ne pas recommencer les défauts clos et ne pas déclarer les moteurs métier qualifiés par leurs imports.

## Méthodes appliquées

Superpowers : diagnostic systématique, TDD, revue indépendante et vérification avant clôture. ECC : module-regression pour les consommateurs et commandes de régression. Graphify consulté avant navigation, fichiers actuels ensuite vérifiés; Basic Memory synchronisé comme miroir. Les commandes uv installées et leurs résultats ont été vérifiés directement. Pas de Jev/Manus nécessaire pour ces correctifs bornés; aucune nouvelle navigation Serena après la lecture ciblée des fichiers connus. OpenDesign/Impeccable et navigateur non déclenchés : logique interne du hook et des adaptateurs, aucune conception/édition visuelle; les tests React sont jsdom et ne valent pas une recette Chromium.
