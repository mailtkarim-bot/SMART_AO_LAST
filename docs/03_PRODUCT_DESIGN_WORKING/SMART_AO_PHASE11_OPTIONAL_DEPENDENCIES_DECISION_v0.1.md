# SMART AO — Décision d’activation OCR / Docling / RAG v0.1

**Date :** 21 septembre 2026  
**Statut :** ACCEPTÉ — activation différée

## Décision

Les extras `document-ocr`, `document-advanced` et `rag` restent désactivés dans la préproduction locale actuelle. Aucun modèle OCR, BGE ou artefact Docling n’est téléchargé pour cette phase.

## Pourquoi

Le chemin natif PDF/DOCX/XLSX/texte est déjà qualifié. Les dépendances optionnelles sont absentes du `.venv`, aucun corpus approuvé ni modèle local vérifié n’est disponible, et le poste ne dispose que d’environ 1,4 Gio de RAM libre. Les activer maintenant augmenterait la surface et le coût mémoire sans produire une mesure comparable.

Le contrat d’exploitation impose déjà `SMART_AO_RAG_ENABLED=0`, `SMART_AO_RAG_INDEXING_ENABLED=0`, `SMART_AO_OCR_ENABLED=0` et les fichiers locaux uniquement. Cette décision conserve donc le comportement actuel.

## Statut par option

| Option | Décision | Condition de réouverture |
|---|---|---|
| OCR / RapidOCR | DIFFÉRÉ | modèles ONNX vérifiés, corpus OCR approuvé, budget mémoire mesuré |
| Docling / PyMuPDF | DIFFÉRÉ | besoin métier démontré, corpus multiformat approuvé, mesure locale isolée |
| RAG / sentence-transformers | DIFFÉRÉ | modèle BGE local préchargé, index non financier vérifié, benchmark et mémoire acceptés |

## Conséquence

Le chemin natif reste la preuve active. Les options sont `NOT_CONFIGURED` ou `PARTIAL` et ne doivent pas être présentées comme disponibles. Une future activation devra être additive, versionnée, mesurée localement, puis approuvée avant préproduction.

