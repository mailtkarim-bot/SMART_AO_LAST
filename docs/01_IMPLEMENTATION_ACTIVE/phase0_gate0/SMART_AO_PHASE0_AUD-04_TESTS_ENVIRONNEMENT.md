# SMART AO — AUD-04 — Tests autoritatifs et reproductibilité

**Date :** 12 septembre 2026  
**Référence :** `feat/ccap-cctp-risk-register-20260831@b6b05b8`  
**Statut :** TERMINÉ  
**Verdict :** frontend et contrôles ciblés verts ; baseline backend globale non verte et environnement DB non reproductible

## 1. Décision

Gate 0 ne peut pas considérer l'environnement comme apte à mesurer une régression métier. Le backend contient 1 624 tests collectables, mais 477 demandent PostgreSQL et 1 147 sont marqués non-DB. La campagne DB échoue faute de service joignable. La campagne non-DB se bloque de façon reproductible sur un test de route après sept succès. Mypy échoue dans un double de test.

Les résultats verts sont néanmoins significatifs : 75 tests d'architecture, 17 tests Golden/Knowledge ciblés, Ruff, format, Bandit, mypy application seule, Alembic offline, simulation de composition et toute la chaîne frontend.

## 2. Commande canonique

Le dépôt doit être exécuté avec `uv`, pas avec le Python global :

```bash
UV_CACHE_DIR=/tmp/smartao-uv-cache uv run --extra calendar pytest ...
```

Une tentative antérieure avec `pytest` global n'est pas une preuve produit, car elle n'utilisait pas l'environnement déclaré par le dépôt.

## 3. Résultats backend

| Contrôle exécuté | Résultat | Interprétation |
|---|---|---|
| collecte `backend/tests` | 1 624 tests | découverte réussie |
| sélection marker `db` | 477 tests | exige PostgreSQL |
| sélection `not db` | 1 147 tests | voir blocage ci-dessous |
| `pytest backend/tests/architecture -q` | **75 passed** | règles d'architecture actuelles vertes |
| `pytest test_golden_corpus.py test_knowledge_benchmark.py -q` | **17 passed en 0,08 s** | harnais/contrats testés sur données synthétiques/vides |
| suite backend complète avec couverture | au moins 39 erreurs dans la série DB, puis interruption | PostgreSQL non joignable ; aucun verdict fonctionnel global |
| suite `-m 'not db'` avec couverture | aucune fin après plusieurs minutes | interrompue ; signal de hang |
| test isolé d'interaction d'affectation | timeout 20 s, code 124 | hang reproductible |
| `ruff check backend/app backend/tests` | réussi | lint vert |
| `ruff format --check ...` | 641 fichiers déjà formatés | format vert |
| `mypy backend/app` | **390 fichiers, aucun problème** | application typée |
| `mypy backend/app backend/tests` | **1 erreur** | baseline globale rouge |
| `bandit -ll` | réussi | aucune alerte moyenne/haute dans le périmètre exécuté |

### Test bloquant non-DB

Le test suivant ne termine pas en 20 secondes et n'émet aucun résultat après sa collecte :

```text
backend/tests/api/test_assignment_interactions_routes.py::
test_assignment_interactions_routes_reject_missing_or_malformed_bearer[None]
```

Il bloque aussi la campagne `not db` après sept tests réussis. PR-A0 devra diagnostiquer le démarrage de l'application ou la dépendance réseau/DB déclenchée par cette route. Le réparer pendant Phase 0 aurait enfreint le mandat.

### Erreur mypy

```text
backend/tests/application/test_preparation_snapshot_transmission.py:435
```

Le double fourni comme `action_writer` ne déclare pas `create_from_registered_risk` ni `create_from_risk_requirement_link`. L'application seule est verte ; le défaut appartient à la compatibilité du double de test avec le port actuel.

### Tests ignorés, xfail et non démarrés

La recherche statique n'a trouvé aucune déclaration `skip` ou `xfail` dans `backend/tests`. Les 477 tests `db` exclus de la tentative non-DB sont une sélection par marker, pas des skips. Comme les deux campagnes globales n'ont pas atteint leur fin, le nombre de tests réellement démarrés, passés ou non démarrés ne doit pas être déduit de la collecte. PR-A0 doit produire un rapport terminal qui distingue `passed`, `failed`, `skipped`, `xfail`, `not started`, `timeout` et `environment blocked`.

## 4. Base de données et infrastructure

| Contrôle | Résultat | Limite |
|---|---|---|
| `docker compose version` | disponible | client seulement |
| `docker version` | socket daemon refusé | impossible de démarrer PostgreSQL/ClamAV |
| Alembic upgrade `head --sql` | réussi | SQL offline uniquement |
| `scripts/simulate_staging_deploy.sh --compose-config` | réussi | validation de configuration |
| `ops/preflight-checklist.sh` sans environnement | échec d'interpolation | variables obligatoires absentes |
| PostgreSQL live | BLOQUÉ | aucune contrainte/catalogue live |
| EICAR/ClamAV | NON EXÉCUTÉ | service indisponible |
| backup/restore | NON EXÉCUTÉ | environnement absent |
| HTTPS/VPS | NON EXÉCUTÉ | hors machine auditée |

Les contrôles CI liés au réseau ou aux images, notamment `pip-audit`, construction d'images et scan Trivy, n'ont pas été rejoués localement. Ils restent `NON EXÉCUTÉS`, sans présumer leur résultat dans la CI distante.

## 5. Résultats frontend

Dans `web/` :

| Commande | Résultat |
|---|---|
| `pnpm lint` | réussi |
| `pnpm test` | **31 fichiers, 132 tests passants** |
| `pnpm typecheck` | réussi (`tsc -b --pretty false`) |
| `pnpm build` | réussi, bundle Vite produit |

Ces résultats qualifient le frontend actuel ; ils ne satisfont pas encore UX-GATE-01, qui exige des scénarios, états, confidentialité, clavier, lecteur d'écran et acceptation sur douze écrans.

## 6. Golden DCE et secrets

Le validateur Golden retourne :

```text
valid corpus=smart-ao-anonymized-dce-v1 documents=0
```

Le schéma est valide, mais aucun document ni annotation réelle n'est exercé. Le contrôle `detect-secrets` a retourné le code 123 parce qu'il a recalculé des numéros de ligne dans la baseline sur ce checkout sale. La modification automatique a été annulée à l'identique. Ce contrôle est **non conclusif** et doit être rejoué sur un checkout maîtrisé en PR-A0.

## 7. Skips, xfails et tests non commencés

- Aucun `skip` ou `xfail` explicite significatif n'a été trouvé par recherche textuelle dans les tests.
- Les 477 tests DB ne sont pas des skips : ils ont été sélectionnés, mais leur infrastructure manque.
- La campagne globale n'a pas atteint les tests situés après le hang non-DB ; ils sont **non commencés**, pas passants.
- `pip-audit`, builds d'images et Trivy existent dans la CI mais n'ont pas été exécutés localement ; ils peuvent exiger réseau et daemon.

## 8. Baseline proposée pour PR-A0

PR-A0 devra produire un seul script/document canonique qui :

1. démarre PostgreSQL et ClamAV avec versions épinglées ;
2. attend les healthchecks ;
3. exécute migrations sur base vide puis sur fixture peuplée ;
4. exécute les 1 624 tests sans hang ;
5. distingue test échoué, bloqué, skip autorisé et non commencé ;
6. exécute Ruff, format, mypy, Bandit et secrets ;
7. exécute lint, typecheck, tests et build frontend ;
8. publie durées, versions et rapports sans modifier les baselines suivies ;
9. s'arrête avec un code non nul au premier gate obligatoire rouge.

## 9. Gate

**Question 5 — environnement et Golden DCE mesurent-ils les régressions ? `NON`.** Action bornée : autoriser PR-A0 seulement après la décision Gate 0, puis PR-A1 après sortie verte de A0.

## 10. Preuves

- `pyproject.toml`
- `backend/tests/architecture/`
- `backend/tests/api/test_assignment_interactions_routes.py`
- `backend/tests/application/test_preparation_snapshot_transmission.py`
- `backend/tests/application/test_golden_corpus.py`
- `backend/tests/application/test_knowledge_benchmark.py`
- `web/package.json`
- `.github/workflows/`
- `ops/golden-corpus/manifest.example.json`
- [QUAL-01](./SMART_AO_PHASE0_QUAL-01_GOLDEN_DCE.md)
