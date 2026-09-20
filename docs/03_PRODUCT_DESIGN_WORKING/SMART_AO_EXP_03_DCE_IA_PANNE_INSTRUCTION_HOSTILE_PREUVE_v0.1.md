# SMART AO — EXP-03 — Panne IA et instruction hostile — preuve verticale v0.1

**Statut : PREUVE VERTICALE EXÉCUTÉE · VOIE MANUELLE CONSERVÉE**  
**Autorité :** cahier produit/métier OWNER_CONSOLIDATED v0.4  
**Périmètre :** indisponibilité de l'assistance IA, contenu importé hostile et poursuite humaine sûre

## Décision de tranche

L'assistance IA reste optionnelle et ne devient jamais une condition d'accès au DCE. Une panne de récupération rend l'échec visible puis conserve la lecture des sources, l'inventaire, les ancres et les contrôles manuels. Aucun texte provenant d'un document ne peut être interprété comme une instruction d'exécution.

Le code existant est réutilisé : l'indexation locale BGE reste désactivée par défaut et exige deux indicateurs explicites ; la récupération renvoie des extraits et leurs localisateurs, sans action externe, mutation de rôle, décision financière ou envoi autonome.

## Contrat prouvé

1. `BgeEmbeddingProvider` charge le modèle de façon paresseuse, avec `local_files_only=True` par défaut. L'absence de la dépendance optionnelle ou du modèle local produit une erreur contrôlable.
2. Le worker d'indexation refuse de démarrer tant que `SMART_AO_RAG_ENABLED` et `SMART_AO_RAG_INDEXING_ENABLED` ne sont pas activés explicitement. Une panne n'est donc pas masquée par un fallback implicite.
3. La route de recherche mappe `RuntimeError` vers `503 KNOWLEDGE_RETRIEVAL_UNAVAILABLE`. Le hook front vide les résultats et affiche : « Assistance IA indisponible. La lecture des sources et les contrôles manuels restent disponibles. »
4. L'extraction native inspecte le texte des fragments avec trois familles de motifs : ignorer les consignes précédentes, révéler un secret ou une donnée sensible, et envoyer vers une URL/webhook. Un motif force `REVIEW_REQUIRED` avec `HOSTILE_INSTRUCTION_REVIEW_REQUIRED` ; les fragments sont conservés pour revue et aucun appel n'est déclenché.
5. Les autres documents de l'import ne sont pas bloqués par un texte hostile isolé. Leur état et leurs ancres restent visibles dans l'inventaire ; la synthèse ne peut pas présenter le DCE comme entièrement classifié tant que la revue n'est pas faite.

## Poursuite manuelle

Après une panne IA ou un document à revoir, l'utilisateur peut continuer par les surfaces déjà prouvées :

- consulter l'inventaire par fichier et ses états (`READ`, `REVIEW_REQUIRED`, `PROTECTED`, `UNREADABLE`, etc.) ;
- ouvrir les fragments natifs et leurs ancres page, paragraphe, feuille/cellule ou ligne ;
- confirmer ou corriger manuellement une exigence classifiée ;
- rechercher une source lorsque la récupération est disponible, sans supposer qu'un résultat absent est une preuve d'absence ;
- enregistrer un rectificatif et reprendre l'impact ciblé sans écraser l'historique.

La reprise ne relance pas automatiquement un fournisseur et ne déduit pas de succès à partir d'un timeout. Toute action externe, décision métier ou élévation de droit reste hors de cette tranche.

## Limites assumées

- Le détecteur d'instruction hostile est une heuristique déterministe, non une garantie exhaustive ; les documents ambigus exigent une revue humaine.
- Aucun modèle LLM distant, OCR ou synthèse générative n'est ajouté avant une preuve dédiée et un budget de coût explicite.
- La voie manuelle prouve la continuité d'accès aux sources, pas la validation automatique du contenu ni la complétude du DCE.
- Les rôles, refus et scénarios Golden DCE restent à parcourir avant le gel d'expérience EXP-03.

## Vérification exécutée

- `backend/tests/application/test_dce_document_extraction.py` : **13 tests passés** contre PostgreSQL Docker dédié, dont le cas hostile.
- `backend/tests/application/test_advanced_extraction.py tests/application/test_knowledge_retrieval.py tests/application/test_knowledge_service.py tests/application/test_knowledge_worker.py` : **30 tests passés, 2 tests image ignorés** faute de `PIL` optionnel.
- `web/src/features/dce/DceKnowledgePanel.test.tsx web/src/features/dce/useDceKnowledge.test.tsx` : **9 tests passés**.
- Ruff ciblé, TypeScript et lint front : passent.

## Fichiers de preuve

- `backend/app/modules/dce/application/extraction.py`
- `backend/app/modules/knowledge/infrastructure/bge_embeddings.py`
- `backend/app/workers/knowledge_embeddings.py`
- `backend/app/interfaces/http/routes/knowledge.py`
- `web/src/features/dce/useDceKnowledge.ts`
- `backend/tests/application/test_dce_document_extraction.py`
- `backend/tests/application/test_knowledge_worker.py`
- `web/src/features/dce/useDceKnowledge.test.tsx`

## Étape suivante

Auditer les rôles et refus DCE, parcourir les scénarios Golden DCE, puis préparer la revue et le gel d'expérience EXP-03.
