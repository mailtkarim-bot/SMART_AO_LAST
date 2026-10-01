# T3 — Cycle de vie de la revue contractuelle locale

**Statut :** préparation active — NO-GO public maintenu

## Objectif

Rendre explicite le cycle de vie d'une revue humaine d'une preuve contractuelle
sans modifier rétroactivement la preuve ni produire d'avis juridique.

## Périmètre de la prochaine tranche

1. conserver chaque acte de revue en append-only ;
2. relier chaque acte à une révision précise de la preuve ;
3. exposer le dernier acte confirmé comme projection, sans supprimer l'historique ;
4. refuser une revue d'une preuve étrangère, absente ou d'une révision inconnue ;
5. conserver `NEEDS_CLARIFICATION` et `REJECTED` comme états réels ;
6. rendre visible la source et la justification dans C07.

## Critères d'acceptation

- deux actes sur la même preuve restent tous deux consultables ;
- un rejeu idempotent ne crée pas de second acte ;
- une nouvelle révision exige un nouvel acte ;
- aucun acte ne change `baseline`, `dérogation` ou `impact` ;
- le dernier état projeté est déterministe par révision et date d'enregistrement ;
- aucun calcul juridique, financier, assurantiel ou HSE n'est déclenché.

## Hors périmètre

Pas de validation externe, de signature électronique, de moteur de conformité,
de scoring automatique, de pilote client ni d'ouverture publique.

## Preuves attendues

Migration/tests PostgreSQL, tests de rejeu et de tenant, projection Patron C07,
tests frontend, puis revue propriétaire locale.

