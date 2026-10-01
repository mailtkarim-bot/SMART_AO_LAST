# SMART AO — EXP-03 — Classification et synthèse DCE — preuve verticale v0.1

**Statut : PREUVE VERTICALE EXÉCUTÉE · SYNTHÈSE PARTIELLE EXPLICITE**  
**Autorité :** cahier produit/métier OWNER_CONSOLIDATED v0.4  
**Périmètre :** classification documentaire déterministe et projection de lecture Case-scoped

## Décision de tranche

Une synthèse DCE n’est exploitable que si son état de classification est visible et si ses sources restent traçables. Elle ne doit jamais être présentée comme complète lorsque des documents sont `NOT_EXTRACTED`, `UNCLASSIFIED`, `REVIEW_REQUIRED`, protégés, non supportés ou rejetés par une limite.

Le code existant suffit pour cette preuve. Aucun modèle de score opaque, registre parallèle, appel LLM ou dépendance supplémentaire n’est introduit.

## Contrat prouvé

1. Le service charge uniquement une version `ADMITTED` ou `SUPERSEDED` dont l’intégrité est `VERIFIED`, dans le tenant demandé.
2. Chaque document est classé à partir de fragments d’extraction terminaux et immuables. Les règles lexicales sont versionnées (`smart-ao-document-rules`, version `1`).
3. Une correspondance unique produit `CLASSIFIED` avec une preuve limitée : identifiant de fragment, règle, offsets UTF-8 et extrait borné. L’extrait est vérifié contre le fragment avant persistance.
4. Une absence de fragment produit `NOT_EXTRACTED`; aucun document n’est alors silencieusement considéré comme lu. Une absence de signal produit `UNCLASSIFIED`. Des familles concurrentes à score égal produisent `REVIEW_REQUIRED`.
5. Le manifeste des fragments, l’identité du classifieur et sa version forment la clé de rejeu. Un rejeu identique retourne le reçu existant sans nouvelle ligne mutable.
6. La readiness de version devient `CLASSIFIED`, `PARTIALLY_CLASSIFIED` ou `UNCLASSIFIED` selon les résultats. La lecture Case conserve aussi les compteurs de confirmation humaine et les exigences à revoir.
7. L’interface affiche explicitement les états de classification et d’analyse. Tant que la classification n’est pas `CLASSIFIED`, elle affiche que la synthèse reste partielle et que les pièces à revoir restent visibles.

## Projection utilisateur

La lecture DCE reste Case-scoped et ne renvoie ni texte intégral, ni chemin de stockage, ni détails d’audit. Elle expose la version, son intégrité, la fraîcheur, les compteurs d’exigences et les localisations de source. La recherche knowledge renvoie un fragment et son locator, jamais le contenu original.

Le panneau `DceKnowledgePanel` montre maintenant la readiness `classification_readiness` et `analysis_readiness`. Toute valeur différente de `CLASSIFIED` déclenche le message de synthèse partielle. Les documents non lus restent consultables par l’inventaire par fichier EXP-03.

## Limites assumées

- Le classifieur v0 repose sur des règles lexicales déterministes : il signale l’incertitude mais ne tranche pas un document concurrent.
- OCR, archives imbriquées, anciens formats et validation terrain restent optionnels ou hors preuve native.
- La synthèse métier complète, les décisions humaines et l’analyse RC viennent après la classification ; elles ne sont pas déduites ici.

## Vérification exécutée

- `backend/tests/application/test_dce_document_classification.py` : **9 tests passés** contre PostgreSQL Docker dédié.
- Cas couverts : sources et preuves immuables, rejeu idempotent, absence de signal, familles concurrentes, `NOT_EXTRACTED`, limites, manifeste, offsets, acteur système et historique après nouvelle extraction.
- `web/src/features/dce/DceKnowledgePanel.test.tsx` : **4 tests passés**, dont l’affichage explicite de `PARTIALLY_CLASSIFIED`.
- Ruff ciblé, `npm run typecheck`, `npm run lint`, `npm run build` et `git diff --check` passent après la modification d’interface.

## Fichiers de preuve

- `backend/app/modules/dce/application/classification.py`
- `backend/app/modules/dce/application/handlers.py`
- `backend/app/modules/dce/infrastructure/case_dce_reading_reader.py`
- `backend/app/interfaces/http/routes/case_dce_reading.py`
- `web/src/features/dce/DceKnowledgePanel.tsx`
- `backend/tests/application/test_dce_document_classification.py`
- `web/src/features/dce/DceKnowledgePanel.test.tsx`

## Étape suivante

Auditer les rectificatifs DCE et invalider uniquement les conclusions qui dépendent de la version remplacée, sans effacer l’historique.
