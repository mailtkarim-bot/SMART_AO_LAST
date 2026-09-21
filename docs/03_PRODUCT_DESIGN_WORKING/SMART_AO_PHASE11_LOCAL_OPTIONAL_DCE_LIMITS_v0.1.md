# SMART AO — Qualification OCR, Docling, RAG et gros PDF local v0.1

**Date :** 21 septembre 2026  
**Environnement :** `.venv` local, PostgreSQL Docker isolé, fixtures DCE bornées

## Résultat

- **38 tests passés** sur extraction avancée, limites PDF/DOCX/texte, stockage des projections OCR, service RAG, retrieval, benchmark manifest et extraction DCE ;
- **2 tests ignorés** faute de PIL, dépendance optionnelle OCR ;
- `docling`, `rapidocr_onnxruntime`, `onnxruntime`, `sentence_transformers` et `pymupdf` ne sont pas installés dans `.venv` ;
- le smoke test `scripts/smoke_document_advanced.py` est donc explicitement `NOT_CONFIGURED` dans cet environnement, pas un échec du chemin natif ;
- les limites PDF, DOCX, texte, archive compressée et extraction OCR en `REVIEW_REQUIRED` restent vérifiées par les tests disponibles.

## Interprétation

Le chemin natif borné et les garde-fous d’activation optionnelle sont qualifiés. Les adaptateurs Docling, RapidOCR, les embeddings locaux et le parsing PDF avancé ne sont pas activés implicitement et nécessitent une installation/revue séparée avant mesure.

Ces résultats sont locaux et ne constituent pas un budget VPS, GPU, mémoire ou production.

