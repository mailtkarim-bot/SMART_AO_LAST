# SMART AO — Verdict RAG local Phase 11 v0.1

**Date :** 21 septembre 2026  
**Statut :** QUALIFIÉ POUR EXPÉRIMENTATION LOCALE — PAS DE PRODUCTION

## Verdict

Le chemin RAG local est qualifié pour une expérimentation temporaire sur la copie DCE `redacted` approuvée : les fragments sont tenant-scoped, source-aware, non financiers, rejouables et supprimés après la passe. L’indexation persistante et l’activation préproduction restent désactivées.

## Preuves

- 116 fragments redacted encodés avec BGE `BAAI/bge-m3`, dimension 1 024 ;
- RC, CCTC et Planning retrouvés dans le top 3 après ajout du titre source dans l’entrée d’embedding ;
- locators `source/chunk` complets ;
- zéro marqueur financier dans les réponses auditées ;
- requête financière hors scope refusée par `FINANCIAL_RETRIEVAL_SCOPE_REQUIRED` ;
- 116 entrées mémoire avant nettoyage, 0 après nettoyage ;
- zéro écriture PostgreSQL et aucun index permanent.

## Limites

Les mesures incluent le premier chargement CPU du modèle et ne constituent pas un budget VPS. Le corpus reste une copie de travail anonymisée dont les droits et l’absence d’identité implicite doivent rester surveillés. Aucun index métier durable, worker RAG permanent ou activation des flags de préproduction n’est autorisé par ce verdict.

## Décision d’exploitation

Conserver `SMART_AO_RAG_ENABLED=0` et `SMART_AO_RAG_INDEXING_ENABLED=0`. Toute promotion doit produire une nouvelle décision avec corpus approuvé, index non financier vérifié, budget mémoire, contrôle des ancres, refus financiers et procédure de suppression/rollback.

