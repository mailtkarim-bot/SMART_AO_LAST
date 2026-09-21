# SMART AO — Audit ancres et refus RAG temporaire v0.1

**Date :** 21 septembre 2026  
**Statut :** qualification temporaire — aucun index persistant

## Ancres

La qualification source-aware sur 116 fragments et trois requêtes retrouve les sources attendues dans le top 3 :

- échéance → RC ;
- prescriptions communes → CCTC ;
- planning → Planning.

Chaque résultat conserve le nom de source et le numéro de chunk. Le titre du document est ajouté uniquement à l’entrée d’embedding ; le texte et le locator source restent inchangés.

## Refus et confidentialité

Les tests de retrieval existants vérifient tenant, Case, version DCE, classification autorisée, exclusion des versions `SUPERSEDED` et exclusion des fragments `FINANCIAL_PRIVATE`. La copie redacted ne contient pas de fragment financier approuvé et aucun index permanent n’a été créé.

Une requête explicitement financière est maintenant refusée au service de retrieval lorsque le scope n’autorise pas `FINANCIAL_PRIVATE`, avec `FinancialRetrievalQueryRejected` et code `FINANCIAL_RETRIEVAL_SCOPE_REQUIRED`. Le moteur vectoriel ne transforme plus l’absence de fragment financier en réponse technique affirmative.

## Verdict

- ancres source-aware : **3/3** ; locators source/chunk complets ;
- isolation et classification : **couverte par les tests existants** ;
- fuite de marqueurs financiers dans les réponses : **0** ;
- refus financier hors scope privé : **REFUSED / FINANCIAL_RETRIEVAL_SCOPE_REQUIRED** ;
- index permanent : **non créé** ;
- index mémoire avant nettoyage : **116 entrées** ; après nettoyage : **0** ;
- refus financier explicite à la frontière applicative : **FERMÉ — 2 tests de contrat**.
