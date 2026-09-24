# RAPPORT D’AUDIT SYSTÈME INDÉPENDANT — SMART_AO V8

**Date :** 23 septembre 2026  
**Auditeur :** Antigravity / Google DeepMind Agentic Systems  
**Périmètre audité :** Dépôt `/home/noor/PROJECTS/BTP/SMART_AO_V8` (`git@github.com:mailtkarim-bot/SMART_AO_LAST.git`)  
**Branche auditée :** `feat/ccap-cctp-risk-register-20260831`  
**Commit examiné :** `374510a033e786884cc5ac0f0c322a12e0b6fc5e` (aligné avec `origin/main`)  
**Méthodologie :** Zéro complaisance, zéro extrapolation. Confrontation directe de la documentation avec le code source, les 90 migrations Alembic, l'exécution locale de 1 720 tests backend sur PostgreSQL 16 réel, 187 tests frontend Vitest, linters, SAST et scans de dépendances.

---

## 1. Résumé exécutif

### Verdict global : **GO CONDITIONNEL LOCAL / NO-GO PRODUCTION PUBLIQUE**

Le projet a accompli une progression majeure depuis les audits de fin août 2026 (passage de 55 à 90 migrations Alembic, de 1 343 à 1 720 tests backend, de 98 à 187 tests frontend). Les régressions opérationnelles critiques précédentes (service `migrate` en dev, tête Alembic non recoupée, faille de course d'idempotence, scan antivirus sur l'import pricing, taxonomie initiale CCAP/CCTP) ont été effectivement corrigées et prouvées par exécution.

Cependant, le produit **n'est pas prêt pour une mise en exploitation commerciale publique** : aucun déploiement VPS réel n'a été exécuté, les intégrations externes réelles (plateformes de dépôt AO, signature eIDAS, SMTP de production) restent absentes ou simulées, et le moteur de chiffrage automatique reste asymétrique (ventes importées du DPGF, mais décomposition des coûts non alimentée automatiquement).

```
Score Global d'Ingénierie & Sécurité : 78 / 100
Score de Prêt-à-l'Emploi Commercial BTP : 48 / 100
```

| Axe | Note / 100 | Statut | Synthèse |
|---|---|---|---|
| 🔐 **Sécurité & Confidentialité** | **94** | EXCELLENT | Hermétisme financier absolu (4 barrières), TOTP MFA complet, anti-SSRF, upload fail-closed (ClamAV + libmagic). 0 fuite détectée. |
| 🏗️ **Architecture & Domaine pur** | **82** | TRÈS BON | 0 fuite ORM/HTTP dans `domain/` (75 tests AST). Progrès sur les ports/readers, mais 25 imports croisés `application -> foreign infrastructure` subsistent. |
| 🗄️ **PostgreSQL & Alembic** | **91** | EXCELLENT | 90 migrations rigoureusement séquentielles, triggers append-only, isolation tenant composite, cycle complet base↔head vérifié sur PG 16. |
| ⚙️ **Fiabilité transactionnelle & Outbox** | **80** | BON | Outbox transactional réel, `CockpitProjectionWorker` créé, course d'idempotence neutralisée par savepoint. Manque la purge des messages `PUBLISHED`. |
| 🖥️ **Frontend React/TypeScript** | **74** | BON | 187 tests verts, 0 `any`, tokens mémoire, CSRF double submit, ErrorBoundary robuste. Reste sans routeur officiel (navigation par état interne). |
| 🚀 **Opérations & Docker/CI** | **68** | MOYEN | Tests de contrats ops solides (45 tests), dev-compose réparé. Bloqué par l'absence d'infrastructure VPS réelle et dépendances vulnérables (`pypdf 6.16.0`). |
| 💼 **Cœur métier BTP** | **52** | EN COURS | Taxonomie contractuelle CCAP/CCTP intégrée (pénalités, garanties, sous-traitance), Cost-Basis pur sans flottants, enveloppes DC1/DC2/DC4. Mais chiffrage DPGF partiel. |

---

### Les 3 principaux risques ouverts

1. **Supply Chain & Dépendances :** Présence de 5 vulnérabilités connues détectées par `pip-audit`, dont `pypdf 6.16.0` (vulnérabilités de déni de service et dépassement de ressources PYSEC-2026-3910 et PYSEC-2026-3911, corrigées en `6.16.1`) et `accelerate 1.14.0` (PYSEC-2026-3804).
2. **Couplage résiduel inter-modules :** 25 imports d'infrastructure étrangère directement depuis la couche `application` (notamment `submission/application/service.py` important les modèles ORM de 4 autres modules), contournant les contrats publics.
3. **Accumulation non bornée de la base :** Zéro routine de purge ou de rétention sur `outbox_messages` (statut `PUBLISHED`) et sur `domain_events`. Saturation inéluctable du disque en exploitation intensive.

### Les 3 principaux blocages de production

1. **Aucun hôte VPS réel qualifié :** Le runbook VPS préproduction n'a été exécuté sur aucun serveur réel hors de l'environnement de développement ; aucune sauvegarde hors-hôte ni restauration désastre n'a été prouvée sur un système externe.
2. **Fournisseurs externes non raccordés :** Aucun raccordement réel pour la signature électronique (provider fictif déterministe en place), les serveurs SMTP (désactivé par défaut) ou le bus d'événements externe.
3. **Absence d'exception handler global FastAPI :** Les erreurs inattendues ou les rejets de commande mènent à des exceptions non normalisées (`HTTP 422 COMMAND_REJECTED` uniforme ou HTTP 500 générique), sans discrimination propre côté client.

### Les 3 fonctionnalités métier BTP restant à livrer

1. **Import et ventilation des coûts DPGF :** L'import XLSX n'alimente que les lignes `SALES` ; les déboursés secs (matériaux, main-d'œuvre, matériel, sous-traitance) doivent être saisis manuellement pour calculer le coût de revient réel.
2. **OCR / Analyse PDF scannés activée :** `SMART_AO_ADVANCED_EXTRACTION_ENABLED=0` par défaut ; les DCE municipaux scannés ne sont pas analysés en préproduction sans activation des modèles lourds.
3. **Raccordement et dépôt automatique sur profils d'acheteur :** Aucun dépôt dématérialisé externe réel n'est connecté (conforme au principe de prudence du produit).

---

## 2. Version exacte auditée & Environnement

```text
Dépôt : git@github.com:mailtkarim-bot/SMART_AO_LAST.git
Commit HEAD : 374510a033e786884cc5ac0f0c322a12e0b6fc5e
Branche : feat/ccap-cctp-risk-register-20260831 (synchronisée avec origin/main)
Dernier commit : "docs: repair active documentation link"
Python : 3.12.3 (x86_64-linux) / uv 0.11.21
Node.js : v22.23.2 / npm 10.9.8
Docker : 29.1.3 / Docker Compose v5.5.0
PostgreSQL de test : PostgreSQL 16-alpine (container isolé smart-ao-v8-postgres-5433, port 5433)
Fichiers non suivis détectés : .codex/, .serena/ (outils d'assistance locale, à ajouter au .gitignore)
```

---

## 3. Matrice exhaustive des findings

| ID | Axe | Gravité | Statut | Fichier / Localisation | Constat exact | Impact | Recommandation |
|---|---|---|---|---|---|---|---|
| **SEC-01** | Sécurité | 🟠 Majeur | Ouvert | `pyproject.toml:22` | `pypdf==6.16.0` vulnérable à PYSEC-2026-3910 et PYSEC-2026-3911 | Risque DoS lors du parsing de PDFs DCE malveillants | Mettre à jour `pypdf>=6.16.1` |
| **SEC-02** | Sécurité | 🟡 Moyen | Ouvert | `backend/app/platform/security/rate_limit.py:24` | Rate limiter stocké en mémoire locale du processus (`LoginRateLimiter`) | Inopérant en cas de scale-out horizontal sans affinité IP | Prévoir stockage Redis ou admission reverse-proxy edge |
| **ARCH-01** | Archi | 🟠 Majeur | Ouvert | `backend/app/modules/*/application/` (25 fichiers) | 25 imports directs de `*.infrastructure.models.*` inter-modules | Couplage fort entre bounded contexts, fragilité des évolutions | Remplacer par des Readers/Ports applicatifs assemblés à la composition root |
| **ARCH-02** | Archi | 🟡 Moyen | Ouvert | `backend/app/interfaces/http/routes/*.py` | Absence de `app.add_exception_handler` global | Erreurs aplaties en 422 ou non capturées en 500 sans code d'erreur typé | Enregistrer un gestionnaire d'exception global FastAPI pour `DomainError` et `CommandExecutionError` |
| **OPS-01** | Ops | 🟠 Majeur | Ouvert | `backend/app/platform/persistence/` | Absence totale de purge des messages `PUBLISHED` dans l'outbox et les `domain_events` | Saturation continue de la base PostgreSQL en production | Implémenter un worker ou cron job de rétention avec soft-delete/archivage |
| **OPS-02** | Ops | 🟡 Moyen | Fermé | `docker-compose.yml:26` | Service migrate pointait vers `/app/alembic.ini` au lieu de `/app/backend/alembic.ini` | Crash du conteneur migrate au boot dev | **Vérifié corrigé** : la ligne 26 pointe désormais bien sur `/app/backend/alembic.ini` |
| **OPS-03** | Ops | 🟡 Moyen | Ouvert | `backend/alembic/versions/20260919_0076_task_result_lot_reference.py` | Linter `ruff check .` échoue sur l'ordre des imports dans la migration 0076 | Dette d'outillage local | Exécuter `uv run ruff check --fix` sur les fichiers alembic |
| **BTP-01** | Métier | 🟠 Majeur | Ouvert | `backend/app/modules/pricing/application/import_handler.py:108` | L'import XLSX affecte systématiquement `category="SALES"` | Décomposition des déboursés secs (main d'œuvre, sous-traitance) non automatisée | Permettre la qualification de colonnes de coûts dans le mapper DPGF |
| **BTP-02** | Métier | 🟢 Mineur | Fermé | `backend/app/modules/dce/application/analysis.py:155-215` | Absence de catalogue contractuel CCAP/CCTP | Pénalités et retenues de garantie non détectées | **Vérifié corrigé** : `_RC_RULES` enrichi avec détection regex CCAP/CCTP |
| **BTP-03** | Métier | 🟢 Mineur | Fermé | `backend/app/modules/pricing/domain/cost_basis.py` | Absence de calcul de prix plancher et seuil de rentabilité | Impossibilité de sécuriser la marge du patron | **Vérifié corrigé** : Moteur `calculate_cost_basis` pur en minor units et bps |
| **FRONT-01**| Front | 🟡 Moyen | Ouvert | `web/src/App.tsx` | Absence de routeur client standard (URL deep-links simulés par paramètre d'URL) | Navigation fragile et historique navigateur non standard | Introduire un routage déclaratif type TanStack Router ou React Router |

---

## 4. Séparation stricte des preuves

### A. Preuves exécutées directement au cours de cet audit

1. **Suite backend hors-DB :** 1 196 tests collectés, **1 196 passés (100 %)** en 20,89s via `uv run --extra calendar pytest -m "not db"`.
2. **Suite de persistance PostgreSQL 16 :** 524 tests collectés, **524 passés (100 %)** en 8m27s contre le conteneur `smart-ao-v8-postgres-5433` (`postgres:16-alpine`).
3. **Totalité des tests backend :** **1 720 tests exécutés, 1 720 passés (100 %)**.
4. **Pureté du domaine :** 75 tests d'architecture AST exécutés et passés (`test_*_domain_purity.py`).
5. **Suite frontend complète :** 34 fichiers de test, **187 tests Vitest exécutés et passés (100 %)** en 14,81s.
6. **Typecheck & Linting frontend :** `tsc -b --pretty false` et `eslint .` exécutés avec **0 erreur**.
7. **Build frontend :** `vite build` exécuté avec succès en 426ms (`dist/index.html` 0.53 kB, bundle JS 402 kB gzip 106 kB).
8. **Analyse SAST Python :** `bandit -r backend/app -ll` exécuté sur 56 020 lignes de code : **0 vulnérabilité détectée**.
9. **Contrôle typage backend :** `mypy backend/app backend/tests` exécuté sur 688 fichiers source : **0 erreur**.
10. **Linter backend CI :** `ruff check backend/app backend/tests` et `ruff format --check backend/app backend/tests` exécutés : **0 erreur**.
11. **Détection de secrets :** `detect-secrets-hook --baseline .secrets.baseline` exécuté sur l'arborescence indexée : **0 secret détecté**.
12. **Migrations de données :** Vérification de l'Alembic current head à `20260920_0090`.

### B. Observations d’inspection statique

1. **Confidentialité financière :** Absence totale de capability financière pour le rôle `COLLABORATOR` (`_COLLABORATOR_CAPABILITIES` hermétique). Refus systématique des données `FINANCIAL_PRIVATE` pour tout acteur non-patron.
2. **Protection SSRF et Webhooks :** Validation DNS stricte interdisant les plages privées (RFC 1918), le loopback et les métadonnées cloud dans `backend/app/platform/security/public_http.py`.
3. **Anti-brute force :** `LoginRateLimiter` avec dégressivité exponentielle et lockout progressif dans `backend/app/platform/security/rate_limit.py`.
4. **Course d'idempotence réparée :** `CommandDispatcher._execute_command` utilise désormais un sous-bloc transactionnel `session.begin_nested()` avec capture de l'`IntegrityError` et relecture du receipt concurrent (`dispatcher.py:170-189`).
5. **Couplage inter-modules :** 25 imports directs de modèles ORM d'infrastructure d'autres modules identifiés dans `backend/app/modules/*/application/`.

### C. Affirmations de la documentation non reproduites / non vérifiables

1. **Déploiement VPS et Caddy HTTPS :** Aucun VPS n'est disponible dans l'environnement d'audit. Le comportement de Caddy sur domaine public réel reste non vérifié.
2. **Scan ClamAV sur hôte de prod :** ClamAV a été validé lors des simulations locales précédentes, mais le daemon n'était pas actif sur le port 3310 lors de ce run.
3. **Performances sous forte charge :** Les benchmarks mentionnés dans la documentation correspondent à des mesures locales sur machines de dev et ne garantissent pas le comportement sous latence réseau réelle.

---

## 5. Recommandations prioritaires par niveau d'urgence

### Priorité P0 (Prérequis avant tout déploiement pilote)
- **SEC-01 :** Mettre à jour `pypdf` vers `>=6.16.1` dans `pyproject.toml` pour corriger les deux CVEs signalées par `pip-audit`.
- **OPS-01 :** Concevoir et planifier un worker de purge ou d'archivage des messages outbox `PUBLISHED` et des événements de domaine traités.
- **OPS-03 :** Formater et corriger l'ordre des imports dans `backend/alembic/versions/20260919_0076_task_result_lot_reference.py` via `ruff check --fix`.

### Priorité P1 (Fiabilisation de l'architecture & API)
- **ARCH-01 :** Éliminer les 25 imports `application -> foreign infrastructure` en extrayant des Readers/Ports applicatifs purs.
- **ARCH-02 :** Ajouter un gestionnaire d'exception global FastAPI pour normaliser les retours d'erreurs domaine vers le client.
- **GIT-01 :** Ajouter `.codex/` et `.serena/` dans `.gitignore`.

### Priorité P2 (Amélioration de la valeur métier BTP)
- **BTP-01 :** Étendre l'importateur Excel pour permettre le mapping de colonnes de coûts directs et sous-traitance, afin d'alimenter directement `calculate_cost_basis`.
- **FRONT-01 :** Moderniser la navigation frontend en intégrant un routeur client complet permettant les URLs profondes naturelles.

---

## 6. Décision commerciale

| Question Commerciale | Réponse & Recommandation |
|---|---|
| **Peut-on vendre le produit comme plateforme AO complète ?** | **NON.** Le dépôt externe automatisé n'est pas branché, la lecture automatique des DCE scannés est inactive par défaut, et la ventilation des coûts DPGF reste partiellement manuelle. |
| **Peut-on le vendre comme outil d'aide à la décision patronale ?** | **OUI, en phase pilote restreinte.** L'analyse du RC/CCAP, le calcul rigoureux de prix plancher/seuil de rentabilité, la génération des brouillons DC1/DC2/DC4 et le coffre-fort financier patronal sont pleinement opérationnels et sécurisés. |
| **Quelles fonctions ne doivent absolument pas être promises ?** | Ne pas promettre le dépôt dématérialisé en un clic sur les profils d'acheteurs (ex: AWS, Maximilien), ni la signature électronique légale intégrée (elle reste externe), ni la conversion magique des devis fournisseurs en coût de revient. |
| **Quelles garanties manquent pour un premier client pilote ?** | Provisionner un VPS de production, déployer la stack avec SSL Caddy réel, valider la politique de backup hors-site, et mettre à jour la dépendance vulnérable `pypdf`. |

---

## 7. Conclusion finale

> **Au commit `374510a`, le produit est classé GO CONDITIONNEL LOCAL / NO-GO PRODUCTION PUBLIQUE.**  
> Les éléments réellement opérationnels sont l'authentification MFA durcie, l'isolation multi-tenant absolue, la pureté du domaine, les 90 migrations PostgreSQL, le moteur exact de calcul de prix plancher et de marge, la taxonomie de détection des risques CCAP/CCTP et la génération de brouillons DC1-DC4.  
> Les éléments seulement préparés, optionnels ou simulés sont l'OCR des PDF scannés, le bus d'événements externe, la signature électronique et le dépôt sur profils d'acheteur.  
> Les blocages avant production sont la vulnérabilité `pypdf 6.16.0`, l'absence d'infrastructure VPS qualifiée avec sauvegardes hors-site prouvées, et l'absence de purge outbox.  
> Les preuves que nous n'avons pas obtenues sont le comportement sur un domaine HTTPS public distant et l'interfaçage avec un serveur SMTP de production.
