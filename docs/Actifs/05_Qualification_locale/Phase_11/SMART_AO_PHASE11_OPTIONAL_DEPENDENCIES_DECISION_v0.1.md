# SMART AO — Décision d’activation OCR / Docling / RAG v0.1

**Date :** 21 septembre 2026  
**Statut :** ACCEPTÉ — dépendances installées, runtime contrôlé

## Décision

Les extras `document-ocr`, `document-advanced` et `rag` sont installés dans `.venv` depuis `uv.lock`. Les artefacts Docling layout et RapidOCR sont présents localement, le modèle `BAAI/bge-m3` est dans `/home/noor/.cache/smartao/models`, et les trois chemins ont été mesurés sur fixtures locales. Les flags runtime restent désactivés dans la préproduction ; aucun index RAG n’est lancé.

## Pourquoi

Le chemin natif PDF/DOCX/XLSX/texte est déjà qualifié. L’installation des paquets permet désormais de vérifier les imports et les adaptateurs sans activer de modèle ni de flux externe. Aucun corpus approuvé ni modèle local vérifié n’est encore disponible, et le poste ne dispose que d’environ 1,4 Gio de RAM libre.

Le contrat d’exploitation impose déjà `SMART_AO_RAG_ENABLED=0`, `SMART_AO_RAG_INDEXING_ENABLED=0`, `SMART_AO_OCR_ENABLED=0` et les fichiers locaux uniquement. Cette décision conserve donc le comportement actuel.

## Statut par option

| Option | Décision | Condition de réouverture |
|---|---|---|
| OCR / RapidOCR | INSTALLÉ — fixture mesurée, runtime désactivé | corpus OCR approuvé et budget mémoire confirmé |
| Docling / PyMuPDF | INSTALLÉ — fixture mesurée, runtime désactivé | besoin métier et corpus multiformat approuvés |
| RAG / sentence-transformers | INSTALLÉ — embedding isolé, runtime désactivé | index non financier vérifié, corpus et budget mémoire acceptés |

## Conséquence

Le chemin natif reste la preuve active. Les paquets et le cache BGE sont disponibles pour les tests locaux, mais les options restent `NOT_CONFIGURED` ou `PARTIAL` tant que les modèles OCR/Docling, l’index non financier et le budget mémoire ne sont pas approuvés. Une activation devra être additive, versionnée, mesurée localement, puis approuvée avant préproduction.
