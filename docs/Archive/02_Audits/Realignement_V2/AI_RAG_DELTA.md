# SMART AO — Delta IA et RAG v2

**24 septembre 2026 · proposition T0**

## Existant vérifié

`backend/app/modules/knowledge/domain/retrieval.py` impose tenant, Affaire, version DCE et classification sur les fragments. `application/retrieval.py` exclut `FINANCIAL_PRIVATE` de l'index mémoire et refuse certaines requêtes financières hors scope. Le chemin OCR/Docling/RAG reste qualifié localement et runtime désactivé selon les verdicts Phase 11 ; aucun moteur juridique v2 n'est démontré.

## Frontière proposée

| Usage | IA admise | Autorité finale |
|---|---|---|
| Extrait CCAP, formule ou date | Détection et proposition avec locator/hash/version | Validation humaine puis calcul déterministe ; ambiguïté → `REVIEW_REQUIRED`. |
| Applicabilité réglementaire | Recherche de texte et faits candidats | Règle datée et faits validés, avec revue spécialisée si nécessaire. |
| Assurance/HSE | Repérage d'obligations, rapprochement candidat | Courtier/QSE/Patron selon la décision ; aucune conclusion `COVERED` issue du LLM. |
| Délais, sanctions, prix/révision, cash | Paramètres candidats | Calculateur déterministe versionné ; aucun chiffre critique dérivé d'une phrase non qualifiée. |
| Carte/P7 | Résumé d'éléments déjà autorisés | Projection serveur des faits et états ; pas de nouveaux droits ni de disparition d'inconnus. |

## Écarts et tests

Le contrôle actuel par mots-clés financiers est une défense supplémentaire, **pas une preuve générale contre les inférences indirectes**. Avant toute extension RAG v2 : filtrage de rôle/classification avant sélection et agrégation, corpus non financier approuvé, refus tenant/role, injection dans CCAP, règle ancienne/future, panne source, citation de locator et nettoyage d'index temporaire. Aucune indexation persistante nouvelle n'est autorisée par ce dossier.
