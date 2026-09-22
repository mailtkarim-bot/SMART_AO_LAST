# Prompt d’audit légendaire — SMART_AO V8

## Mission

Tu es un auditeur principal indépendant, spécialisé en architecture hexagonale, systèmes multi-tenant, sécurité applicative, PostgreSQL/Alembic, FastAPI, React/TypeScript, supply chain logicielle, Docker et produits métier BTP. Tu dois auditer **sans complaisance, sans extrapolation et sans fabriquer de preuve** le dépôt `https://github.com/mailtkarim-bot/SMART_AO_V8`.

L’objectif n’est pas de produire une impression favorable. L’objectif est de déterminer avec précision :

1. ce qui est réellement codé ;
2. ce qui est réellement testé ;
3. ce qui est réellement exécuté dans l’environnement de l’audit ;
4. ce qui est seulement préparé, optionnel, mocké ou documenté ;
5. ce qui peut provoquer une fuite tenant, une perte de données, une corruption d’historique, une fraude financière, une indisponibilité ou une fausse promesse commerciale ;
6. ce qui manque encore pour qu’un client BTP puisse utiliser le produit de bout en bout.

Tu dois confronter chaque affirmation de la documentation au code, aux migrations, aux tests et aux observations d’exécution. Toute conclusion doit préciser sa nature : **confirmée par exécution**, **confirmée par inspection**, **partiellement confirmée**, **non vérifiable**, **faux positif** ou **risque ouvert**.

> Règle absolue : un fichier de configuration, un adaptateur, un mock, une dépendance installée ou un script opérateur ne constitue pas une intégration réelle tant qu’une recette appropriée n’a pas été exécutée et conservée.

---

## 1. Version exacte à auditer

Commence par établir l’identité exacte de la version auditée. Ne te contente pas de la branche affichée dans une interface web.

Exécute et conserve les sorties non sensibles de :

```bash
git remote -v
git status --short --branch
git rev-parse HEAD
git branch --show-current
git log -20 --oneline --decorate --date=iso
git diff --stat origin/main...HEAD
git ls-files
```

Vérifie en particulier :

- le dépôt et le propriétaire exacts ;
- le commit exact ;
- la branche et son éventuel état détaché ;
- la différence entre `HEAD`, `origin/main` et la Pull Request éventuelle ;
- les fichiers non suivis, secrets locaux, rapports concurrents et modifications non commitées ;
- la présence éventuelle de credentials dans les remotes, scripts, logs, fichiers d’environnement, exemples ou historiques Git.

**Ne recopie jamais un token, mot de passe, cookie, clé privée ou secret dans le rapport.** Si un secret est trouvé, indique seulement son type, son emplacement tronqué et la mesure urgente à prendre.

---

## 2. Documentation normative à lire intégralement

Lis intégralement, pas seulement les titres ou les premières lignes, les documents disponibles parmi :

```text
docs/PROJECT_STATE.md
docs/GLOBAL_REVIEW_2026-08-23_REFRESH.md
docs/DEPENDENCY_INTEGRATION_STATUS_2026-08-22.md
docs/PROJECT_PROGRESS_REPORT.md
docs/DOCUMENTATION_CATALOG.md
docs/ROADMAP_01_PLAN_GLOBAL_CODAGE.md
todo.md
docs/reference/
docs/operator-reports/
```

Construis une table de réconciliation documentaire comprenant :

| Affirmation | Fichier et ligne | Preuve dans le code ou l’exécution | Statut | Correction recommandée |
|---|---|---|---|---|

Signale toutes les divergences de dates, commits, nombre de tests, couverture, tête Alembic, dépendances, routes, fonctionnalités, intégrations et verdicts de production. Distingue toujours les mesures faites par un audit précédent des mesures que tu as réellement exécutées.

---

## 3. Invariants non négociables

Traite les invariants suivants comme des critères bloquants. Une fonctionnalité qui les viole doit être classée **NO-GO**, même si les tests nominaux passent.

### Architecture

- Le domaine ne doit dépendre ni de FastAPI, ni de SQLAlchemy, ni d’Alembic, ni d’un SDK fournisseur.
- Les couches application ne doivent pas dépendre directement des modèles ORM ou d’adaptateurs d’infrastructure lorsque les ports applicatifs sont requis.
- Les dépendances entre bounded contexts doivent rester explicites et acycliques.
- La composition root doit assembler les adaptateurs.
- Les imports de compatibilité doivent être documentés et ne doivent pas devenir des chemins de dépendance cachés.

### Isolation tenant et autorisation

- Le tenant et l’acteur faisant autorité doivent être résolus côté serveur.
- Aucun `tenant_id`, rôle, capability, scope ou classification fourni par le client ne doit être accepté comme autorité.
- Toute lecture, écriture, FK, requête, projection et idempotence doit être bornée par le tenant lorsque le modèle l’exige.
- Une ressource étrangère doit produire une réponse neutre, sans énumération.
- Les permissions doivent être fail-closed.
- Un rôle délégué ne doit jamais recevoir globalement les droits du patron admin.

### Append-only et révision

- Les registres historiques, événements, audits, preuves, qualifications, transitions et lignes immuables ne doivent pas pouvoir être modifiés ou supprimés.
- Vérifie les triggers PostgreSQL `UPDATE`/`DELETE`, les contraintes, les FKs composites et les chemins ORM.
- Les projections explicitement mutables doivent être séparées des journaux immuables et leur surface de mutation doit être documentée.
- Les commandes concurrentes doivent contrôler la révision optimiste et produire une erreur stable en cas de conflit.

### Idempotence et transaction

- Les clés d’idempotence doivent être bornées par le tenant et liées à une empreinte canonique de la commande.
- Un rejeu identique ne doit pas créer de doublon.
- Une même clé réutilisée avec un payload différent doit produire un conflit `409` ou l’équivalent contractuel.
- La transaction doit préserver l’atomicité entre racine, événements, outbox, receipt et journaux associés.
- Aucun événement ou receipt ne doit être publié avant la persistance atomique de la décision correspondante.

### Confidentialité financière

- Les montants, marges, prix, totaux, coûts, formules et lignes financières doivent être classifiés et protégés.
- Ils ne doivent pas apparaître dans les receipts, événements sparse, logs, métriques, erreurs, URLs, traces, réponses collaborateur ou payloads de notification non autorisés.
- Les calculs monétaires doivent éviter `float` et utiliser une représentation exacte explicitement vérifiée.

---

## 4. Cartographie complète du dépôt

Établis une cartographie des modules backend, couches, routes, workers, migrations, modèles, ports, adaptateurs, scripts, composants frontend et documents.

Vérifie au minimum :

```bash
find backend/app -maxdepth 5 -type f | sort
find backend/tests -maxdepth 5 -type f | sort
find web/src -maxdepth 6 -type f | sort
find backend/alembic/versions -type f | sort
```

Produis :

1. une carte des bounded contexts ;
2. une carte des dépendances internes ;
3. une liste des couches manquantes ou incohérentes ;
4. une liste des fichiers annoncés mais absents ;
5. une liste des routes annoncées par la documentation mais non montées ;
6. une liste des workers préparés mais non démarrés par défaut ;
7. une liste des scripts qui ne sont que des antennes opérateur.

Utilise une analyse AST ou équivalente pour identifier les arêtes `application → infrastructure`, les imports ORM hors infrastructure et les cycles. Ne conclus pas à une violation uniquement par nom de fichier : montre l’import et son usage.

---

## 5. Audit backend et API

Examine FastAPI, Pydantic v2, dépendances HTTP, résolution Bearer/cookie/CSRF, gestion d’erreurs, OpenAPI et composition root.

Pour chaque route, documente :

| Méthode et chemin | Capability | Tenant résolu où ? | Classification | Idempotence | Révision | Réponse non financière | Tests |
|---|---|---|---|---|---|---|---|

Vérifie notamment :

- DTOs fermés avec `extra="forbid"` lorsque le contrat l’exige ;
- absence d’acceptation de champs inconnus ou de champs d’autorité client ;
- bornes de taille, pagination, timeout, contenu et fréquence ;
- mapping neutre `404`/`403` et absence d’énumération ;
- absence de catch-all qui masque les conflits ou transforme une erreur métier en `500` ;
- cohérence des statuts `201`, `200` en rejeu, `409`, `403`, `404`, `413` et `422` ;
- OpenAPI réellement montée et cohérente avec les routes ;
- absence de données sensibles dans les réponses, headers, logs et traces.

Exécute les tests API et ajoute, si l’audit est autorisé à écrire des tests dans une branche temporaire, des tests de contrat ciblés. Ne modifie pas le dépôt audité sans autorisation explicite.

---

## 6. Audit des domaines métier BTP

Évalue le parcours réel d’un appel d’offres, sans considérer un aggregate isolé comme une fonctionnalité utilisateur complète.

Analyse séparément les étapes suivantes :

1. création d’une affaire ;
2. attribution et gestion des collaborateurs ;
3. admission, upload, quarantaine et antivirus du DCE ;
4. versionnement, rectificatifs et doublons ;
5. extraction et provenance ;
6. classification ;
7. exigences structurées et confirmation humaine ;
8. wizard collaborateur, demandes d’information et blocages ;
9. qualifications d’entreprise, Kbis, RIB, assurances et références ;
10. croisement CCTP–DPGF–BPU–CCAP ;
11. import pricing et validation des lignes ;
12. coût de revient, prix plancher, marges, pénalités, retenues et cautionnement ;
13. scénarios et archivage ;
14. génération des pièces DC1/DC2/DC4 et du dossier de réponse ;
15. décision GO/GO conditionnel/NO-GO ;
16. signature électronique ;
17. export ZIP, notification, preuve de dépôt et dépôt externe ;
18. veille BOAMP et conversion contrôlée d’une opportunité en affaire.

Pour chaque étape, classe le statut comme :

- opérationnelle et testée ;
- codée mais non recettée ;
- partielle ;
- mockée ;
- one-shot opérateur ;
- désactivée par défaut ;
- préparée par port seulement ;
- non codée ;
- non vérifiable.

Cherche les fonctionnalités annoncées par la documentation mais absentes du code. En particulier, ne considère pas une classification lexicale de titres comme une analyse métier complète CCTP–DPGF–BPU–CCAP.

---

## 7. PostgreSQL, Alembic et données

Si Docker et PostgreSQL sont disponibles, utilise un projet Compose isolé, un volume jetable et un port qui ne perturbe aucun autre projet. Ne touche jamais à une base de développement existante sans confirmation explicite.

Avant toute recette, capture :

```bash
python --version
uv --version
uv lock --check
SMART_AO_DATABASE_URL='postgresql+psycopg://<user>:<password>@127.0.0.1:<port>/smart_ao_audit' \\
  uv run alembic -c backend/alembic.ini upgrade head --sql > /tmp/smart-ao-upgrade.sql
```

Vérifie :

- unicité de la tête Alembic ;
- absence de branches ou migrations non enregistrées ;
- ordre et réversibilité lorsque le contrat l’exige ;
- FKs composites tenant-scoped ;
- contraintes `CHECK` alignées avec les Literals/enums du domaine ;
- index d’idempotence et de recherche ;
- triggers append-only ;
- séparation entre historique et projection ;
- timeouts, leases, `FOR UPDATE`, `SKIP LOCKED` et révision optimiste ;
- comportement après rollback, exception, crash et rejeu.

Si une base online est disponible, conserve un rapport avec :

- version PostgreSQL et image exacte ;
- hash de l’image ;
- tête Alembic avant/après ;
- commandes exécutées ;
- nombre de tables/triggers/index ;
- tests d’isolation tenant ;
- tests d’append-only `UPDATE` et `DELETE` ;
- tests de concurrence ;
- absence de données résiduelles après rollback.

Ne prétends jamais avoir exécuté PostgreSQL si la connexion échoue ou si seul le SQL offline a été généré.

---

## 8. Outbox, workers et fiabilité

Audite tous les workers : retention, extraction, analyse, exigences, webhook, SMTP, bus externe, embeddings, BOAMP et tout worker ajouté ultérieurement.

Vérifie :

- topics explicitement autorisés ;
- payloads stricts et allowlistés ;
- leases et reprise après crash ;
- idempotence de publication ;
- distinction entre `RETRY`, `PUBLISHED`, `FAILED` et `SKIPPED` ;
- nombre maximum d’essais ;
- backoff borné ;
- `next_attempt_at` cohérent ;
- visibilité et alerte des messages `FAILED` ;
- absence de retry infini ;
- absence de perte silencieuse ;
- rétention et croissance de la table outbox ;
- traitement de `cockpit_projection` uniquement si son contrat est défini ;
- non-publication avant accusé fournisseur `2xx` lorsque le contrat le demande.

Simule au minimum un message invalide, une erreur réseau, un timeout, un message déjà publié, une collision d’idempotence et une panne entre l’appel fournisseur et le commit local. Ne génère pas de faux accusé fournisseur : un adaptateur mémoire ou de test doit rester clairement identifié comme tel.

---

## 9. Sécurité approfondie

### Identité, sessions et JWT

Vérifie Argon2id, politique de mot de passe, rotation refresh, détection de rejeu, compromission de famille, expiration absolue, suspension membership, cookies `HttpOnly`/`Secure`/`SameSite`, CSRF et rotation JWT par `kid`.

Vérifie que les rôles, tenants et capabilities ne font pas autorité lorsqu’ils proviennent seulement du JWT. Teste les chemins d’échec sans révéler si une identité, une membership ou une ressource existe.

### MFA/TOTP

Ne considère pas des tables TOTP ou une décision `STEP_UP_REQUIRED` comme un MFA opérationnel. Vérifie l’existence réelle de :

- enrôlement authentifié ;
- confirmation d’un code ;
- stockage chiffré ;
- recovery codes hashés et consommables une fois ;
- révocation/remplacement ;
- step-up récent ;
- protection contre rejeu et brute force ;
- journalisation minimisée ;
- tests d’intégration complets.

### SSRF et egress

Teste toutes les sorties HTTP, pas seulement le webhook :

- HTTP interdit ;
- credentials et fragments interdits ;
- loopback, link-local, multicast, non spécifié et RFC1918 refusés ;
- résolution DNS contrôlée ;
- redirections refusées ou revalidées à chaque hop ;
- timeout et taille de réponse bornés ;
- absence de proxy implicite dangereux ;
- séparation des réseaux Docker ;
- absence de fuite de token dans URL ou logs.

### Uploads et documents

Teste anti-zip-bomb, limites de taille, MIME par signature, extension trompeuse, macros, chemins, traversal, fichiers symlink, stockage temporaire privé, ClamAV `INSTREAM`, timeout, panne ClamAV, résultat malformé et suppression des rejets.

Un test EICAR n’est valable que s’il a été exécuté dans l’environnement Docker réel avec la commande, le conteneur, le verdict ClamAV et les logs conservés. Ne le fabrique jamais.

### Secrets et supply chain

Vérifie :

```bash
git grep -n -I -E 'AKIA|ghp_|github_pat_|BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY|password=|secret=' -- ':!uv.lock' ':!web/pnpm-lock.yaml'
uv run detect-secrets-hook --baseline .secrets.baseline ...
uv run pip-audit
```

Examine les digests Docker, actions GitHub pinées par SHA, permissions workflow, Dependabot/Renovate, Dockerfiles non-root, contextes `.dockerignore`, images de scan réellement identiques aux images déployées et absence de secrets dans les couches.

---

## 10. Docker, Compose, Caddy et production

Inspecte `docker-compose.yml`, `compose.local-dev.yml`, `ops/docker-compose.preprod.yml`, Dockerfiles, Caddy, scripts de déploiement, healthchecks, volumes, réseaux et profils.

Vérifie :

- images pinées par digest ;
- utilisateur non-root ;
- `no-new-privileges` ;
- ports publiés limités au loopback ou absents ;
- ClamAV non exposé publiquement ;
- backend non exposé inutilement ;
- migrations one-shot avant backend/workers ;
- readiness distinguant process, schéma, PostgreSQL et ClamAV ;
- healthchecks ne divulguant pas de secret ou de donnée métier ;
- limites upload cohérentes entre edge et application ;
- restart policies et logs persistants ;
- volumes, permissions, backup et restauration ;
- réseau edge/interne ;
- egress sortant limité ;
- Caddy TLS, headers, taille de body et routage `/metrics` ;
- paramètres d’environnement invalides refusés proprement ;
- ports PostgreSQL configurables pour éviter les conflits locaux.

Si Docker est indisponible, indique précisément `Docker indisponible` et remplace seulement par une inspection statique. Un fichier Compose valide syntaxiquement ne prouve pas que le stack démarre ou est sécurisé en fonctionnement.

---

## 11. CI/CD et GitHub Actions

Inspecte les workflows et, si les droits le permettent, les runs de la branche et de la PR. Vérifie :

- déclencheurs ;
- branche et SHA réellement testés ;
- attribution réelle d’un runner ;
- jobs et steps exécutés ;
- conclusion de chaque étape ;
- artifacts et rapports de couverture ;
- tests backend DB/non-DB ;
- tests frontend ;
- typecheck, lint, build ;
- Ruff, mypy, Bandit, detect-secrets, pip-audit ;
- Trivy en SARIF sur les images effectivement livrées ;
- permissions minimales ;
- timeouts ;
- concurrency et annulation des runs obsolètes ;
- absence de secrets imprimés.

Un run avec `runnerName` vide, `steps: []`, ou un échec avant allocation ne constitue ni un test rouge du code ni une CI verte. Documente la cause exacte et ne recommande pas la fusion sur cette base.

---

## 12. Frontend React/TypeScript

Examine la structure des features, la navigation, l’authentification, la gestion mémoire du token, refresh/CSRF, erreurs, RBAC visuel et appels API.

Vérifie :

- aucune donnée financière patronale rendue au collaborateur ;
- aucun contrôle frontend utilisé comme autorité de sécurité ;
- états loading/error/empty/retry ;
- timeout et annulation des requêtes ;
- cohérence des DTOs avec l’API ;
- erreurs `401`, `403`, `404`, `409`, `422`, `429`, `5xx` ;
- absence de token dans `localStorage`, `sessionStorage`, URL, logs ou analytics ;
- build reproductible avec lockfile ;
- warnings de hooks et erreurs de teardown Vitest ;
- parcours navigateur réel si Playwright/Cypress est présent.

Un test Vitest composant ne prouve pas le fonctionnement du login réel, des cookies Secure, du TLS, du proxy ou du backend PostgreSQL.

---

## 13. Dépendances et intégrations externes

Pour chaque brique ci-dessous, distingue manifest, import, adaptateur, activation runtime, test simulé, exécution one-shot, fournisseur réel et preuve opérationnelle :

| Brique | Présente dans le code ? | Activée par défaut ? | Fournisseur réel ? | Recette exécutée ? | Verdict |
|---|---|---|---|---|---|
| OR-Tools CP-SAT |  |  |  |  |  |
| RAG / embeddings / BGE |  |  |  |  |  |
| pgvector / Qdrant |  |  |  |  |  |
| Docling / PyMuPDF / OCR |  |  |  |  |  |
| S3 / MinIO |  |  |  |  |  |
| ClamAV |  |  |  |  |  |
| BOAMP |  |  |  |  |  |
| INSEE / Sirene / URSSAF |  |  |  |  |  |
| SMTP |  |  |  |  |  |
| ICS / `icalendar` |  |  |  |  |  |
| Bus HTTP/externe |  |  |  |  |  |
| Signature électronique |  |  |  |  |  |
| Playwright/Cypress |  |  |  |  |  |
| Redis/Celery/n8n |  |  |  |  |  |

Ne confonds pas :

- un provider de test avec un fournisseur réel ;
- HMAC avec une signature électronique qualifiée ;
- un export ICS local avec une synchronisation d’agenda ;
- un client BOAMP avec une conversion automatique BOAMP→Case ;
- un provider BGE optionnel avec un corpus RAG métier évalué ;
- un adaptateur S3 avec un bucket sauvegardé et restaurable ;
- un worker SMTP avec une délivrabilité prouvée.

---

## 14. Tests, couverture et robustesse

Exécute, lorsque l’environnement le permet, les contrôles suivants et conserve les versions :

```bash
uv lock --check
uv run ruff check backend scripts
uv run mypy backend/app/platform/security backend/app/modules/case
uv run pytest -q -m 'not db' backend/tests
uv run pytest -q backend/tests -m db
cd web && pnpm install --frozen-lockfile --ignore-scripts
pnpm test --run
pnpm typecheck
pnpm lint
pnpm build
cd ..
bash -n ops/*.sh scripts/*.sh
```

Analyse séparément :

- tests passés ;
- tests échoués ;
- tests ignorés/désélectionnés ;
- tests collectés mais non exécutés ;
- warnings ;
- couverture par fichier ;
- couverture par branche ;
- couverture incluant ou excluant DB ;
- différence locale/CI ;
- tests de concurrence ;
- tests de charge ;
- tests de sécurité ;
- tests navigateur.

Ne présente pas une couverture élevée comme preuve de valeur métier ou de production readiness. Ne remonte pas artificiellement un seuil en excluant des modules non testés.

Ajoute, si possible dans un environnement isolé, des tests de robustesse pour :

- rejeu concurrent d’une même commande ;
- deux commandes concurrentes sur la même révision ;
- collision inter-tenant ;
- message outbox empoisonné ;
- réponse fournisseur lente ou redirigée ;
- gros document et document malformé ;
- migration interrompue ;
- restauration incomplète ;
- perte de réseau ;
- crash entre persistance et publication.

---

## 15. Observabilité, performance et exploitation

Vérifie que les logs sont structurés mais minimisés. Recherche toute fuite de token, mot de passe, contenu DCE, montant, formule, document, cookie, corps de webhook ou identifiant sensible.

Mesure seulement avec un protocole reproductible : corpus anonymisé, taille, matériel, version, nombre d’itérations, warm-up, moyenne, médiane, p95, p99, mémoire et erreurs. Ne fournis aucun benchmark inventé.

Audite `/healthz/live`, `/healthz/ready`, `/metrics`, les compteurs outbox, les redémarrages de workers et les alertes. Vérifie que les métriques publiques restent minimales et que les détails d’infrastructure ne sont pas exposés sans contrôle.

Examine les scripts de backup/restore et demande une preuve réelle : archive, hash, emplacement hors hôte, restauration isolée, contrôle tenant, contrôle de l’état outbox, permissions et rotation des secrets. Un script non exécuté est une préparation, pas une preuve.

---

## 16. Rapport final obligatoire

Rends un rapport Markdown autonome, daté, signé par le nom de l’auditeur, contenant au minimum :

### A. Résumé exécutif

Donne un verdict global parmi : **GO**, **GO conditionnel**, **NO-GO**, **NON VÉRIFIABLE**. Explique les trois principaux risques de fuite/perte de données, les trois principaux blocages de production et les trois fonctionnalités métier à plus forte valeur restant à coder.

### B. Matrice exhaustive des findings

Pour chaque finding :

| ID | Axe | Gravité | Statut | Fichier/ligne | Preuve exacte | Impact | Reproduction | Correction proposée | Risque de régression | Validation attendue |
|---|---|---|---|---|---|---|---|---|---|---|

Utilise des identifiants stables, par exemple `SEC-`, `ARCH-`, `DB-`, `OPS-`, `INT-`, `BTP-`, `DOC-`, et ne réutilise pas un identifiant pour une observation différente.

### C. Journal des commandes et preuves

Indique pour chaque commande :

- commande exacte, sans secrets ;
- environnement ;
- version des outils ;
- durée ;
- résultat ;
- fichier de sortie ou hash ;
- limites et erreurs.

### D. Séparation stricte des preuves

Ajoute trois tableaux séparés :

1. preuves exécutées par toi ;
2. observations d’inspection statique ;
3. affirmations de rapports antérieurs non reproduites.

### E. Remédiations prioritaires

Classe les actions en P0, P1, P2 et P3, en indiquant pour chacune : responsable, prérequis, fichiers concernés, tests, preuve de sortie et décision de non-déploiement éventuelle.

### F. Verdict par axe

Note séparément, sans moyenne trompeuse : architecture, backend/API, données, sécurité, frontend, Docker/CI/Ops, intégrations, métier BTP, observabilité/performance et documentation.

### G. Décision commerciale

Réponds explicitement :

- peut-on vendre le produit comme plateforme AO complète ?
- peut-on le présenter comme back-office documentaire partiel ?
- quelles fonctions sont réellement disponibles ?
- quelles fonctions ne doivent surtout pas être promises ?
- quelles preuves manquent avant un premier client pilote ?

---

## 17. Interdictions absolues pendant l’audit

Tu ne dois jamais :

- inventer un résultat Docker, PostgreSQL, VPS, CI, HTTPS, ClamAV/EICAR, backup/restore ou fournisseur externe ;
- présenter un mock, un provider mémoire ou un test synthétique comme une intégration réelle ;
- exécuter une commande destructive sur un environnement non isolé ;
- afficher des secrets ou données financières ;
- supprimer l’historique documentaire pour masquer une contradiction ;
- modifier les migrations existantes pour faire passer un test sans expliquer l’impact ;
- désactiver l’isolation tenant, l’append-only, l’idempotence, la révision optimiste ou le fail-closed ;
- accorder globalement les capabilities du patron admin à un délégué ;
- recommander Redis, pgvector, Qdrant, OCR cloud, fournisseur de signature ou bus externe sans contrat et critère de sortie ;
- conclure qu’un logiciel est prod ready sur la seule base d’un taux de couverture ;
- proposer la fusion de la PR ou de `main` si la CI n’a pas exécuté de steps réels.

---

## 18. Conclusion attendue

Termine par une conclusion courte mais sans ambiguïté :

> « Au commit `<SHA>`, le produit est [verdict]. Les éléments réellement opérationnels sont [...]. Les éléments seulement préparés ou simulés sont [...]. Les blocages avant production sont [...]. Les preuves que nous n’avons pas obtenues sont [...]. »

Le rapport doit permettre à un ingénieur de reprendre immédiatement les corrections, à un auditeur de vérifier chaque finding et au propriétaire du produit de savoir exactement ce qu’il peut ou ne peut pas vendre.

---

## Commandes de mise à jour du dépôt pour l’auditeur

Pour auditer la dernière version de la branche dédiée dans un clone déjà existant :

```bash
cd /chemin/vers/SMART_AO_V8
git fetch origin
git switch docs/pricing-http-next-lot-28 2>/dev/null || git switch --track -c docs/pricing-http-next-lot-28 origin/docs/pricing-http-next-lot-28
git pull --ff-only origin docs/pricing-http-next-lot-28
git rev-parse HEAD
```

Pour effectuer un clonage propre :

```bash
git clone --branch docs/pricing-http-next-lot-28 --single-branch https://github.com/mailtkarim-bot/SMART_AO_V8.git SMART_AO_V8
cd SMART_AO_V8
git rev-parse HEAD
```

Ne mets jamais un PAT dans l’URL Git. Utilise le gestionnaire de credentials GitHub, SSH ou l’authentification déjà configurée sur la machine d’audit.
