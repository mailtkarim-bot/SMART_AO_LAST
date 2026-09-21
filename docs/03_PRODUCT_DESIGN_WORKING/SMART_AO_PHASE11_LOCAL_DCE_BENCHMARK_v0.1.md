# SMART AO — Benchmark DCE local borné v0.1

**Date :** 21 septembre 2026  
**Environnement :** poste local, Python `.venv`, extraction déterministe native  
**Corpus :** synthétique, borné, sans donnée client ; trois itérations par format

## Périmètre

Le benchmark mesure uniquement la projection d’extraction native (`_project_document`) sur trois entrées représentatives. Il n’active ni OCR, ni Docling, ni RAG, ni PostgreSQL, ni antivirus, ni réseau. Les résultats caractérisent ce poste et ne sont pas un budget VPS.

| Format | Taille | Contenu borné | Fragments | Médiane | P95 | Statut |
|---|---:|---:|---:|---:|---:|---|
| Texte UTF-8 | 1,33 Mo | 20 000 lignes | 20 000 | 105,881 ms | 162,374 ms | COMPLETED |
| DOCX | 42,5 Ko | 2 000 paragraphes | 2 000 | 75,915 ms | 76,368 ms | COMPLETED |
| XLSX | 51,4 Ko | 3 feuilles × 200 × 20 cellules | 12 000 | 182,319 ms | 249,050 ms | COMPLETED |

## Limites

Ce benchmark ne mesure pas l’ingestion HTTP, la quarantaine ClamAV, l’écriture PostgreSQL, l’analyse RC, la matérialisation des exigences, les gros PDF, l’OCR ou les modèles IA. Il sert à détecter une régression locale simple avant d’activer ces couches plus coûteuses.

La commande reproductible est :

```bash
PYTHONPATH=backend ./.venv/bin/python scripts/benchmark_dce_local.py \
  --output /tmp/smartao-dce-benchmark.json --iterations 3
```

**Preuve :** `scripts/benchmark_dce_local.py`, sortie JSON locale non versionnée.

