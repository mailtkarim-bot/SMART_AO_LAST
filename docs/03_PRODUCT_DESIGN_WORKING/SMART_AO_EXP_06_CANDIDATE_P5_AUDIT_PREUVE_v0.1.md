# SMART AO — EXP-06
## Candidate persistante et autorisation P5

**Statut :** PREUVE VERTICALE P5 EXÉCUTÉE · CANDIDATURE SEULE ET RÉCEPTION INCONNUE AJOUTÉES · REMISE EXTERNE NON EFFECTUÉE  
**Date :** 15 septembre 2026  
**Autorité produit/métier :** `docs/00_REFERENCE_ACTIVE/SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md`
**Tranche suivante :** cadrer la copie de sauvegarde et le redépôt, puis fermer les critères de rôles, d'audit et de gel d'EXP-06.

## 1. But de la tranche

EXP-06 doit rendre contrôlable le passage d’une réponse préparée à une remise humaine. Le premier incrément ne dépose rien auprès d’un tiers : il prouve qu’une candidate persistante peut recevoir une autorisation humaine P5 portant sur une version exacte et un manifeste exact, puis que l’export est refusé tant que cette autorisation n’existe pas.

## 2. Contrat retenu

Une `SubmissionPackageRecord` existante reste immuable. L’autorisation est un fait séparé, append-only, dans `SubmissionPackageAuthorizationRecord` :

- tenant et package sont liés par une clé étrangère composite ;
- `package_version` doit égaler la version attendue par la commande ;
- `manifest_sha256` est recalculé sur le JSON canonique (`ensure_ascii=False`, clés triées, séparateurs compacts) ;
- une seule autorisation existe pour un package et une version ; la commande reste idempotente par `command_id` ;
- l’état persistant unique est `AUTHORIZED` ; une fonction PostgreSQL refuse toute modification ou suppression ;
- le motif, l’acteur Patron et son membership sont conservés sans contenu de pièce ni secret.

La route Patron est `POST /api/v1/patron/submission-packages/{submission_package_id}/authorize`. Elle exige un bearer MFA valide, un Patron Admin ou Delegate actif, une version positive et une justification non vide. Le handler revalide le package dans le tenant, la version, l’intégrité du manifeste et la porte de décision de soumission. Il publie `SubmissionPackageAuthorized` avec `external_submission: NOT_PERFORMED`.

La route `GET /api/v1/patron/submission-packages/{submission_package_id}/manifest` permet au Patron de relire la version, le SHA-256, les entrées et les exclusions déclarées (`private_storage`, `financial_amounts`, `external_submission_result`) sans exposer de clé de stockage ni de montant.

Les intentions de signature et les preuves de réception manuelle conservent également le `manifest_sha256` du package au moment de leur création. Une modification ultérieure du package ne peut donc pas être confondue avec le fait signé ou reçu.

Le paquet porte désormais un mode explicite `FULL` ou `CANDIDATURE_ONLY`. Le mode candidature seule exige une justification persistée, conserve le périmètre d'Affaire dans le manifeste et omet le snapshot financier ainsi que l'entrée de pricing. Une nouvelle préparation avec une nouvelle intention produit une version distincte qui doit être relue et autorisée à nouveau ; aucun redépôt n'est déduit d'un téléchargement antérieur.

L’export ZIP existant vérifie désormais, dans cet ordre, le package tenant-scopé, l’intégrité du manifeste, le document technique, la décision de soumission et l’autorisation P5 exacte. Sans ligne correspondante, il renvoie `SUBMISSION_PACKAGE_NOT_AUTHORIZED` et ne lit pas le stockage privé.

## 3. Parcours UI minimal

Après la préparation d’un package, le panneau Patron expose :

1. la prévisualisation du manifeste exact ;
2. la version du package à autoriser ;
3. une justification de contrôle ;
4. le bouton « Autoriser la remise humaine » ;
5. l’export ZIP seulement après confirmation de l’autorisation.

Le hook conserve `command_id`, `idempotency_key` et `authorization_id` après une réponse réseau inconnue. Un second clic rejoue exactement la même intention. L’interface garde l’invariant visible `external_submission: NOT_PERFORMED`.

## 4. Preuves exécutées

- **Serveur applicatif/PostgreSQL :** 36 tests combinés de `test_submission_package.py` et `test_submission_evidence.py` passent ; ils couvrent P5, manifeste, export, tentative humaine `UNKNOWN`, justification obligatoire de candidature seule et absence de pricing ; la suite préparation, revue, remise et routes conserve ses preuves existantes.
- **Front :** 163 tests passent ; les tests couvrent l’appel API P5, la lecture du manifeste exact, la lecture des preuves partielles, les identifiants stables après résultat inconnu, la validation UI et l’export masqué avant autorisation ; `pnpm typecheck`, `pnpm lint` et `pnpm build` passent.
- **Statique :** Ruff, format Ruff, mypy ciblé et `git diff --check` passent.
- **Limite d’environnement :** les tests HTTP synchrones utilisant `starlette.testclient.TestClient` restent suspendus dans cet environnement ; une route FastAPI vide reproduit le blocage, indépendant du contrat P5. Les preuves applicatives et PostgreSQL ont donc été exécutées séparément.

## 5. Décisions et limites

- L’autorisation P5 est distincte de la signature et de la preuve de dépôt ; aucune réussite externe n’est fabriquée.
- Le manifeste canonique déclare ses exclusions de confidentialité sans reprendre les noms de champs privés ni de montants.
- La signature et la preuve manuelle sont chacune rattachées au hash exact du manifeste ; elles restent des faits indépendants.
- La lecture des preuves expose uniquement `PARTIAL` et `NOT_PERFORMED`; elle ne déduit ni dépôt réussi ni rapprochement complet.
- Un Delegate peut autoriser selon ses capacités déléguées ; l’export conserve la restriction Patron Admin déjà existante.
- La validation détaillée du contenu, la signature, le dépôt humain, les lots et le rapprochement complet de réception restent à prouver séparément ; le redépôt est représenté par une nouvelle version de package, mais sa copie de sauvegarde et son acte externe restent hors système.
- Aucun fournisseur externe, worker, fichier brut ou nouvelle dépendance n’est introduit dans cette tranche.

## 6. Références de code

- `backend/app/modules/submission/application/service.py`
- `backend/app/modules/submission/infrastructure/models/submission.py`
- `backend/alembic/versions/20260915_0071_submission_package_authorizations.py`
- `backend/app/interfaces/http/routes/patron_submission.py`
- `backend/app/interfaces/http/routes/patron_submission.py` — lecture Patron-only du manifeste exact.
- `backend/app/modules/submission/application/signature_service.py`
- `backend/app/modules/submission/application/evidence_service.py`
- `backend/alembic/versions/20260915_0072_signature_manifest_hash.py`
- `backend/alembic/versions/20260915_0073_evidence_manifest_hash.py`
- `backend/app/modules/submission/public/evidence_contracts.py`
- `backend/app/interfaces/http/routes/patron_submission_evidence.py`
- `web/src/features/submission/SubmissionPanel.tsx`
- `web/src/features/submission/useSubmissionActions.ts`

## 7. Prochaine tranche

Cadrer la copie de sauvegarde et le redépôt, puis fermer les critères de rôles, d'audit et de gel d'EXP-06.
