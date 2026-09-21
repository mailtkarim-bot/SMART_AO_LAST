# SMART AO — Audit sécurité de production Phase 11

**Date :** 20 septembre 2026  
**Statut :** audit local exécuté  
**Périmètre :** secrets, dépendances, upload hostile, isolation, audit et restauration

## Résultats exécutés

- suite backend complète contre PostgreSQL Docker : **1 717 passés, 2 skips PIL, 10 avertissements non fonctionnels** ;
- `pip-audit .` sur les dépendances déclarées du projet : **aucune vulnérabilité connue** ;
- `pnpm --registry=https://registry.npmjs.org audit --prod --json` : **0 vulnérabilité** (3 dépendances de production) ;
- Bandit sur `backend/app` : **vert** ;
- detect-secrets avec `.secrets.baseline` : **vert** ;
- `scripts/simulate_staging_deploy.sh --static-only` et `--compose-config` : **verts**, sans démarrer de services ;
- simulation locale complète exécutée avec PostgreSQL, ClamAV, migration, backend, frontend, Caddy et workers ; le registre npm répond depuis l’hôte et un conteneur Docker, `pnpm install --frozen-lockfile` et `pnpm build` passent, la tête Alembic `20260920_0090` s’applique, et le smoke test HTTPS via Caddy retourne `200` avec `database=ok`, `schema=ok` et `clamav=ok` ; le port hôte 80 déjà occupé a été isolé par un override éphémère `18080/18443` ;
- le build a révélé puis corrigé un défaut réel du Dockerfile frontend : le chemin PID Nginx était réécrit avec un espacement trop strict et laissait `/run/nginx.pid` inaccessible à l’utilisateur non-root ; la réécriture tolère maintenant les espaces et cible `/tmp/nginx.pid` ;
- `scripts/simulate_preprod_local.sh` rejoue désormais cette qualification en une commande : build/start complet, smoke HTTPS, 20 puis 100 requêtes concurrentes, redémarrage backend/frontend/PostgreSQL et des trois workers, panne ClamAV visible puis récupération, backup PostgreSQL, restauration isolée de 127 tables à la tête `20260920_0090`, rotation JWT éphémère `0600` et nettoyage automatique ; exécution réussie à 151,52 req/s pour la passe de 100 requêtes sur le poste local ; ce chiffre ne vaut pas budget VPS ;
- `scripts/benchmark_dce_local.py` mesure séparément l’extraction native bornée sur texte, DOCX et XLSX ; médianes locales de 105,881 ms, 75,915 ms et 182,319 ms ; OCR, IA, DB, réseau, quarantaine et ingestion restent hors périmètre ;
- la qualification PostgreSQL DCE séparée passe 76 tests : ingestion/quarantaine (36), extraction/classification (22), exigences/persistance et routes authentifiées (18) ; preuve `SMART_AO_PHASE11_LOCAL_DCE_PIPELINE_QUALIFICATION_v0.1.md` ; analyse RC lourde, OCR, RAG et corpus PDF volumineux restent hors périmètre ;
- les parcours DCE lourds passent 68 tests PostgreSQL en 24,54 s : analyse RC, exigences lourdes et lecture DCE tenant-scoped, sourcées, atomiques et rejouables ; OCR, Docling, RAG et gros PDF restent hors périmètre dans `SMART_AO_PHASE11_LOCAL_DCE_HEAVY_PATHS_BENCHMARK_v0.1.md` ;
- la qualification optionnelle passe 9 tests avancés sans skip PIL après installation ; PyMuPDF traite une fixture PDF en 9,2 ms, Docling offline en 6 361,68 ms, RapidOCR en `REVIEW_REQUIRED` en 2 818,22 ms, et BGE produit un vecteur CPU de dimension 1 024 en environ 4 435 ms ; aucune indexation métier n’est lancée ;
- décision d’activation : les extras sont installés depuis `uv.lock`, le snapshot BGE `BAAI/bge-m3` est vérifié dans le cache local, mais OCR/Docling/RAG restent runtime désactivés ou `PARTIAL` sans fixtures, index non financier et budget mémoire mesuré ; détail dans `SMART_AO_PHASE11_OPTIONAL_DEPENDENCIES_DECISION_v0.1.md` ;
- exercice PostgreSQL local isolé : **PASS**, sauvegarde compressée puis restauration dans une seconde base temporaire, 127 tables, tête `20260920_0090` et trigger append-only vérifiés ;
- rotation JWT atomique avec environnement éphémère protégé : **PASS**, ancien fichier supprimé après simulation ;
- recherche de clés privées, tokens GitHub et secrets versionnés hors fixtures explicitement marquées : **aucun secret de production trouvé** ;
- uploads protégés, archives limitées, contenu hostile, antivirus fail-closed et quarantaine : couverts par les tests backend complets ;
- contrat d’autorité Product Freeze : **2 tests verts**, v1.0 actif et v0.4 archivé.

## Isolation et autorité

Les tests de sécurité couvrent tenant, membership, affectation, MFA, délégations, partage, confidentialité financière et refus Collaborateur. Les routes sensibles utilisent le contexte serveur et les classifications `FINANCIAL_PRIVATE`/`INTERNAL_OPERATIONAL`.

## Limites restant à traiter

- la restauration réelle d’une sauvegarde PostgreSQL et la rotation opérationnelle des secrets restent à exécuter dans l’environnement de préproduction ; l’exercice local isolé ne remplace pas cette preuve ;
- `ops/preflight-checklist.sh` refuse l’exécution sans `.env.preprod` et `SMART_AO_PUBLIC_HOST` réels ; cette absence de secrets/runtime est une limite de l’environnement local ;
- les deux skips PIL concernent l’option OCR avancée, pas le chemin nominal ;
- l’audit pnpm via le miroir `registry.npmmirror.com` reste indisponible, mais le même audit contre npm officiel est vert ;
- les vulnérabilités détectées dans l’environnement Python système global ne sont pas attribuées au projet : l’audit projet ciblé est celui de `pip-audit .`.

## Références

- `backend/tests/security/`
- `backend/tests/architecture/`
- `backend/app/platform/storage/quarantine.py`
- `backend/app/modules/dce/application/extraction.py`
- `backend/app/modules/knowledge/application/retrieval.py`
- `backend/tests/ops/test_product_freeze_authority_contract.py`
- `ops/docker/frontend.Dockerfile`
