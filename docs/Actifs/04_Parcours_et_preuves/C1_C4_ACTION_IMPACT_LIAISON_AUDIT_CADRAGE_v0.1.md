# C1/C4 — liaison entre action Patron et impact C3

**Date :** 3 octobre 2026<br>
**Statut :** C4 implémenté et vérifié localement ; aucun commit/push
**Base auditée :** HEAD `9c2a982` + WIP local C2/C3/C4 non commités
**Autorités :** Product Freeze PF31-03/04, Master métier M31-05 étapes 4–5, Cahier technique CT31-04/07

## AS-IS vérifié

- `CaseContractChangeActionRecord` est un acte C1 append-only, tenant/Affaire/event-scoped. Il référence une `applicability_id` C1, un résumé d’action, des références de preuve, une date déclarée ou un motif d’absence, et l’acteur/révision.
- `RecordCaseContractChangeActionCommand` accepte une action uniquement si la revue d’applicabilité référencée est `APPLICABLE_TO_HANDOVER` et encore la plus récente. Le rejeu et `expected_revision` sont contrôlés.
- La projection déclare l’état C1 `RECORDED`. Elle n’expose ni exécution terminée ni réception externe. Les `evidence_refs` sont les références fournies avec l’action ; elles ne prouvent pas, à elles seules, que l’action a été exécutée.
- C3 est un acte append-only distinct, identifié par `declaration_id`, qui référence l’événement, une liaison C2 exacte et une source A1/axe ; la lecture dérive `CURRENT`/`REVIEW_REQUIRED` sans réécrire l’acte.
- Aucun champ, commande, FK ou endpoint existant ne relie un Action C1 à un C3. Le lien commun à l’événement C1 ne dit pas quel impact une action traite.

## Arbitrage

La commande C1 Action et l’acte C3 doivent rester séparés. Un champ `impact_declaration_id` nullable sur l’action ne permettrait pas de relier après coup les actions déjà enregistrées sans UPDATE ; stocker l’ID dans `action_summary` ou les `evidence_refs` ne fournirait ni intégrité, ni historique de relation, ni projection fiable. Créer automatiquement une action depuis un impact fusionnerait déclaration et décision humaine.

**Décision de tranche :** créer un acte C4 append-only distinct qui relie, sur une même Affaire et un même événement, un `action_id` C1 exact à zéro ou plusieurs `declaration_id` C3 exacts. La relation ne modifie ni l’action ni l’impact C3.

## Contrat C4 minimal

Un acte de révision par action contient :

- `action_id`, `event_id`, `expected_revision`, `command_id`, `idempotency_key` et corrélation ;
- état fermé `LINKED`, `UNKNOWN` ou `NOT_APPLICABLE` ;
- pour `LINKED`, une liste bornée et sans doublon d’IDs C3 ; les deux autres états n’acceptent aucune sélection ;
- une justification et, pour `UNKNOWN`/`NOT_APPLICABLE`, un motif explicite ; acteur et date serveur.

Le serveur contrôle tenant/Affaire, que l’action appartient à l’événement, que l’action est encore autorisée par la dernière revue C1 `APPLICABLE_TO_HANDOVER`, et que chaque C3 appartient au même événement/Affaire et conserve `linkage_state=CURRENT`. Une action peut être liée à un C3 dont l’impact est `UNKNOWN` : cela indique que l’action humaine vise justement cet inconnu, sans affirmer que l’impact est établi.

La projection restitue chaque révision C4 séparément. Si la revue C1 de l’action devient obsolète ou si l’un des C3 liés passe à `REVIEW_REQUIRED`, l’ancien acte C4 reste lisible et sa projection signale `REVIEW_REQUIRED`. Une nouvelle relation exige un nouvel acte. `LINKED` signifie **relation déclarée par le Patron** ; l’action C1 demeure `RECORDED`, jamais « exécutée » ou « terminée » par C4.

La persistance recommandée est un acte C4 parent et une table enfant de relations vers les actes C3. Des FK composites relient l’acte parent à l’action C1 exacte et à l’événement, puis chaque relation enfant à un C3 exact du même tenant/Affaire/événement. Une garde transactionnelle PostgreSQL vérifie aussi que la revue C1 et la liaison C2/C3 sont encore courantes à l’insertion. Les relations enfant sont append-only ; cela évite de traiter une liste JSON d’IDs comme une intégrité référentielle. Aucune action, tâche, date ou notification n’est créée automatiquement.

## Points d’insertion

- Nouvel acte relationnel dans `pricing`, qui possède déjà les actes C1/C2/C3 ; aucune nouvelle couche « Contract Control ».
- Nouvelle migration additive et triggers append-only propres à C4 ; pas de colonne ajoutée ou modifiée dans `case_contract_change_actions` ni dans la table C3.
- Commande via `CaseContractChangeService.record`, politique Patron `FINANCIAL_PRIVATE`, endpoint sous le routeur Patron C1, lecture dans la projection d’événement et le `CaseContractChangePanel`.
- Le bouton C4 n’existe qu’après relecture serveur d’une action C1 et d’un C3 `CURRENT`. Une interruption conserve la même intention, et la confirmation n’apparaît qu’après la projection serveur.

## Garanties attendues

| Garantie | Test attendu |
|---|---|
| Une même Affaire : C2→C3→Action C1→C4 lié | E2E HTTP/PostgreSQL ; IDs C1 et C3 exacts retrouvés séparément |
| États relationnels | `LINKED` avec 1..N C3, `UNKNOWN` motivé, `NOT_APPLICABLE` motivé ; aucun faux état d’exécution |
| Refus d’intégrité | action d’un autre event/Affaire/tenant, C3 étranger, C3 `REVIEW_REQUIRED`, action sur revue C1 dépassée |
| Sécurité | Collaborateur refusé ; Patron soumis à la politique existante `FINANCIAL_PRIVATE` |
| Rejeu et concurrence | même commande/idempotency key sans doublon ; stale `expected_revision` refusé |
| Historique | UPDATE/DELETE refusés ; révision C4 conserve les relations antérieures, les actes C1/C3 ne changent pas |
| Obsolescence après C4 | nouvelle revue C1 ou C2/C3 : ancienne relation projetée `REVIEW_REQUIRED`, aucune réécriture ni relance |
| UI | historique de liens C4 distinct des actions C1 et déclarations C3 ; confirmation après relecture serveur |

## Implémentation et preuves locales

- Migration `20261003_0128` : un acte C4 parent append-only par action/révision et une table enfant normalisée, avec FK composites tenant/Affaire/événement vers l’action C1 et les actes C3 exacts. Les triggers exigent à l’écriture une revue C1 applicable et courante, un C2 `LINKED` courant pour chaque C3 et un nombre d’enfants cohérent avec `LINKED`/`UNKNOWN`/`NOT_APPLICABLE`.
- Commande Patron sous la politique existante `FINANCIAL_PRIVATE`, route `POST .../actions/{action_id}/impact-links`, idempotence via le dispatcher et `expected_revision` sérialisé par le verrou d’Affaire. La lecture expose l’historique et calcule `REVIEW_REQUIRED` après une revue C1 ou liaison C2 dépassée sans réécrire l’acte.
- `CaseContractChangePanel` conserve les actes C1, C3 et C4 séparés ; le Patron sélectionne les C3 exacts, et confirme seulement après la relecture serveur. L’action demeure `RECORDED` dans l’API et l’interface.

| Preuve exécutée | Résultat | Limite |
|---|---|---|
| E2E `backend/tests/db/test_case_handover_http_e2e.py::test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action` sur PostgreSQL, HTTP réel local, upgrade/downgrade | **1/1** ; `LINKED` vers deux C3 exacts, dont un impact C3 `UNKNOWN`, `UNKNOWN`, `NOT_APPLICABLE`, rejeu, conflit de révision, C1/C2 obsolète, Collaborateur, tenant étranger, projection, UPDATE/DELETE refusés ; l’action C1 reste `RECORDED` | Pas de navigateur CUA ni de test de concurrence multi-processus ; test complet local par `pytest` |
| Frontend ciblé `CaseContractChangePanel.test.tsx` | **4/4** ; sélection d’un C3 `UNKNOWN`, payload exact et affichage `RECORDED` | Test composant, sans navigateur réel |
| Suite backend complète PostgreSQL | **2013/2013** sur l’implémentation C4 avant l’ajout final de l’index tenant à la migration 0128 | Local uniquement ; après cet index, E2E C4 1/1 et architecture/schema/ops 38/38 ont été rejoués |
| Suite frontend complète | **299/299** ; typecheck, lint et build verts | Avertissement Vite sur le bundle principal de 575 kB |
| Architecture/schema/ops ciblés, Ruff et mypy | **38/38** ; Ruff et mypy ciblés verts | Ruff global du dépôt non rejoué |

La build émet aussi la dépréciation Starlette/httpx observée avant C4. Ces avertissements ne sont pas des échecs de la tranche.

## Limites et suite

C4 ne clôture pas une action, ne prouve pas sa réalisation, ne calcule pas d’échéance ni ne conclut à un droit préservé. La preuve d’exécution d’une action reste un futur acte distinct après la liaison C4. Les invariants C1/C3, le NO-GO public et la distinction entre déclaration et exécution restent inchangés.

**Suite cadrée :** [C1/C5 — preuve humaine d’exécution d’une action reliée par C4](C1_C5_PREUVE_EXECUTION_ACTION_AUDIT_CADRAGE_v0.1.md). C5 est un acte distinct proposé ; il n’est pas encore implémenté. Le NO-GO public reste maintenu.
