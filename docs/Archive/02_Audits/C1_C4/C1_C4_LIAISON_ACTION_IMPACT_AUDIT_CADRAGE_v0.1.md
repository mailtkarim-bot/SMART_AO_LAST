# C1/C4 — relier une action humaine aux impacts C3

> **Copie de travail remplacée pour le suivi actif.** L’audit consolidé, l’implémentation et les preuves C4 sont maintenus dans [C1_C4_ACTION_IMPACT_LIAISON_AUDIT_CADRAGE_v0.1.md](../../../Actifs/04_Parcours_et_preuves/C1_C4_ACTION_IMPACT_LIAISON_AUDIT_CADRAGE_v0.1.md). Ce fichier conserve les notes initiales et ne fait pas autorité sur l’état actuel.

**Date :** 3 octobre 2026<br>
**Statut :** notes d’audit initiales conservées ; se reporter au dossier canonique pour l’état actuel<br>
**Base auditée :** HEAD `9c2a982` + WIP C2/C3 local non commité<br>
**Autorités :** Product Freeze PF31-03/04, Master métier M31-05 étapes 4–5, Cahier technique CT31-04/07

## AS-IS vérifié

- `CaseContractChangeActionRecord` est un acte C1 append-only tenant/Affaire-scoped. Il référence l’événement C1 et la revue d’applicabilité courante qui a autorisé l’action ; il conserve un résumé, des `evidence_refs`, une date déclarée ou son motif d’absence, l’acteur et la révision.
- La commande C1 refuse l’action sans revue `APPLICABLE_TO_HANDOVER`, refuse une revue dépassée, sérialise les écritures par Affaire et rend les retries idempotents.
- La projection C1 restitue l’action comme `RECORDED`. Aucun état « exécutée/terminée » n’est défini ; les références saisies ne prouvent ni exécution ni réception externe.
- C3 conserve maintenant un acte distinct par source A1 et axe, relié à une révision C2 exacte. Chaque projection C3 expose son `linkage_id` et `linkage_state` (`CURRENT` ou `REVIEW_REQUIRED`). C1 Action ne stocke aucun identifiant C3.
- Aucun endpoint, modèle ou composant actuel ne relie un acte C1 Action à un acte C3 précis.

## Risques

- Ajouter un champ nullable `impact_declaration_id` à l’acte Action ne relierait que les actions futures et obligerait à modifier les actions déjà enregistrées pour les raccorder : interdit par l’append-only.
- Copier l’identifiant C3 dans `action_summary` ou `evidence_refs` ne donne ni FK, ni vérification tenant/Affaire, ni état de liaison projetable.
- Fusionner l’action avec C3 ferait perdre la séparation entre conséquence déclarée, intention de suivi et preuve/exécution.
- Afficher l’état C1 `RECORDED` comme action terminée transformerait une intention en succès sans preuve.
- Relier une action à une C3 dont la C2 est devenue obsolète masquerait qu’un Patron doit requalifier le lien.

## Contrat minimal retenu pour C4

Ajouter un **acte de relation append-only distinct** entre un `CaseContractChangeActionRecord` C1 et un ou plusieurs `CaseContractChangeImpactDeclarationRecord` C3 exacts. Le premier geste est un seul lien action↔C3 ; le contrat autorise une petite liste d’IDs C3 si la même action traite explicitement plusieurs impacts.

L’acte C4 porte : event/action exacts, liste d’IDs C3 ou état sans liaison, état `LINKED` / `UNKNOWN` / `NOT_APPLICABLE`, justification, acteur/date, `expected_revision`, `command_id` et `idempotency_key`. `LINKED` exige des actes C3 du même événement, de la même Affaire et du même tenant, tous issus de C2 `CURRENT`. `UNKNOWN` et `NOT_APPLICABLE` interdisent une liste de C3 et exigent chacun leur motif distinct. Une correction est une nouvelle révision ; un rejeu ne produit pas de seconde révision.

Avant écriture, le serveur exige que l’action C1 existe et soit encore liée à la dernière revue `APPLICABLE_TO_HANDOVER`. Si sa revue est dépassée, l’action C1 ne peut pas être présentée comme courante pour C4. Un nouvel acte C1 de revue reste une décision séparée ; il ne réactive ni ne modifie l’ancienne action.

Après écriture, l’action demeure `RECORDED` et C3 demeure inchangé. C4 signifie uniquement « le Patron relie cette action à ces déclarations d’impact », jamais « l’action est exécutée ». Une nouvelle revue C1 ou une nouvelle C2/C3 laisse les anciens C4 intacts et expose `REVIEW_REQUIRED` dans la projection ; aucune tâche, échéance ni notification n’est déclenchée automatiquement.

## Points d’insertion

- Nouvel aggregate relationnel dans le bounded context `pricing` déjà propriétaire de C1/C2/C3 ; aucun changement de colonnes sur l’action ou les actes C3 existants.
- Persistance tenant/Affaire-scoped avec FK composite vers le C1 `event_id` + `action_id` et vers chaque ID C3 exact ; trigger UPDATE/DELETE append-only. Une table de relation peut représenter une ligne par acte C4 et liste C3 bornée, sans stocker de copie des notes ou valeurs des impacts.
- Commande et route Patron C1 sous `FINANCIAL_PRIVATE` ; lecture intégrée à l’action et à la chronologie C1/C3 dans `CaseContractChangePanel`.
- Le C4 n’exige pas une nouvelle catégorie d’action, de preuve, d’état d’exécution ou de workflow.

## Recette C4 minimale

| Garantie | Preuve à écrire |
|---|---|
| Même Affaire C1 Action→C3→C4 | HTTP → API → PostgreSQL → lecture C07/C12 ; les IDs exacts restent distincts |
| État humain | `LINKED` à un ou plusieurs C3 exacts ; `UNKNOWN` avec motif ; `NOT_APPLICABLE` avec motif différent |
| Refus | action ou C3 d’un autre événement/Affaire/tenant ; C3 non courant ; action dont la revue C1 est dépassée ; Collaborateur |
| Rejeu/concurrence | même IDs de commande/idempotence ; `expected_revision` obsolète refusé |
| Immutabilité | C4 UPDATE/DELETE refusés ; l’action C1, ses preuves, le C3 et A1/B1/C1 restent inchangés |
| Absence de faux succès | la liaison C4 ne change jamais C1 Action `RECORDED` en « exécutée » ; aucune tâche/échéance automatique |
| Obsolescence après coup | C3/C2 ou la revue C1 est ensuite révisée ; l’ancien C4 reste visible avec `REVIEW_REQUIRED`, sans réécriture |
| UX | Patron relie volontairement action et déclaration(s) C3, voit les états inconnus et relit le résultat serveur avant confirmation |

## Limites et suite

C4 n’apporte pas encore un cycle d’exécution d’action, une réception de preuve d’exécution, une échéance calculée ou une conclusion juridique/financière. Ces besoins restent séparés et à auditer après C4. Cette décision de tranche ne promeut pas l’orientation produit, les cahiers intégraux ou le NO-GO public.

**Statut de cette recommandation :** remplacée par l’implémentation C4 et les preuves consignées dans le dossier canonique.
