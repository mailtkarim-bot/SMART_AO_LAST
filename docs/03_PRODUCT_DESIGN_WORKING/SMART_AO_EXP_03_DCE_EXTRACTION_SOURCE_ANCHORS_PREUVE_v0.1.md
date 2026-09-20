# SMART AO — EXP-03 — Extraction multiformat et ancres de source

**Date :** 15 septembre 2026  
**Statut :** PREUVE VERTICALE EXÉCUTÉE · PÉRIMÈTRE NATIF V0  
**Autorité :** cahier OWNER produit/métier v0.4, contrat UX OWNER v0.3, code vivant et tests exécutés

## 1. Contrat prouvé

Une extraction lit uniquement un original DCE déjà admis, vérifié et consommé par une version. Elle contrôle à nouveau la taille et le SHA-256, produit des fragments bornés avec un locator déterministe, puis enregistre une projection immuable et rejouable. Une erreur, une limite ou un format non pris en charge produit un état explicite sans fragment ; elle ne devient jamais une lecture réussie.

La reprise d’une extraction réutilise l’identité déterministe `(document, hash, extracteur, version)`. Le rejeu retourne le reçu existant sans seconde extraction persistée ni nouvel événement métier.

## 2. Formats et ancres natives

| Format | Traitement V0 | Ancre exposée | Limite honnête |
|---|---|---|---|
| PDF texte | `pypdf` | `pdf_page` + numéro de page + part | PDF chiffré `DOCUMENT_PROTECTED`, scan illisible `FAILED_SAFE` |
| DOCX | `python-docx` après contrôle ZIP décompressé | `docx_paragraph` + paragraphe + part | fonctionnalités complexes et protection non promises |
| XLSX | `openpyxl` en lecture seule | `xlsx_cell` + feuille + cellule + part | formules/objets non interprétés comme preuve métier |
| texte brut | lecture bornée | `text_line` + ligne + part | encodage et volume bornés |
| image/PDF scanné | adaptateur OCR avancé optionnel | `ocr_page` + ordre et bbox si moteur configuré | aucune promesse si modèles/runtime absents ; `REVIEW_REQUIRED` |
| DOC/XLS/ODT/archives | conservés au niveau admission si type autorisé | pas d’ancre native V0 | `UNSUPPORTED` ou traitement avancé explicitement configuré |

Aucune page, cellule ou zone n’est déduite à partir d’un simple offset. Les futures ancres A2/A3 pourront ajouter des types génériques sans réécrire les fragments existants.

## 3. États visibles

- `RECEIVED` : original admis, extraction non encore exécutée ;
- `READ` : fragments déterministes enregistrés ;
- `REVIEW_REQUIRED` : fragments disponibles mais revue humaine obligatoire ;
- `UNSUPPORTED` : format ou capacité non couverte ;
- `LIMIT_REACHED` : limite de taille, pages, feuilles, lignes ou décompression atteinte ;
- `PROTECTED` : protection détectée, notamment PDF chiffré ;
- `UNREADABLE` : original absent, intégrité divergente ou parseur en échec.

L’inventaire `GET /api/v1/dce-versions/{id}/documents` restitue ces états et le motif `issue_code` sans chemin privé, octet original ni contenu extrait.

## 4. Preuves exécutées

- projection PDF avec page et part ;
- projection DOCX avec paragraphe ;
- projection XLSX avec feuille/cellule/part ;
- projection texte avec lignes ;
- PDF protégé signalé sans extraction ;
- limites PDF/texte/DOCX refusées sans fragments ;
- extraction persistée, immuable et rejouée sans fuite d’outbox ;
- stockage d’un résultat OCR `REVIEW_REQUIRED` et rejeu déterministe ;
- contrôle tenant, version admise, intégrité et hash d’entrée côté handler.

**Résultat : 13 tests d’extraction passent sur PostgreSQL dédié**, dont le contrôle d'instruction hostile décrit dans la preuve IA/manuelle.

## 5. Décisions et travail volontairement parqué

Aucune bibliothèque supplémentaire n’est ajoutée. Docling, PyMuPDF et RapidOCR restent des adaptateurs optionnels déjà présents ; ils ne sont pas invoqués depuis une route HTTP et leur absence reste visible. L’inventaire multi-fichiers, les archives imbriquées, les formats historiques DOC/XLS, le graphe `SourceAnchor` générique, la classification et l’orchestration de jobs viennent après la preuve de lecture native.

## 6. Prochaine étape unique

Après la preuve IA/manuelle, parcourir les rôles, refus et scénarios Golden DCE avant la revue et le gel d’expérience EXP-03.
