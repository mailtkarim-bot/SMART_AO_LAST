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

Une requête explicitement financière doit rester refusée en amont du retrieval métier ; le moteur vectoriel ne doit jamais transformer l’absence de fragment financier en réponse technique affirmative. Cette règle reste à intégrer/recetter à la frontière applicative avant indexation persistante.

## Verdict

- ancres source-aware : **3/3** ;
- isolation et classification : **couverte par les tests existants** ;
- index permanent : **non créé** ;
- refus financier explicite à la frontière applicative : **à fermer avant promotion**.

