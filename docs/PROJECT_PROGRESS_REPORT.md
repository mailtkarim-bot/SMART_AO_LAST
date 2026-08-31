# SMART_AO V8 — Rapport global d’avancement

**Date de mise à jour :** 30 août 2026
**Branche de référence :** `main`
**Dernier commit publié :** [`16f61b9`](https://github.com/mailtkarim-bot/SMART_AO_V8/commit/16f61b9)
**Dernière CI verte :** [workflow `32912209432`](https://github.com/mailtkarim-bot/SMART_AO_V8/actions/runs/32912209432)
**Validation intégrée courante :** 1132 tests backend non-DB passés, mypy `backend/app` propre sur 386 fichiers, Ruff check/format pass, couverture CI **88,77 %** avec seuil à 85,50 %, frontend typecheck/lint/build/tests verts.

## 1. Position honnête du produit

SMART_AO V8 est un **backend métier avancé et un frontend réel**, avec une architecture modulaire, une sécurité tenant-scoped, une idempotence systématique et une surface fonctionnelle couvrant la majeure partie du cycle AO. Le projet a dépassé le stade prototype et dispose d’un domain model pur, d’une outbox, d’invariants append-only et d’une CI exécutée sur runners GitHub Actions.

Il ne faut toutefois pas le présenter comme une application commerciale achevée de bout en bout. Les frontières restantes sont : la consolidation des derniers refactors architecturaux (ARCH-001), la preuve d’exploitation sur VPS réel (ClamAV/EICAR, HTTPS, backup/restore), le raccordement frontend à une URL HTTPS backend vérifiée, les recettes fournisseurs et la validation juridique/métier des pièces finales. Le dépôt électronique ne sera jamais déclaré réussi sans accusé externe vérifiable.

La séparation fondamentale reste obligatoire : le collaborateur prépare et remonte des informations opérationnelles ; le patron conserve la décision, le chiffrage, la marge, la trésorerie et l’action de dépôt. Aucun contrat collaborateur ne doit transporter de données financières.

## 2. État par domaine

| Domaine | État | Fonctionnalités réellement présentes | Limite actuelle |
|---|---|---|---|
| Noyau métier | Livré et stable | `Case`, Consultation, DCE, Decision, révisions, événements, outbox, receipts et idempotence. | Assemblage E2E navigateur authentifié de bout en bout. |
| Sécurité et tenants | Livré et durci | Authentification, sessions, refresh rotatif, MFA/TOTP complet, step-up sur décision et signature, RBAC/ABAC/ReBAC, audit append-only, anti-brute-force. | Preuve d’exploitation réelle sur VPS. |
| Admission DCE | Livrée côté code | Staging privé, upload binaire, limites, hash serveur, MIME détecté, ClamAV fail-closed, rétention et extraction déterministe. | Scan ClamAV réel, HTTPS, stockage privé et sauvegardes sur hôte réel. |
| Analyse DCE | Livrée dans un périmètre déterministe | Analyse lexicale RC, classification, exigences atomiques, preuves sourcées, confirmations humaines, impact de rectificatif, OCR opt-in RapideOCR, détection de contradictions interdocuments. | Corpus Golden DCE anonymisé, métriques OCR/RAG, modèle BGE réel. |
| Entreprise | Livrée dans son premier incrément | Société, assurances/Kbis/RIB, uploads privés, vérification humaine, qualifications, références, capacités, preuves versionnées et bibliothèque. | Workflows métier plus riches et usage des preuves dans la qualification. |
| Collaboration | Fondations avancées | Affectations, interactions, tâches, demandes d’information, blocages, readiness, revues, corrections, brouillons techniques et documents générés. | Parcours complet de production de l’offre technique assemblé E2E. |
| Finance patronale | Très avancée | Snapshots, lignes, publication contrôlée, scénarios privés versionnés, import DPGF/BPU/Excel sécurisé avec libmagic/ClamAV, preview persistée, rapprochement DPGF/BPU. | Écriture durable des lignes importées et calcul opérationnel complet. |
| Génération documentaire | Livrée dans un périmètre contrôlé | Assembleur déterministe avec `TechnicalDocumentFacts`, exigences DCE structurées, versions append-only, readiness, stockage privé et enveloppes DC1/DC2/DC4 non contractuelles. | Validation juridique/métier des textes finaux. |
| Cockpit patron | Unifié et enrichi | React/Vite : login, création d’affaire, affectations, DCE, opportunities/BOAMP, Dossier décision, risques, GO/NO-GO conditionnel, scénarios pricing, paquet, preuve de dépôt, TOTP. | Raccordement à une URL HTTPS backend réelle et E2E navigateur. |
| Dépôt | Préparation et preuve manuelle livrées | Paquet tenant-scoped idempotent, manifest JSONB hashé, contrôles de versions publiées, preuve manuelle hashée append-only, garde Decision intégré et `external_submission` permanent `NOT_PERFORMED`. | Transmission électronique réelle et accusé externe vérifié. |
| Veille | Intégrée | Profil opportunity, ingestion BOAMP, observations fingerprintées, scoring, qualification humaine `QUALIFIED`/`REJECTED`/`SNOOZED`, conversion contrôlée en Case, cockpit frontend. | Recette réseau BOAMP stable et recette externe. |
| Déploiement | Préparé, non exécuté sur VPS | Factory production, Caddy, healthchecks, pinning digest, sauvegarde/restauration isolée, timers et rotation des secrets. | Gate VPS réel, HTTPS, EICAR, supervision externe et rapport opérateur. |

## 3. Corrections de socle publiées

Les corrections confirmées par les audits sont maintenant intégrées : limitation anti-brute-force sur login/refresh, fixtures PostgreSQL centralisées, logs JSON et `request_id`, endpoint `/metrics` sans données métier, runtime backend non-root, dépendances frontend figées, seuil de couverture et scénarios de concurrence déterministes.

Le durcissement architectural a ensuite isolé la lecture DCE de l’application préparation derrière un port et un adaptateur, déplacé la détection de contenu sensible vers un contrat public, extrait les ports de quarantaine vers `platform.storage` et déplacé le bounded context `enterprise` hors de `membership`. Les tests d’architecture vérifient désormais ces nouvelles frontières.

| Slice | Commit | Preuve distante |
|---|---:|---:|
| Anti-brute-force | `025c36d` | CI `32076462140` verte |
| Fixtures PostgreSQL centralisées | `aac4de0` | CI `32078237301` verte |
| Observabilité et runtime non-root | `0ecb24c` puis `0ab3cbc` | CI corrective `32080763983` verte |
| Dépendances frontend reproductibles | `d4b33fe` | CI `32081102590` verte |
| Couverture et concurrence | `e3eafc7` | CI `32083322693` verte |
| Documentation consolidée | `cff4302` | CI `32083816529` verte |
| Frontières préparation | `bdce65a` | CI `32104138038` verte |
| Arborescence enterprise et ports platform | `4c995d2` | CI `32104886313` verte |

## 4. Architecture et arborescence

Le dépôt respecte la stratégie de **monolithe modulaire incrémental** : les modules réels ont des couches séparées, les routes HTTP ne portent pas les transitions métier, les tests d’architecture sont bloquants et les bounded contexts nouvellement réels sont maintenant rangés dans `backend/app/modules/enterprise`.

Cette conformité doit être lue comme une conformité vérifiée sur les frontières couvertes, non comme une preuve mathématique que chaque règle future ARC-01 est déjà exhaustive. Toute nouvelle dépendance inter-module doit passer par un contrat public, un port, un événement ou une commande aval corrélée, puis recevoir un test d’architecture.

## 5. Parcours métier restant à construire

Le parcours cible est : **DCE reçu → DCE sécurisé → lecture/confirmation → préparation collaborative → revue patronale → chiffrage → génération des pièces → paquet de dépôt → transmission**.

Les étapes DCE, préparation collaborative, génération technique, cockpit patron, navigation unifiée, wizard collaborateur, scénarios pricing, import sécurisé et préparation contrôlée du paquet sont codées et validées par CI. La suite immédiate est le gate VPS, désormais seule frontière opérationnelle ouverte. Un éventuel connecteur de transmission restera ultérieur et le dépôt électronique ne devra jamais être simulé comme réussi sans preuve externe.

## 6. Ordre de travail avant VPS

| Phase | Slice | Résultat attendu |
|---:|---|---|
| 1 | Stabilisation | Tests verts hors DB, Ruff/mypy/format propres, documentation d’état à jour. |
| 2 | Fin du refactoring ARCH-001 | Extraire les derniers readers/ports dans `pricing` et `membership` ; verrouiller par un test d’architecture anti-import `infrastructure` dans `application/`. |
| 3 | Cœur métier BTP | Registre CCAP/CCTP, croisement CCTP–DPGF–BPU, OCR Golden Corpus, GO/NO-GO conditionnel finalisé. |
| 4 | E2E navigateur | Parcours Playwright authentifié : Case → DCE → préparation → pricing → decision → submission. |
| 5 | Gate VPS | Docker préproduction, PostgreSQL 16, ClamAV/EICAR, Caddy/HTTPS public, backup/restore, supervision et rapport opérateur. |
| 6 | Recettes fournisseurs | S3/MinIO, SMTP, signature, bus externe, BOAMP/INSEE, OCR avancé avec secrets runtime hors Git. |
| 7 | Validation juridique/métier | Textes DC1/DC2/DC4, droits `PATRON_DELEGATE`, conservation et conformité opérationnelle. |

## 7. Limites explicitement conservées

MinIO sans contrat de stockage stabilisé, Redis/sharding/tracing distribué spéculatifs, DAST/Semgrep déjà couverts par les contrôles existants et tests de charge nécessitant un environnement dédié ne sont pas ajoutés artificiellement. L’import métier actuel reste une prévisualisation contrôlée ; les fichiers non `.xlsx`, les macros, les archives surdimensionnées et les classeurs malformés sont rejetés plutôt que traités implicitement. Les formats documentaires non pris en charge restent explicitement `UNSUPPORTED` plutôt que de produire une fausse analyse.

## 8. Références internes

| Document | Rôle |
|---|---|
| [`docs/PROJECT_STATE.md`](PROJECT_STATE.md) | Reprise technique, slices, migrations, validations et risques courants. |
| [`todo.md`](../todo.md) | Checklist durable des frontières restantes. |
| [`docs/reference/SMART_AO_V8_ARC_01_CONTRAT_ARBORESCENCE_MODULES.md`](reference/SMART_AO_V8_ARC_01_CONTRAT_ARBORESCENCE_MODULES.md) | Contrat d’arborescence, couches et dépendances. |
| [`docs/reference/SMART_AO_V8_PREPARATION_COMPLETENESS_01_CONTRAT.md`](reference/SMART_AO_V8_PREPARATION_COMPLETENESS_01_CONTRAT.md) | Contrat de readiness et génération technique contrôlée. |
| [`docs/AUDIT_REMEDIATION_MATRIX.md`](AUDIT_REMEDIATION_MATRIX.md) | Réconciliation du premier audit. |
| [`docs/AUDIT2_RELEVANCE_MATRIX.md`](AUDIT2_RELEVANCE_MATRIX.md) | Pertinence du second audit et corrections retenues. |
