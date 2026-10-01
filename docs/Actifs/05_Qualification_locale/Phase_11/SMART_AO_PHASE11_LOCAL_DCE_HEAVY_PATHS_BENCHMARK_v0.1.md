# SMART AO — Mesure des parcours DCE lourds local v0.1

**Date :** 21 septembre 2026  
**Environnement :** PostgreSQL Docker isolé, migrations Alembic fraîches, `.venv` local  
**Corpus :** fixtures DCE locales bornées et anonymisées

## Résultat

| Parcours | Couverture | Résultat |
|---|---|---:|
| Analyse RC | sources, règles, taxonomie CCAP/CCTP, limites, rejeu et absence de fuite de texte | inclus dans 68 tests |
| Exigences lourdes | préconditions, manifeste, projection, atomicité, provenance et rejeu | inclus dans 68 tests |
| Lecture DCE | projection Case, tenant-scope, lecture déterministe, routes et états absents | inclus dans 68 tests |

La suite complète passe **68 tests en 24,54 s**, avec 3 avertissements Starlette/httpx non fonctionnels. Les durées de préparation les plus élevées restent autour de 3 secondes par module, principalement liées à la création du schéma PostgreSQL de test.

## Ce que cette preuve établit

Les flux RC → exigences → lecture DCE restent sourcés, tenant-scoped, déterministes et rejouables. Les limites et états absents ne produisent pas de succès implicite ; les tests de fuite de texte et de source injectée restent refusés.

## Limites

Cette mesure ne couvre pas OCR réel, Docling, RAG, gros PDF, corpus multi-affaires, débit disque ou budget VPS. Elle mesure la logique applicative et la persistance sur des fixtures bornées locales.

