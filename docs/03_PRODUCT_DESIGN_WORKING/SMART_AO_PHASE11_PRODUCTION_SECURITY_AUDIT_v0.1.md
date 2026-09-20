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
- recherche de clés privées, tokens GitHub et secrets versionnés hors fixtures explicitement marquées : **aucun secret de production trouvé** ;
- uploads protégés, archives limitées, contenu hostile, antivirus fail-closed et quarantaine : couverts par les tests backend complets ;
- contrat d’autorité Product Freeze : **2 tests verts**, v1.0 actif et v0.4 archivé.

## Isolation et autorité

Les tests de sécurité couvrent tenant, membership, affectation, MFA, délégations, partage, confidentialité financière et refus Collaborateur. Les routes sensibles utilisent le contexte serveur et les classifications `FINANCIAL_PRIVATE`/`INTERNAL_OPERATIONAL`.

## Limites restant à traiter

- la restauration réelle d’une sauvegarde PostgreSQL et la rotation opérationnelle des secrets doivent encore être exécutées dans l’environnement de préproduction ;
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
