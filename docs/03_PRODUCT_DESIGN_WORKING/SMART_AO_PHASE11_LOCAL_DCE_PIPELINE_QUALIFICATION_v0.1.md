# SMART AO — Qualification pipeline DCE local v0.1

**Date :** 21 septembre 2026  
**Environnement :** PostgreSQL Docker isolé, migrations Alembic fraîches, `.venv` local  
**Corpus :** fixtures DCE bornées et anonymisées déjà présentes dans les tests ; aucune donnée client

## Tranches exécutées

| Tranche | Couverture | Résultat | Durée |
|---|---|---:|---:|
| Ingestion / quarantaine | staging privé, upload, limites incrémentales, interruption, suppression du partiel, scan, routes | **36 tests passés** | 22,73 s |
| Extraction / classification | extraction texte/PDF/DOCX/XLSX, ancres, limites, fichiers protégés, classification et historique | **22 tests passés** | 25,12 s |
| Exigences / persistance | exigences DCE, admission, routes authentifiées, refus tenant, absence d’effets durables | **18 tests passés** | 22,06 s |

Total : **76 tests passés**, 4 avertissements Starlette/httpx non fonctionnels. La tête Alembic est appliquée et chaque module nettoie son schéma après exécution.

## Ce que cette preuve établit

Le chemin local ingestion → quarantaine → extraction/classification → exigences/persistance est rejouable sur PostgreSQL isolé. Les limites de taille, le fichier protégé, l’écriture partielle, l’instruction hostile et les refus d’autorisation restent visibles sans succès implicite.

## Limites

La qualification ne mesure pas encore l’analyse RC lourde, l’OCR, Docling, RAG, un corpus PDF volumineux, le débit disque ou une charge multi-worker. Elle ne remplace pas une mesure VPS et n’utilise aucune donnée DCE réelle.

Commande représentative :

```bash
SMART_AO_TEST_DATABASE_URL='postgresql+psycopg://smart_ao:smart_ao@127.0.0.1:5433/smart_ao' \
PYTHONPATH=backend ./.venv/bin/pytest -q --durations=15 \
  backend/tests/application/test_dce_staging.py \
  backend/tests/application/test_dce_upload.py \
  backend/tests/application/test_dce_document_extraction.py \
  backend/tests/application/test_dce_document_classification.py \
  backend/tests/application/test_dce_requirements_worker.py \
  backend/tests/api/test_dce_staging_routes.py \
  backend/tests/api/test_dce_authenticated_api.py
```

