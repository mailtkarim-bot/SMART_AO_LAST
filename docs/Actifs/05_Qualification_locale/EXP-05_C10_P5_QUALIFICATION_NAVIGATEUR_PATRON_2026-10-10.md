# EXP-05 C10/P5 — qualification navigateur Patron locale — 10 octobre 2026

**Statut :** QUALIFIÉE EN LOCAL SYNTHÉTIQUE — cette preuve couvre l’interface et son contrat avec une API de simulation, pas le backend SMART_AO en exécution.

## Portée et environnement

Parcours Patron C10/P5 dans l’application locale, avec une session `PATRON_ADMIN`, un tenant synthétique, un step-up TOTP synthétique et un serveur API temporaire en mémoire. Chromium a utilisé le contexte isolé `smartao-patron-c10-p5-20261010`. Vite était sur `127.0.0.1:4173`, l’API synthétique sur `127.0.0.1:8765`; Chrome DevTools Local a piloté la page. Les 149 requêtes observées sont restées sur ces deux origines locales; zéro destination externe.

Aucun backend métier, corpus réel, VPS, déploiement, dépôt externe, action P3, push ou GO public. L’API synthétique simule volontairement l’effet append-only avant le premier `500`, le conflit de version, le step-up et l’archive. Elle ne prouve pas l’authentification, l’isolation tenant, les verrous PostgreSQL, l’origine C10 courante ni la génération ZIP du backend réel. L’autorité de ces propriétés reste dans les tests backend/PostgreSQL consignés en CT31-38 à CT31-41.

## Parcours observé

- Connexion synthétique, lecture du rôle Patron résolu, step-up TOTP puis confirmation explicite du contexte tenant. La page affiche les contrôles MFA avant l’accès métier.
- Saisie du candidat Submission synthétique et lecture du manifeste. Le manifeste expose schema 3, le tenant/plan C10, une entrée, les exclusions et le SHA-256 courant. Aucun POST P5 ne précède le clic « Autoriser la remise humaine ».
- Première autorisation P5 : le simulateur inscrit l’effet puis renvoie `500`; la page conserve l’état d’incertitude. Aucun GET manifeste ne suit cet état avant le retry explicite. Le retry a le même corps, `command_id`, `idempotency_key`, `authorization_id`, version et SHA; il reçoit `200`.
- Scénario de manifeste obsolète sur un second candidat : lecture v1, POST P5 `409`, puis un seul GET de manifeste. La page présente v2 et son nouveau SHA; le candidat demeure non autorisé jusqu’au clic humain suivant. L’autorisation P5 v2 reçoit `200` avec ce SHA courant.
- Export après P5 v2 : GET export `200`, `external_submission: NOT_PERFORMED`. Le ZIP local contient exactement `manifest.json` et `c10-synthetic-response.txt`.

## Vérification de l’archive téléchargée

Le navigateur a téléchargé `submission-submission-c10-conflict.zip` (artefact synthétique local conservé hors Git). `python3`/`zipfile` a pu ouvrir et tester l’archive sans erreur CRC. Résultats : 675 octets; SHA-256 de l’archive `14c5cefb598dc935d21986e68d4e8e388c66f9f9ced84988f4dd52b837c60bad`; deux entrées exactes; SHA du manifeste v2 `fd3d7f1119f57e6ccbc1b98461669f37f24bc13ac5084d982897e2511b4f5702`; SHA du document `faf79d0bcbaa34a2b8cc64dcd702f26a3d108c9c6ed189b7e25dac7212a52cb7`, égal à celui de l’entrée du manifeste. Le manifeste n’expose ni contenu `FINANCIAL_PRIVATE`, ni clé de stockage, ni identifiant externe.

La première archive générée par le harnais avait des drapeaux de compression ZIP incorrects et a échoué au contrôle CRC. Le harnais local a été corrigé; le parcours a ensuite été rejoué et l’archive ci-dessus passe le contrôle ZIP et les comparaisons SHA. Ce défaut ne concernait pas le code produit.

## Résultats et limites

- P5 synthétique `UNKNOWN → retry identique → 200`; second candidat `409 → GET manifeste courant → v2 P5 200`; export `200` après P5 exact.
- Zéro exception JavaScript observée. Les réponses HTTP `500` et `409` sont les scénarios attendus; le `404` observé concerne la fiche entreprise absente de la fixture synthétique.
- La suite n’est ni Playwright ni un E2E backend : aucun Playwright MCP n’est installé dans cette session. La capture DevTools qualifie l’interface React et les réponses du simulateur uniquement. Aucune passe axe/accessibilité, lecteur d’écran, layout trois tailles, performance, persistance ou origine C10 réelle n’a été exécutée ici.
- Les fichiers applicatifs et tests du dépôt n’ont pas été modifiés. Le travail produit local reste non commité et non poussé; NO-GO public maintenu.

**Revue Owner — 11 octobre 2026.** L’Owner valide la clôture de cette qualification locale synthétique. Cette décision ne qualifie pas le backend métier/live, l’origine C10 réelle, l’exploitation de l’ancien binaire, un dépôt externe ou le GO public.

**Outils/méthode :** ECC `browser-qa`, Chrome DevTools Local, `python3`/`zipfile`, vérification avant clôture Superpowers. Le contexte Chromium était isolé; la clôture Owner porte uniquement sur la preuve locale décrite ici.
