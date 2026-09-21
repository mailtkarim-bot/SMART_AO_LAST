# SMART AO — Qualification OCR, Docling, RAG et gros PDF local v0.1

**Date :** 21 septembre 2026  
**Environnement :** `.venv` local, PostgreSQL Docker isolé, fixtures DCE bornées

## Résultat

- **38 tests passés** sur extraction avancée, limites PDF/DOCX/texte, stockage des projections OCR, service RAG, retrieval, benchmark manifest et extraction DCE ;
- **2 tests ignorés** faute de PIL, dépendance optionnelle OCR ;
- `docling`, `rapidocr`, `onnxruntime`, `sentence_transformers`, `pymupdf` et PIL sont maintenant installés dans `.venv` depuis `uv.lock` ; le snapshot BGE `BAAI/bge-m3` est présent et vérifié dans `/home/noor/.cache/smartao/models` ;
- fixture PDF locale : PyMuPDF termine `COMPLETED` en 9,2 ms avec 2 fragments sourcés ;
- Docling est importable mais la conversion réelle reste `NOT_CONFIGURED` : ses modèles layout/vision ne sont pas présents dans le cache local et le téléchargement Hugging Face a échoué par résolution DNS ;
- RapidOCR est importable mais l’adaptateur applicatif refuse honnêtement l’exécution sans chemins de modèles locaux (`OCR_MODELS_REQUIRED`) ;
- les limites PDF, DOCX, texte, archive compressée et extraction OCR en `REVIEW_REQUIRED` restent vérifiées par les tests disponibles.

## Interprétation

Le chemin natif borné, les imports optionnels, l’adaptateur PyMuPDF et la présence du cache BGE sont qualifiés. Docling complet reste bloqué par ses artefacts de modèles, RapidOCR par l’absence de chemins de modèles dédiés, et l’embedding BGE CPU n’est pas forcé sur ce poste à faible mémoire disponible. Aucun de ces états ne devient un succès implicite.

Ces résultats sont locaux et ne constituent pas un budget VPS, GPU, mémoire ou production.
