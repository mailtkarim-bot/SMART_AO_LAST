# RAPPORT D'AUDIT SYSTÈME INTÉGRÉ — SMART_AO V8

**Type d'audit** : Autopsie 360° — Génie Logiciel + Cybersécurité + DevOps + Valeur Métier BTP
**Date** : 23 août 2026
**Périmètre audité** : 599 fichiers sources (~94 300 lignes Python backend dont ~42 000 lignes de tests ; ~8 200 lignes TypeScript frontend), ops/, docs/, CI, Docker, migrations Alembic (55).
**Posture** : Zéro complaisance. Chaque constat est adossé à une preuve (`chemin:ligne`).

---

## 1. EXECUTIVE SUMMARY

### Bilan de santé global : **51 / 100** — « Forteresse bancaire devant un atelier vide »

| Axe | Note /100 | Appréciation sans filtre |
|---|---|---|
| 🔐 Sécurité & confidentialité (backend) | **88** | Niveau exceptionnel, rare même dans la fintech. Quatre barrières indépendantes protègent les données financières. |
| 🏗️ Ingénierie backend (archi/code) | **66** | Domaine pur réel et outbox authentique, mais modularité enfreinte en profondeur (~45 imports croisés), machine à états cosmétique, outbox à voie morte. |
| 🖥️ Frontend / UX | **42** | Fondations saines (token mémoire, CSRF, zéro XSS, zéro `any`) mais c'est un incrément de démo : pas de routeur, RBAC UI absent, session non gérée, workflow à UUIDs saisis à la main. |
| ⚙️ Opérations (CI/CD/tests/backup/obs) | **36** | État NO-GO auto-documenté : CI morte, couverture 67,46 % < seuil 85,50 %, backups sans copie hors-hôte, alerting muet. |
| 💼 Valeur métier BTP | **26** | Le moteur qui doit gagner des AO et protéger les marges est quasi vide : pénalités, retenues de garantie, prix plancher, sous-traitance, DC1–DC4 : tout est absent du code produit. |

### Résumé des risques critiques (points de rupture immédiats)

1. **Le produit ne résout pas encore le problème pour lequel il existe.** Un entrepreneur qui l'utilise demain devra quand même lire son CCAP à l'œil nu, chiffrer dans Excel et déposer à la main. La règle métier centrale (« détecter ce qui ruine une offre ») n'est implémentée nulle part : grep `pénalit|retenue de garantie|cautionn` sur `backend/app` → **0 occurrence**.
2. **La chaîne qualité est coupée.** Les runners GitHub Actions échouent avant toute étape (commit `bbf4fa9`, PR #49 bloquée) : aucun des gates (ruff, mypy, bandit, pip-audit, coverage, Trivy) ne bloque rien en pratique aujourd'hui.
3. **La dette de couverture explose le gate** : 67,46 % mesuré contre 85,50 % exigé (`pyproject.toml:97`). Pire module : `dce/application/handlers.py` à **9,34 %** — soit précisément le handler métier central de 1 847 lignes.
4. **L'outbox grossit sans fin** : le topic par défaut `cockpit_projection` (`platform/events/dispatcher.py:65`) n'a aucun consommateur et aucune purge n'existe — accumulation infinie garantie en production.
5. **UX disqualifiante** : saisie manuelle d'UUIDs, montants en centimes, pas de deep-links, expiration de session non gérée → inutilisable par un patron ou métreur BTP réel.

---

## 2. MATRICE DES RISQUES CRITIQUES

| ID | Gravité | Risque | Preuve | Impact si non traité |
|---|---|---|---|---|
| R-01 | 🔴 **CRITIQUE** | Moteur métier BTP vide : aucune lecture clause par clause du CCAP/CCTP/DPGF (pénalités, RG, avance, caution, résiliation). Catalogue complet = 10 regex génériques sur le RC. | `backend/app/modules/dce/application/analysis.py:83-149` ; grep mots-clés métier = 0 hit | L'utilisateur se fait piéger exactement comme sans le logiciel. Produit invendable. |
| R-02 | 🔴 **CRITIQUE** | Chiffrage à sens unique : import XLSX ventes uniquement (`category="SALES"` forcé), coûts initialisés à 0 jamais alimentés, **pas de prix plancher ni coefficient**. La marge affichée au patron est fictive. | `pricing/application/import_service.py:170` ; `membership/application/financial_report_draft.py:142-147` ; `pricing/domain/scenario.py:16-43` | Décision GO sur marge fantôme = ruine sur exécution. C'est LE risque mortel que le produit devait éliminer. |
| R-03 | 🔴 **CRITIQUE** | CI inopérante : les 3 jobs échouent avant exécution (`runnerName` absent, `steps: []`). Tous les gates sont théoriques. | `.github/workflows/ci.yml` ; commit `bbf4fa9` ; `todo.md:56` ; PR #49 UNSTABLE | Régression silencieuse garantie sur main. |
| R-04 | 🔴 **CRITIQUE** | Couverture 67,46 % < gate 85,50 %. Handlers métier critiques quasi nus (`handlers.py` 9,34 %, `preparation/service.py` 13,56 %, `authentication.py` 34 %). | `.coverage` racine (mesuré 23/08/2026) ; `docs/COVERAGE_UNDER_85_ANALYSIS.md` | Si la CI revient, elle bloque immédiatement ; d'ici là, code critique non régressé. |
| R-05 | 🟠 **MAJEUR** | Outbox : topic défaut `cockpit_projection` sans consommateur + zéro purge des messages publiés et des `domain_events`. Croissance non bornée. | `platform/events/dispatcher.py:65` ; consommateurs limités à `workers/{dce_retention,submission_export_*,opportunity_event_bus}.py` | Saturation DB en production, dégradation progressive irréversible sans intervention manuelle. |
| R-06 | 🟠 **MAJEUR** | Machine à états cosmétique : toute transition vers tout état acceptée (OPEN→COMPLETED direct légal), état courant recalculé au read, double source de vérité. | `patron_action/application/transition_service.py:143-148` ; `list_open:101` | Invariants métier contournables ; données d'état incohérentes sous charge. |
| R-07 | 🟠 **MAJEUR** | Modularité décorative : ~45 imports croisés d'internals inter-modules, dépendance inversée platform→module, shared kernel (`ApplicationCommand`) logé dans le module dce. | `dce/application/handlers.py:12` ; `platform/storage/object_storage.py:14` ; `dce/application/commands.py:16` | Coût de modification exponentiel ; refactoring futur de plus en plus cher. |
| R-08 | 🟠 **MAJEUR** | Auth hors DI FastAPI : helper `_resolve_context` copié-collé dans 8+ fichiers de routes. Toute nouvelle route oubliant l'appel est anonyme-accessible, sans filet. | `interfaces/http/routes/dce_versions.py:160` ; `consultations.py:153` ; `dce_staging.py:237` ; répertoires `dependencies/` et `middleware/` vides | Faille d'autorisation par omission — classe de bug OWASP A01 classique. |
| R-09 | 🟠 **MAJEUR** | Session frontend : `expires_in` ignoré, pas de refresh proactif, échec de refresh silencieux (`return null`) → utilisateur coincé en boucle 401 sans re-login. Uploads FormData exclus du retry. | `web/src/infrastructure/api.ts:58,103-151,143` ; `useAuthentication.ts:43-77` | Abandon utilisateur lors d'un import DPGF en fin de session — pire moment possible. |
| R-10 | 🟠 **MAJEUR** | Backups confinés à l'hôte (`/var/backups/smart-ao`), restauration réelle jamais implémentée (script = verify-only), alerting = simple `logger` local. Workers sans healthcheck. | `ops/backup-preprod.sh:8` ; `ops/restore-preprod.sh` ; `ops/systemd/smart-ao-health-alert.service` | Perte totale possible en cas de destruction du VPS ; panne silencieuse des workers. |
| R-11 | 🟡 **MOYEN** | Race d'idempotence : doublon concurrent de clé d'idempotence → `IntegrityError` mappé en erreur générique au lieu de replay. | `platform/events/dispatcher.py:196-199` | Erreurs 500 spurious sous concurrence, violation du contrat d'idempotence annoncé. |
| R-12 | 🟡 **MOYEN** | Rate limiter login mono-processus (dict mémoire). Scale-out silencieux = anti-brute-force désactivé. Clé JWT par défaut commise dans compose dev passe les garde-fous prod. | `platform/security/rate_limit.py:24-57` ; `docker-compose.yml:28` | Compromission possible lors du passage multi-réplicas ou mauvais usage du compose dev. |
| R-13 | 🟡 **MOYEN** | N+1 massifs : jusqu'à 4 requêtes/proposition + 1/preuve dans l'évaluation de préparation ; latest-transition re-queryé par ligne dans 4 lecteurs. | `preparation/application/service.py:350,356,363,375` ; `submission/application/service.py:444-482` ; `patron_action/service.py:121-130` | Latence cockpit dégradée dès quelques dizaines de propositions. |
| R-14 | 🟡 **MOYEN** | Pas d'OCR en service (`SMART_AO_ADVANCED_EXTRACTION_ENABLED=0`) : PDF scanné → `FAILED_SAFE`. Or la majorité des DCE municipaux sont scannés. | `dce/infrastructure/advanced_extraction_factory.py:28` ; `extraction.py:240-245` | Le pipeline d'analyse est aveugle sur une grande partie du marché cible. |
| R-15 | 🟡 **MOYEN** | Import xlsx pricing sans antivirus ni MIME-sniffing (contrairement aux flux DCE/enterprise) ; validation sur Content-Type déclaré client. | `routes/patron_pricing_import.py:75-82` | Surface malware incohérente avec le reste du durcissement. |
| R-16 | 🟢 **MINEUR** | Code mort : module entier `watch_profile_service.py`, table migrée jamais utilisée `ProcessInboxRecord`, adaptateur de test en production, `app/demonstrations/m1.py` dans le package prod. | `opportunity/application/watch_profile_service.py:59` ; `platform/persistence/models.py:170` ; `submission/infrastructure/fake_signature_provider.py:26` | Confusion maintenance, surface d'attaque et de compréhension gonflée. |

---

## 3. AUTOPSIE TECHNIQUE (Code & Architecture)

### 3.1 Ce qui est réellement excellent (à préserver absolument)

Ces acquis constituent la valeur nette du projet et toute remédiation doit les respecter :

- **Domaine pur prouvé par tests AST** (`tests/architecture/test_*_domain_purity.py`) : zéro import SQLAlchemy/LLM/HTTP dans `modules/*/domain/`.
- **Confidentialité financière à 4 barrières indépendantes**, testées :
  1. Catalogue fermé `_COLLABORATOR_CAPABILITIES` sans aucune capability financière (`platform/security/capabilities.py:104-125`) ;
  2. Policy ABAC refusant toute donnée `FINANCIAL_PRIVATE` hors `PATRON_ADMIN` (`authorization.py:109-113`), y compris anti-forgery testé ;
  3. Double contrôle service (`pricing/application/service.py:60-61`, etc.) ;
  4. FK composites tenant-scoped en base (`pricing/infrastructure/models/financial.py:23-74`).
- **AuthN durcie** : Argon2id uniquement avec paramètres minimaux forcés et contrainte CHECK en base (`models.py:60`), anti-énumération timing-safe, JWT HS256 allowlist + `kid` obligatoire + clé ≥ 32 chars, **aucun claim de rôle dans le token** (autorisation toujours re-résolue serveur), refresh opaques hashés SHA-256 avec rotation à détection de replay compromettant la lignée (`authentication.py:445-447`).
- **Upload fail-closed** : MIME par libmagic sur octets, allowlist fermée, ClamAV INSTREAM où toute erreur = rejet, streaming avec coupure taille, path traversal doublement protégé, zéro URL pré-signée exposée.
- **Zéro injection SQL** : balayage exhaustif négatif ; tout passe par l'expression language SQLAlchemy typée.
- **Zéro fuite LLM** : aucun appel LLM externe ; embeddings locaux `bge-m3` `local_files_only` ; exclusion explicite de `FINANCIAL_PRIVATE` de l'index vectoriel (`vector_index.py:43-44`) ; webhook sortant anti-SSRF DNS + HMAC signé + payload sans montants.
- **Idempotence/outbox réels** : receipts avec hash canonique, leasing `skip_locked` + backoff exponentiel, index partiels soignés.
- **Frontend sécurité** : access token mémoire uniquement (testé : jamais dans localStorage), refresh cookie HttpOnly + CSRF double-submit, zéro `dangerouslySetInnerHTML`, runtimeConfig refusant API non-HTTPS depuis page HTTPS.
- **Ops contract tests** rares et précis (`tests/ops/test_preprod_ops_contract.py`) : digest-pinning vérifié par test.

### 3.2 Fautes majeures & anomalies critiques

#### A. Architecture : le « modular monolith » est décoratif hors du domaine

- **~45 imports croisés d'internals inter-modules** ; la couche `public/` est systématiquement contournée par les services applicatifs. Exemples : `dce/application/handlers.py:12` lit les tables ORM de `case` ; `submission/application/service.py:13,20-26` importe les modèles infra de 3 modules étrangers ; `membership/application/collab_capability.py:10-11`.
- **Dépendance inversée platform→module** : `app/platform/storage/object_storage.py:14` importe `preparation.infrastructure.document_storage`. La plateforme doit être une feuille du graphe, jamais une racine.
- **Shared kernel mal placé** : `ApplicationCommand` vit dans `dce/application/commands.py:16` et est importé par membership. Il appartient à `platform/`.
- **Les tests d'architecture ne voient rien de tout cela** : ils vérifient la pureté du domaine et le layout, mais aucune règle inter-modules (`test_post_slice_boundaries.py`).
- **God functions** : `create_app` = 442 lignes (`bootstrap/application.py:610`) ; `TransitionHandler.execute` = 255 lignes (`dce/application/handlers.py:638`) ; `_evaluate` = 242 lignes cc≈38 (`preparation/application/service.py:258`) ; router builders de 294/269 lignes. 45 fonctions ≥ 100 lignes.

#### B. Fiabilité transactionnelle

- **Race d'idempotence** (`dispatcher.py:196-199`) : `IntegrityError` en course → `CommandExecutionError("command persistence failed before commit")` au lieu d'une rejouabilité idempotente. Le `FOR UPDATE` sur receipt inexistant ne verrouille pas l'insertion concurrente.
- **Outbox voie morte** : topic défaut `cockpit_projection` sans worker consommateur ; aucune purge des messages `PUBLISHED` ni des `domain_events`.
- **Machine à états absente** : `transition_service.py:145-148` accepte n'importe quel `target_state` (seuls gardes : non fermé + ≠ courant). `PatronActionRecord.state` jamais écrit après transition — état recalculé au read (`list_open:101`). Deux conventions transactionnelles coexistent (helper revision optimiste pour case/dce/decision, ORM nu + `with_for_update` ailleurs).

#### C. Gestion d'erreurs aplatie

- **Aucun exception handler global** dans toute l'application (`add_exception_handler` introuvable).
- **221 `raise ValueError` applicatifs** tous aplatis en HTTP 422 `COMMAND_REJECTED` indistinct (`routes/dce_staging.py:105-109`) : NOT_FOUND, VERSION_CONFLICT et état invalide confondus. Le client ne peut rien discriminer.

#### D. Performance

- N+1 confirmés et chiffrés (cf. R-13) : le pire est O(P×(3+L)) dans `_evaluate` — 1 query capability (:350), 1 version (:356), 1 links (:363) par proposition, + 1 document par preuve (:375).
- Création dynamique de classe Python **par itération** dans une boucle (`patron_action/application/transition_service.py:105`) + ligne morte `projections.append(row.__class__)` immédiatement écrasée.
- Index globalement bien conçus (partiels, composites) — point positif.

#### E. Frontend : incrément de démonstration

- **Pas de routeur** : navigation par `scrollIntoView` (`App.tsx:263-266`), 9 sections montées simultanément, back-button mort, deep-linking impossible.
- **RBAC UI inexistant** : seul l'avatar change selon le rôle (`App.tsx:325`) ; un COLLABORATEUR voit le shell « ESPACE PATRON », le brouillon financier et les scénarios ; les appels `/patron/*` partent inconditionnellement (`App.tsx:189-196`). Aveu dans `web/README.md:5`. Le mur serveur tient (heureusement), mais l'UI transformera les 403 en bruit d'erreurs plutôt qu'en masquage.
- **App.tsx composant-dieu de 514 lignes**, ~30 états, prop drilling jusqu'à 25 props sur un panel ; bus de message unique last-error-wins partagé par 8 hooks (`App.tsx:77,335`) ; duplication `type Message` ×8.
- **Aucune ErrorBoundary** (`main.tsx:5-8`) : toute exception de rendu = page blanche sur les 9 sections.
- **Workflow à UUIDs saisis à la main** (reportId, batchId, packageId, snapshotId…) (`FinancialDraftPanel.tsx:70-77`, `CollaboratorWizardPanel.tsx:68-87`) : agrégats non chaînés entre panels.
- Montants saisis **en centimes entiers** (placeholder « 125000 ») — un métreur tape des euros.
- Tooling : aucun ESLint/Prettier, pas de script lint/typecheck autonome, `@testing-library/dom` (peer obligatoire RTL v16) non déclaré dans package.json.
- Point fort à créditer : zéro `any`, zéro `@ts-ignore`, strict TS compilant propre ; 89 tests vitest verts (vérifié en exécution).

### 3.3 Incohérences structurelles & flous opérationnels

- **Taxonomie pytest fictive** : marqueurs `schema`/`application` déclarés à 0 test, `domain` à 2, `concurrency` à 3, `e2e` à 2 ; **827 tests sur 1325 sans marqueur** (`pyproject.toml:70-82` vs réalité de collection).
- **mypy borné à 4 fichiers** de sécurité dans la CI (`ci.yml:36-40`) : 300+ fichiers jamais typés-vérifiés.
- **Image backend non reproductible** : `pip install .` sur plages de `pyproject.toml` au lieu de `uv.lock` (`ops/docker/backend.Dockerfile:25`) — divergence entre ce que pip-audit audite et ce que l'image installe réellement.
- **Frontend Dockerfile sans `USER`** au stade final : nginx master en root ; workers preprod sans healthcheck.
- **README frontend contredit le code** (token « stockage local » prétendu vs implémentation mémoire imposée par les tests ; proxy Vite prétendu vs URL absolue par défaut).
- **Divergence limites upload** : app 2 GB (`upload.py:78`) vs Caddy 150 MB (`Caddyfile:13-15`).
- `app/demonstrations/m1.py` (438 lignes) dans le package de production ; répertoires `interfaces/http/dependencies/` et `middleware/` vides (squelettes jamais remplis).

### 3.4 Dettes techniques conceptuelles

- Deux conventions de concurrence optimiste coexistantes (helper blindé vs ORM nu) — il faudra unifier un jour, chaque nouveau module choisit aujourd'hui au hasard.
- Tests e2e quasi absents côté backend (0,15 %) **et aucun** test frontal↔API réel ; mocks fetch artisanaux dupliqués au lieu de MSW.
- Concurrence jamais disputée réellement : 2 tests séquentiels, aucune tempête de retry, outbox jamais contesté en parallèle.
- Corpus `fixtures/` vide : le produit n'a **jamais** traité un seul AO de bout en bout.
- Alerting et restauration réelle restent des stubs documentés (`todo.md:26-28`) : le runbook VPS n'a jamais été exécuté sur un hôte réel.

---

## 4. VERDICT MÉTIER (Le regard du Patron BTP)

> *« On m'a vendu un coffre-fort blindé avec alarme et caméras. À l'intérieur, il n'y a ni mètre, ni devis, ni lecture du CCAP. Mes risques de chantier restent sur papier et dans ma tête. »*

### Tableau de couverture des 10 capacités vitales

| Capacité | Statut | Preuve principale |
|---|---|---|
| Détection pièges DCE (pénalités ‰/j plafonnées, retenue de garantie 5 %, avance, cautionnement, résiliation) | ❌ ABSENT | `dce/application/analysis.py:83-149` = 10 regex ; grep métier = 0 |
| Incohérences CCTP ↔ DPGF ↔ CCAP | ❌ ABSENT | Seul diff = exigences entre versions successives, « aucune correspondance sémantique » assumée (`impact.py:105-148`) |
| Chiffrage coût/marge/coefficient/prix plancher | ⚠️ PARTIEL (ventes seules) | `import_service.py:170` ; coûts à 0 (`financial_report_draft.py:142-147`) ; scénario = bps globaux (`scenario.py:16-43`) |
| Sous-traitance (plafond, DC4) & co-traitance (groupement, mandataire) | ❌ ABSENT | Grep = 0 hit produit |
| Risques techniques (amiante, décennale, BT01/indexation) | ❌ ABSENT | Grep = 0 ; bibliothèque entreprise = KBIS/RIB/assurance avec contrôle d'expiration seulement |
| Mémoire technique / variantes | ❌ ABSENT (workflow squelette) | Document généré = Markdown d'UUIDs et codes de section, sans texte libre (`document_content.py:25-58`, `review.py:434-441`) |
| Veille BOAMP | ⚠️ PARTIEL (réel mais manuel) | Adaptateur API Explore v2.1 authentique (`boamp.py:45-78`) ; scoring naïf ; ingestion one-shot, pas de polling, pas de conversion→Case |
| Décision GO/NO-GO patronale | ⚠️ PARTIEL (beau domaine, inopérant) | Aggregate DEC riche (`decision/domain/decision.py`) mais **aucune route d'écriture** — GET seul (`routes/patron_decisions.py:18`) ; probabilité de gain : 0 occurrence |
| Dépôt offre (DC1/DC2/AE, signature, AR) | ⚠️ PARTIEL | Paquet = ZIP de 2 fichiers (`service.py:118-134`) ; invariant permanent `NOT_PERFORMED` (:372) ; signature = intention + callback HMAC vers provider factice |
| SaaS multi-entreprises vendable | ⚠️ PARTIEL | Multi-tenant technique réel ; pas de self-signup, pas de facturation, CI morte, recette online jamais faite |

**Bilan : 0 couvert solidement, 4 partiels, 6 absents.**

### Est-ce un gadget ou une arme de guerre ?

**Aujourd'hui : un gadget d'ingénieur. Demain (potentiellement) : une arme — le socle est le bon.**

Trois vérités terrain :

1. **Ce logiciel ne protège pas encore la marge.** Le risque n°1 de l'entrepreneur — signer un AO mal calibré parce qu'il a raté une retenue de garantie, une pénalité plafonnée trop bas, un délai irréaliste ou un prix sous le coût de revient — est intégralement inchangé. La marge « validée » dans le module pricing est calculée sur des coûts à zéro : c'est pire que pas de logiciel, car cela crée une **illusion de contrôle**.
2. **Ce logiciel ne fait pas encore gagner de points à la note technique.** Ni mémoire technique assisté, ni variantes chiffrables, ni DC1–DC4. L'avantage concurrentiel promis n'existe pas encore.
3. **Mais les rails sont ceux qu'il faut.** Provenance sourcée par byte-offset, confirmation humaine obligatoire (`SOURCE_SIGNAL_ONLY`), append-only, traçabilité décisionnelle fingerprintée : quand les « machines-outils » métier seront branchées dessus (parseur CCAP, coût de revient, générateur DC1-DC4), elles seront dignes de confiance — ce qui est rare et précieux dans ce marché.

### Ce qui manque pour devenir indispensable (par ordre de valeur)

1. **Parseur de clauses CCAP/RC** : pénalités (taux/plafond), retenue de garantie, avance, cautionnement, délais, conditions de paiement, résiliation → fiches de risque signées patron.
2. **Coût de revient par ligne** : main-d'œuvre, fournitures, sous-traitance, FG, coefficients → prix plancher automatique et alerte anti-ruine sur scénario.
3. **Génération DC1/DC2/DC4 + acte d'engagement** depuis la bibliothèque entreprise (les données KBIS/RIB/assurance y sont déjà).
4. **Croisement CCTP ↔ DPGF ↔ CCAP** (au minimum : exigences CCTP sans ligne DPGF correspondante).
5. **OCR activable** pour les DCE scannés (dépendance `document-advanced` déjà déclarée mais jamais branchée en défaut).
6. **Sous-traitance/co-traitance** : entités, plafond légal, DC4, convention de groupement.
7. **Boucle décisionnelle fermée** : routes d'écriture DEC alimentées automatiquement par l'analyse DCE + le chiffrage + probabilité de gain estimée.

---

## 5. PLAN DE REMÉDIATION CHIRURGICAL

### Phase 0 — Débloquer la chaîne qualité (Semaine 1, prérequis à tout le reste)

1. **Rétablir les runners GitHub Actions** (self-hosted runner si les hosted restent HS). Critère de sortie : un run vert complet sur `main`.
2. **Décider honnêtement du gate de couverture** : soit remonter à 85,50 % par tests utiles ciblés sur les modules nus (`bootstrap/production.py` 0 %, `handlers.py` 9,34 %, `authentication.py` 34 %), soit abaisser temporairement à 70 % avec jalon daté de remontée. Ne jamais tricher par exclusions.
3. **Pin les GitHub Actions par SHA** dans `ci.yml` ; ajouter Trivy sur l'image frontend ; `USER` nginx dans `frontend.Dockerfile`.

### Phase 1 — Stabiliser le socle fiabilité/archi (Semaines 2-4)

4. **Outbox** : ajouter un consommateur pour `cockpit_projection` OU changer le topic défaut en topic explicitement consommé ; ajouter worker de purge rétentionnelle des `outbox_messages` `PUBLISHED` et des `domain_events` anciens (même politique que `dce_retention.py`).
   ```python
   # dispatcher.py — remplacer le défaut muet
   DEFAULT_TOPIC = "cockpit_projection"  # AVANT : aucun consommateur
   # APRÈS : lever si aucun consumer enregistré pour le topic à l'emission,
   # ou router vers un topic consommé + job de purge quotidien.
   ```
5. **Idempotence en course** : dans `dispatcher.py:196-199`, intercepter `IntegrityError` sur la contrainte d'idempotence et rejouer la lecture du receipt existant (comparaison du hash canonique) au lieu de lever `CommandExecutionError`.
6. **Machine à états réelle** : table de transitions autorisées en constantes de domaine + garde dans chaque `transition_service`, testée :
   ```python
   ALLOWED_TRANSITIONS: dict[PatronActionState, frozenset[PatronActionState]] = {
       PatronActionState.OPEN: frozenset({PatronActionState.IN_PROGRESS}),
       PatronActionState.IN_PROGRESS: frozenset({PatronActionState.COMPLETED, PatronActionState.OPEN}),
       PatronActionState.COMPLETED: frozenset(),
   }
   ```
7. **Erreurs typées** : introduire une hiérarchie `ApplicationError(code)` mappée individuellement en HTTP (404/409/422), remplacer progressivement les 221 `ValueError` ; ajouter un `add_exception_handler` global (500 structuré + request_id, jamais de stack trace au client).
8. **Auth en DI FastAPI** : créer `dependencies/auth.py` avec `require_actor`, `require_patron_admin`, brancher via `APIRouter(dependencies=[...])` ; supprimer les 8 copies de `_resolve_context` (fusionner les 3 doublons de routes en un module partagé public).
9. **Couper les imports croisés** : déplacer `ApplicationCommand` vers `platform/commands.py` ; inverser `object_storage.py` (port défini dans platform, adaptateur câblé dans bootstrap) ; ajouter un test d'architecture interdisant `from app.modules.X.infrastructure` hors de X (import-linter ou AST custom, sur le modèle existant des tests de pureté).
10. **N+1** : refactorer `_evaluate` et les 4 lecteurs « latest per row » avec jointures fenêtrées ou chargement batch (`selectinload` / une requête par collection). Objectif mesurable : ≤ 5 requêtes par évaluation quelle que soit P.

### Phase 2 — Remonter la valeur métier (Semaines 4-10, priorité ROI)

11. **Slice CCAP-RISK-01** : extraction des clauses de risque sur texte déjà extrait — pénalités (taux/jour, plafond %), retenue de garantie (%), avance forfaitaire, cautionnement, délai, paiement, résiliation. Sortie = exigences structurées `SOURCE_SIGNAL_ONLY` + fiche de risque patronale confirmable (réutilise exactement les rails existants `requirements.py`).
12. **Slice COST-BASIS-01** : import DPGF avec colonnes de coût optionnelles ; si absence, coût = estimation éditable par ligne ; calcul prix plancher = Σcoûts×(1+FG) ; garde-fou blocant tout scénario sous le plancher sans override patronal tracé. Alimenter `cost_totals` (actuellement figé à 0).
13. **Slice DOC-GEN-01** : génération DC1/DC2/DC4 (docx via python-docx, déjà en deps) depuis `enterprise` library + case.
14. **Activer OCR opt-in** avec docling/pymupdf (deps déjà présentes) sur flux d'extraction `EMPTY_EXTRACTED_TEXT`, quarantaine conservée.
15. **Fermer la boucle DEC** : routes POST création/finalisation dossier décisionnel, alimentation auto depuis analyse DCE + pricing, champ probabilité de gain patronale.

### Phase 3 — Frontend digne d'utilisateurs (Semaines 6-12, en parallèle)

16. **Routeur** (TanStack Router recommandé) : URLs `/cases/:id/pricing` etc., sections lazy-loadées, ErrorBoundary par route.
17. **Session complète** : timer proactif sur `expires_in`, handler global 401→refresh→re-login modal ; intégrer les 3 endpoints fetch brut au mécanisme de retry ; `AbortController` + timeout sur toutes les requêtes ; logout purgeant localement même si l'appel réseau échoue.
18. **RBAC UI** : masquer conditionné par `actor_kind` (union TypeScript stricte, pas `string`), navigation différenciée patron/collaborateur, erreurs scopées par panel (fin du bus unique last-wins).
19. **Chaînage des agrégats** : sélecteurs d'agrégats contextuels remplaçant la saisie d'UUIDs ; montants en euros avec conversion centimes à la frappe ; pagination réelle des listes tronquées (`slice(0,4)` etc.).
20. **Tooling** : ESLint (+ typescript-eslint, react-hooks) + script `lint` ; déclarer `@testing-library/dom` ; MSW pour les mocks réseau.

### Phase 4 — Exploitation prouvable (avant premier client payant)

21. **Backup off-site** (restic/rsync vers stockage externe) + runbook de restauration réelle exécuté et horodaté ; healthchecks sur les 4 workers preprod ; alerte réelle (mail/webhook) derrière `smart-ao-health-alert.service`.
22. **Rate limiter distribué-ready** : garde-fou bloquant le démarrage si `replicas > 1` avec implémentation mémoire, ou bascule Redis/PG.
23. **Blacklister les secrets par défaut connus** dans `production.py` (`dev-only-signing-key-change-me-*`) ; retirer le mot de passe commis de `alembic.ini:5` ; retirer la publication du port 5432 en compose dev ou isoler le réseau.
24. **Reproductibilité image** : installer depuis `uv export --format requirements.txt --locked` dans `backend.Dockerfile`.
25. **Gate VPS réel** (déjà listé `todo.md:26`) : EICAR, HTTPS, timers, sauvegarde/restauration, supervision — exécuté, pas simulé.

### Feuille de route synthétique

| Jalon | Contenu | Critère de sortie mesurable |
|---|---|---|
| J1 (sem. 1) | CI vivante + décision coverage | 1 run vert ; coverage ≥ seuil choisi |
| J2 (sem. 4) | Socle fiabilité | Outbox bornée, transitions contraintes, DI auth, archi-test inter-modules rouge→vert |
| J3 (sem. 10) | Moteur métier v1 | 1 DCE réel analysé : fiches risque CCAP + prix plancher + DC1/DC2 générés |
| J4 (sem. 12) | Frontend utilisable | Parcours complet sans saisie d'UUID, session robuste, RBAC UI |
| J5 (pré-vente) | Exploitation prouvée | Backup off-site restauré sur hôte neuf, VPS gate signé, alertes reçues |

---

## ANNEXE — Méthodologie et limites

- Audit statique approfondi + exécution ciblée vérifiée : suite vitest (93 tests verts), collecte pytest (1 325 tests), mesure `coverage report` (67,46 %), greps négatifs de sécurité et de vocabulaire métier (résultats reproductibles).
- La partie DB-gated de la suite pytest n'a pas pu être exécutée ici (PostgreSQL local inaccessible : `FATAL: password authentication failed`) — cohérent avec l'état auto-documenté du projet ; les constats DB reposent sur la lecture des migrations/modèles/tests.
- Aucun test d'intrusion actif ni scan dynamique (DAST) : périmètre exclu par le projet lui-même (`todo.md:60`).
