# SMART AO — Qualification OCR, Docling, RAG et gros PDF local v0.1

**Date :** 21 septembre 2026  
**Environnement :** `.venv` local, PostgreSQL Docker isolé, fixtures DCE bornées

## Résultat

- **38 tests passés** sur extraction avancée, limites PDF/DOCX/texte, stockage des projections OCR, service RAG, retrieval, benchmark manifest et extraction DCE ;
- **2 tests ignorés** faute de PIL, dépendance optionnelle OCR ;
- `docling`, `rapidocr`, `onnxruntime`, `sentence_transformers`, `pymupdf` et PIL sont maintenant installés dans `.venv` depuis `uv.lock` ; le snapshot BGE `BAAI/bge-m3` est présent et vérifié dans `/home/noor/.cache/smartao/models` ;
- le smoke test `scripts/smoke_document_advanced.py` passe avec PyMuPDF et l’adaptateur Docling importé ; aucun modèle Docling/OCR/RAG n’est téléchargé ;
- les limites PDF, DOCX, texte, archive compressée et extraction OCR en `REVIEW_REQUIRED` restent vérifiées par les tests disponibles.

## Interprétation

Le chemin natif borné, les imports optionnels, l’adaptateur PyMuPDF et la présence du cache BGE sont qualifiés. RapidOCR, Docling complet et les embeddings locaux restent installés mais non activés : ils nécessitent fixtures, index non financier et revue séparée avant mesure métier.

Ces résultats sont locaux et ne constituent pas un budget VPS, GPU, mémoire ou production.
