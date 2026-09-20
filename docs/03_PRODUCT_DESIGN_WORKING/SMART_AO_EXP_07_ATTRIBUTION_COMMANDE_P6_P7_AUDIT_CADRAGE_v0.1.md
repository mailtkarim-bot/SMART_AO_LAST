# SMART AO — EXP-07 : attribution, commande, P6 et P7

**Statut :** preuve commande, contrôle P6 et résultat P7 implémentée ; REX et gel restent à faire

## Séparation obligatoire

| Fait | Sens | Peut produire le suivant ? |
|---|---|---|
| `WON` par lot | attribution déclarée et sourcée | oui, proposition de commande |
| commande | engagement contractuel accepté | oui, préparation P6 |
| P6 | contrôle/validation avant exécution | oui, passage en exécution |
| P7 | résultat d’exécution ou clôture opérationnelle | capitalisation et rétention |

`WON` ne signifie donc ni commande, ni P6, ni P7. `LOST` et `UNKNOWN` ne produisent aucun engagement. Les réserves sont transportées sans être effacées ni converties en approbation.

## Contrat minimal suivant

La preuve en cours ajoute des actes append-only distincts, chacun avec lot, auteur, horodatage, révision et idempotence :

1. accepter ou refuser une commande issue d’un `WON` ;
2. enregistrer le contrôle P6 avec ses réserves ouvertes ;
3. enregistrer le résultat P7, y compris `UNKNOWN` ou interruption.

Aucun changement direct de `CaseRecord.commercial_stage` ne remplacera ces faits. La projection de stage sera dérivée seulement lorsque les preuves nécessaires existent.

## Refus

- commande depuis `LOST` ou `UNKNOWN` : refus ;
- commande sans attribution `WON` correspondante : refus ;
- P6 sans commande acceptée : refus ;
- P7 sans P6 : refus ;
- résultat inconnu : conservé comme `UNKNOWN`, jamais comme succès ;
- rejeu : même acte selon `command_id`/`idempotency_key`, sans doublon.

**Prochaine étape :** produire le retour d’expérience P7 avec motif connu ou inconnu, puis préparer le gel EXP-07.

## Preuve exécutée de la commande et du P6

La tranche est maintenant codée dans le backend : `RecordCaseOrderCommand` crée un fait `CaseOrderRecord` uniquement lorsqu’un résultat `WON` existe dans le même tenant et que son lot appartient au périmètre de l’Affaire. La décision `ACCEPTED` ou `REJECTED`, la source, les réserves et la justification sont conservées sans mutation de l’attribution. Le rejeu des mêmes identifiants de commande est servi par le reçu durable du dispatcher sans nouvel acte.

`RecordCaseP6ControlCommand` crée un fait `CaseP6ControlRecord` uniquement pour une commande `ACCEPTED`. Le contrôle conserve sa décision et ses réserves ; une commande refusée, un résultat `LOST`/`UNKNOWN`, un autre tenant ou un lot hors périmètre ne produisent aucun engagement. Les deux actes émettent leur événement append-only et disposent de routes Patron sous `/api/v1/patron/case-orders`.

La migration `20260919_0079` crée les commandes et complète les timestamps manquants des tables de résultat existantes ; `20260919_0080` crée les contrôles P6. La preuve PostgreSQL `backend/tests/application/test_case_order_p6.py` vérifie la création, le rejeu sans doublon et les refus `ONLY_WON_OUTCOMES_ORDERABLE` et `ORDER_NOT_ACCEPTED` : 2 tests passent sur le service PostgreSQL isolé du projet.

La limite reste volontaire : aucun stage commercial n’est avancé automatiquement. Le résultat P7 est conservé comme fait séparé, y compris `UNKNOWN` et `INTERRUPTED`; la prochaine tranche porte sur le retour d’expérience, la capitalisation et les règles de rétention avant le gel EXP-07.

## Preuve exécutée du résultat P7

`RecordCaseP7ResultCommand` exige un contrôle P6 `APPROVED` et conserve un résultat `COMPLETED`, `UNKNOWN` ou `INTERRUPTED` dans `case_p7_results`. Un résultat `COMPLETED` exige une source ; les états `UNKNOWN` et `INTERRUPTED` exigent un motif. Les réserves restent visibles et le rejeu des mêmes identifiants ne crée aucun second résultat. La route Patron est `/api/v1/patron/case-p6/{p6_control_id}/p7`.

La migration `20260919_0081` ajoute la table append-only et devient la tête Alembic. Le test PostgreSQL `backend/tests/application/test_case_order_p6.py` vérifie la chaîne WON → commande ACCEPTED → P6 APPROVED → P7 UNKNOWN, son rejeu et les refus précédents ; avec le contrôle de tête, 3 tests passent. Aucun stage courant n’est modifié et aucune clôture réussie n’est présumée depuis `UNKNOWN`.
