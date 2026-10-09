# EXP-05 — qualification navigateur du formulaire Collaborateur

**Date :** 8 octobre 2026
**Résultat :** QUALIFIÉ LOCAL SUR FIXTURES SYNTHÉTIQUES; aucune qualification live ou ouverture publique.
**Périmètre :** App existante, authentification synthétique, sélection de source DCE et intentions POST/rejeu/conflit.

## AS-IS observé

- Le Vite lancé pour cette recette répondait sur `127.0.0.1:4173`. L’API in-memory synthétique a été servie sur `127.0.0.1:8765`, puis redémarrée entre les scénarios pour remettre son état à zéro. Après le test, Vite, l’API, Chromium et le profil temporaire ont été arrêtés/supprimés; les ports `4173`, `8765` et `9229` ne sont plus à l’écoute.
- Le compte résout `actor_kind=COLLABORATEUR`; MFA est affichée validée et le contexte est confirmé. `operational_profile=null` n’a été appliqué qu’au mock pour éviter le libellé de sous-profil « Responsable ».
- Le mock a reçu trois corrections de fixture, sans code produit : GET P7 vide conforme (`case_id`/`items`) en 200; inventaire DCE avec `items: []`; première proposition qui enregistre l’effet synthétique puis répond HTTP 500 JSON. Le DCE seedé est courant/admis/vérifié, avec une exigence et une tâche synthétiques; leur état documentaire de source reste `UNKNOWN`.
- Chromium 141.0.7390.37 a tourné headless dans un profil temporaire isolé. Desktop 1440×900 : largeur document 1425 px, sans débordement horizontal. Mobile 390×844 : largeur document 390 px, sans débordement. Tab donne un focus visible (outline solid) sur le candidat; Space sélectionne l’exigence et ArrowDown sélectionne la tâche.

## Parcours et preuves

- Avant la coche de confirmation et après la coche mais avant le clic d’envoi : zéro POST. Une tentative non confirmée est refusée localement.
- Première intention sur tâche DCE : le mock enregistre l’effet synthétique puis répond `500`. L’App affiche `UNKNOWN`; le journal montre un seul POST, `first_attempts=1` et aucun GET d’évaluations supplémentaire (le seul GET reste la lecture initiale).
- Le clic explicite « Réessayer la même proposition » envoie la même structure et les mêmes `command_id`, `idempotency_key`, `correlation_id`, capacité, version, tâche et justification. Le reçu 200 est reconnu; un seul GET `capability-assessments` suit. Le corps ne contient ni `assignment_id` ni `source_locator`.
- Une nouvelle intention, avec source requirement DCE et nouveaux command/idempotency IDs, reçoit `409`; un seul GET `capability-assessments` suit. Le journal final du mock donne les statuts POST `[500, 200, 409]` et trois GET d’évaluations : lecture initiale, reçu et conflit.
- La preuve privée et les captures sont sous `/home/noor/.local/share/smartao-proofs/exp05-browser-20261008/` (`evidence.json` mode 0600, SHA-256 `e8525fdd0511db7cd1fbc833918c5c8488a2504c12db1ea2409f46cfaafea60f`; `unknown-1440x900.png`, `desktop-409.png`, `mobile-409.png`). Aucun cookie, jeton ou mot de passe n’a été lu ou conservé.
- `Runtime.exceptionThrown` : 0 pendant la recette finale. Aucun appel externe n’a été observé dans le trafic applicatif; le navigateur utilisait une résolution externe bloquée.

## Diagnostic du rejeu réseau initial

Une première simulation qui coupait la socket avant tout header a donné deux exécutions HTTP après un seul clic. Les compteurs de page montraient un seul événement submit, un seul clic et un seul appel `fetch`; le journal serveur enregistrait deux corps identiques, et Chromium recevait finalement le second 200. Le hook React ne réessaie qu’après l’action explicite du bouton Retry; le client API appelle `fetch` une fois et ne rejoue qu’après 401. Le rejeu s’est donc produit sous le niveau de l’appel Fetch (transport Chromium/local). Cette simulation n’a pas été retenue comme preuve `UNKNOWN`.

Le mock final répond `500` JSON après avoir enregistré l’effet synthétique : cela évite la reprise transparente du transport et permet de vérifier explicitement UNKNOWN, aucun GET, puis Retry idempotent. Ce choix caractérise le parcours UI et l’idempotence du fixture; il ne prouve pas le comportement d’un serveur de production réel en perte de réponse.

## Limites et risques restant ouverts

- Aucun backend live, base métier, corpus réel, dépôt, disponibilité ou effet P3 n’a été exercé. `proposal_saved` est un booléen du mock en mémoire, pas une preuve de persistance réelle.
- Les tailles responsive et le focus clavier ont été vérifiés; audit axe/lecteur d’écran, performance et couverture visuelle complète non exécutés.
- L’appel MCP `chrome-devtools-local` via stdio a réussi : initialize, `tools/list` (30 outils) et `list_pages` (1 page isolée). L’alias d’outil Codex exposé `mcp__chrome_devtools__list_pages` échoue encore, car il cherche `/opt/google/chrome/chrome`, absent. La qualification a utilisé CDP direct sur le Chromium isolé; un échange MCP local a vérifié l’attachement et `list_pages`.
- Le 404 de `/auth/logout` appartient au harness synthétique et a été consommé par son `finally`, selon la consigne; il n’est pas classé comme défaut produit.
- Aucun code applicatif, test, migration ou dépendance n’a été modifié. Suites globales, lint/build, Semgrep et ECC verification-loop non exécutés pour cette qualification de runtime/documentation. Basic Memory n’était pas callable; les documents actifs portent le résultat.

## Décision Owner et périmètre de clôture

Le 08/10/2026, l’Owner a approuvé la clôture de cette tranche de qualification locale. La décision porte uniquement sur le formulaire en navigateur local avec API synthétique décrit ici; elle ne qualifie ni backend live, ni corpus réel, ni disponibilité, ni effet P3, et ne lève pas le NO-GO public. A1 reste en attente et A2 générique en HOLD.

La suite post-clôture est consignée dans le plan actif. Après l’audit du POST et le transport web typé, le formulaire C08 a été intégré et testé localement; son rapport est [C08 — commande humaine de rapprochement des lignes](C08_RAPPROCHEMENT_LIGNES_UI_2026-10-08.md). La qualification navigateur réelle reste non exécutée faute de navigateur local disponible; la preview OpenDesign Locale est accessible depuis ce rapport. Aucun backend live, corpus réel, effet P3 ou GO public n’est qualifié.
