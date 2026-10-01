# SMART AO — Qualification OCR, Docling, RAG et gros PDF local v0.1

**Date :** 21 septembre 2026  
**Environnement :** `.venv` local, PostgreSQL Docker isolé, fixtures DCE bornées

## Résultat

- **38 tests passés** sur extraction avancée, limites PDF/DOCX/texte, stockage des projections OCR, service RAG, retrieval, benchmark manifest et extraction DCE ;
- **2 tests ignorés** faute de PIL, dépendance optionnelle OCR ;
- `docling`, `rapidocr`, `onnxruntime`, `sentence_transformers`, `pymupdf` et PIL sont maintenant installés dans `.venv` depuis `uv.lock` ; le snapshot BGE `BAAI/bge-m3` est présent et vérifié dans `/home/noor/.cache/smartao/models` ;
- fixture PDF locale : PyMuPDF termine `COMPLETED` en 9,2 ms avec 2 fragments sourcés ;
- Docling exécute maintenant la conversion locale offline en `COMPLETED` en 6 361,68 ms sur la fixture PDF, avec 61 caractères Markdown ;
- RapidOCR exécute la fixture PNG avec les modèles fournis par le paquet, retourne `REVIEW_REQUIRED` avec 1 fragment en 2 818,22 ms ;
- BGE `BAAI/bge-m3` produit un embedding CPU offline de dimension 1 024 en environ 4 435 ms, sans indexation ni accès base ;
- les limites PDF, DOCX, texte, archive compressée et extraction OCR en `REVIEW_REQUIRED` restent vérifiées par les tests disponibles.

## Interprétation

Le chemin natif borné, les imports optionnels, les artefacts Docling/RapidOCR et l’embedding BGE isolé sont qualifiés. Les temps sont des repères de premier chargement sur ce poste et ne valent pas budget VPS. Aucun index métier n’a été écrit.

Ces résultats sont locaux et ne constituent pas un budget VPS, GPU, mémoire ou production.
