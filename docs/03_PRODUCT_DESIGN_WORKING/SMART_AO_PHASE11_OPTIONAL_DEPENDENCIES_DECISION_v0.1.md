# SMART AO — Décision d’activation OCR / Docling / RAG v0.1

**Date :** 21 septembre 2026  
**Statut :** ACCEPTÉ — dépendances installées, runtime contrôlé

## Décision

Les extras `document-ocr`, `document-advanced` et `rag` sont maintenant installés dans `.venv` depuis `uv.lock`. Les flags runtime restent désactivés dans la préproduction et aucun modèle OCR, BGE ou artefact Docling n’est téléchargé.

## Pourquoi

Le chemin natif PDF/DOCX/XLSX/texte est déjà qualifié. L’installation des paquets permet désormais de vérifier les imports et les adaptateurs sans activer de modèle ni de flux externe. Aucun corpus approuvé ni modèle local vérifié n’est encore disponible, et le poste ne dispose que d’environ 1,4 Gio de RAM libre.

Le contrat d’exploitation impose déjà `SMART_AO_RAG_ENABLED=0`, `SMART_AO_RAG_INDEXING_ENABLED=0`, `SMART_AO_OCR_ENABLED=0` et les fichiers locaux uniquement. Cette décision conserve donc le comportement actuel.

## Statut par option

| Option | Décision | Condition de réouverture |
|---|---|---|
| OCR / RapidOCR | INSTALLÉ — runtime désactivé | modèles ONNX vérifiés, corpus OCR approuvé, budget mémoire mesuré |
| Docling / PyMuPDF | INSTALLÉ — runtime désactivé | besoin métier démontré, corpus multiformat approuvé, mesure locale isolée |
| RAG / sentence-transformers | INSTALLÉ — modèle absent | modèle BGE local préchargé, index non financier vérifié, benchmark et mémoire acceptés |

## Conséquence

Le chemin natif reste la preuve active. Les paquets sont disponibles pour les tests locaux, mais les options restent `NOT_CONFIGURED` ou `PARTIAL` tant que les modèles et flags runtime ne sont pas approuvés. Une activation devra être additive, versionnée, mesurée localement, puis approuvée avant préproduction.
