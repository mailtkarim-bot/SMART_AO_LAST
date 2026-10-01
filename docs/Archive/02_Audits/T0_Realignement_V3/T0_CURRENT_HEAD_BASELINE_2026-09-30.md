# T0 — Baseline au HEAD commité

**Date :** 30 septembre 2026  
**SHA :** `1c8ac62fcddc78d2b156f70df9f0b130910cc918`  
**Branche d’audit :** `feat/ccap-cctp-risk-register-20260831`  
**Verdict T0 : `PARTIAL` — le full backend n’a pas reçu de résultat final exploitable dans cette passe.**

## Périmètre

Les commandes backend ont tourné dans un clone temporaire `/tmp/smartao-t0-head-1c8ac62`, checkout exact du commit ci-dessus. `.venv` et `web/node_modules` étaient des liens vers les dépendances déjà installées du dépôt. PostgreSQL était épinglé à l’image `postgres:16-alpine` du projet, sans volume persistant. Le clone et ses résultats n’intègrent pas les fichiers locaux non commités du checkout source.

## Frontend — résultat complet

Commandes exécutées dans ce clone :

- `pnpm exec vitest run --maxWorkers=1` : **258 tests verts** ;
- `pnpm run typecheck` : vert ;
- `pnpm run lint` : vert ;
- `pnpm run build` : vert, bundle principal `493,39 kB`.

## Backend — tentatives non concluantes

Commande des deux tentatives :

```bash
env -u SMART_AO_DATABASE_URL \
  SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:55433/smart_ao_v8_test' \
  ./.venv/bin/pytest backend/tests -q --tb=short
```

La première tentative a utilisé `--tmpfs /var/lib/postgresql/data:...:size=1g` au port 55433. Pour la seconde, le port était 55435, tmpfs `size=2g`, avec `max_wal_size=256MB`, `min_wal_size=64MB`, `checkpoint_timeout=2min`, `synchronous_commit=off`, `fsync=off`. Le conteneur a été supprimé automatiquement à l’interruption.

1. PostgreSQL jetable avec données en tmpfs 1 Gio : **1 795 passed, 135 errors en 458,90 s**. Un traceback capturé est `psycopg.errors.DiskFull: could not write to file "pg_wal/xlogtemp...": No space left on device`; les migrations PostgreSQL n’ont donc pas pu se terminer correctement. Ce run ne démontre pas de régression de code et ne compte pas comme full backend valide.
2. PostgreSQL jetable en tmpfs 2 Gio avec `max_wal_size=256MB`, `synchronous_commit=off`, `fsync=off` : interruption utilisateur pendant l’exécution après **140 passed en 54,61 s**. La sortie est `KeyboardInterrupt`; aucun verdict complet.

Le plan opérationnel versionné au HEAD consigne un run antérieur **1 930/1 930 backend** et le même **258/258 frontend** pour PUX-19. Le frontend a été confirmé de nouveau ici ; le backend versionné reste un élément d’historique, pas un résultat répété indépendamment dans ce T0.

## Gaps de validation

- backend complet au SHA exact : `UNCONFIRMED` dans cette passe ;
- upgrade/downgrade globalement terminé sur base fraîche : pas de verdict séparé ;
- lint/typecheck/build frontend : verts ;
- code modifié non commité du checkout source : hors du périmètre de ce baseline ;
- aucune promotion V3 ni modification production n’a été faite.

**Conclusion :** ne qualifier ce HEAD ni `RED` ni `GREEN` sur le backend à partir de ces exécutions. La prochaine qualification backend doit utiliser un PostgreSQL isolé avec stockage/WAL suffisants et finir jusqu’au résumé pytest complet.
